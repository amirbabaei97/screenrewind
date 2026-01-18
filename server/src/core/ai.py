import os
import json
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.models.project import Project, Task
import logging
import dotenv

dotenv.load_dotenv()


# initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini Client
# reading API key from environment variable .env file
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_context_from_db(db: Session):
    projects = db.query(Project).all()
    projects_list = []
    tasks_list = []
    
    for p in projects:
        projects_list.append(p.name)
        for t in p.tasks:
            tasks_list.append(f"{p.name}: {t.name}")
            
    return ", ".join(projects_list), ", ".join(tasks_list)

def analyze_snapshot(image_path: str, ocr_text: str) -> Dict[str, str]:
    """
    Analyzes a snapshot using Google Gemini 2.0 Flash to determine Project and Task.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not set. Skipping AI analysis.")
        return {
            "project": "Uncategorized",
            "task": "General",
            "explanation": "AI analysis disabled (missing API key)."
        }

    db = SessionLocal()
    try:
        projects_str, tasks_str = get_context_from_db(db)
        logger.info(f"list of projects: {projects_str}")
        logger.info(f"list of tasks: {tasks_str}")
    finally:
        db.close()

    prompt = f"""
You are an intelligent activity classifier for a time-tracking application.

**Input:**
1. A list of User Projects: {projects_str} 
2. and their active Tasks (with descriptions): {tasks_str}
3. Raw Data: The Screen OCR Text and the **Actual Screenshot Image**. 

!!! MOST IMPORTANT RULE: ONLY USE THE PROJECTS AND TASKS PROVIDED IN THE LISTS ABOVE. DO NOT MAKE UP NEW ONES.!!!
IF NOTHING MATCHES, RETURN "Uncategorized" FOR PROJECT AND null FOR TASK.

**Goal:** Analyze the visual screenshot and text data to match the activity to the most relevant **Project** and **Task**, and provide a brief explanation.

**Rules:**
1. **Visual & Textual Analysis:** Combine visual cues from the screenshot (software layout, icons, websites, video players) with the OCR text to understand the context.
2. **Context Matching:** Use the project/task descriptions to disambiguate. (e.g., If the image shows VS Code with Python code, match to the coding project. If it shows a PDF with double-column text, match to "Literature Review").
3. **Generate Detailed Explanation:** Write a comprehensive explanation of the user's actions. Explain what is happening in this screenshot.
4. **Strict JSON:** Return ONLY valid JSON.
5. **Fallback:** If no task matches, return `null` for the task name but try to identify the Project. If nothing matches, use "Uncategorized".

**Output Schema:**
Return ONLY a raw JSON object. Do not use markdown code blocks.
{{
  "project": "Project Name",
  "task": "Task Name or null",
  "explanation": "Reasoning..."
}}
"""

    try:
        # Load image
        # The google-genai library handles file uploads or inline data.
        # For local files, we might need to read bytes or upload.
        # Checking documentation for google-genai (v0.1.0+ usually supports direct file or bytes)
        # Assuming we can pass the file path or bytes.
        
        # For the 'google-genai' SDK (not google-generativeai), the usage is slightly different.
        # Based on recent SDKs, we often upload the file first or pass bytes.
        
        # Let's try reading the file as bytes.
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Log the full prompt for debugging
        logger.info(f"--- GEMINI PROMPT PREVIEW ---\n{prompt}\n-----------------------------")
        
        # Use a model that supports JSON mode (e.g., gemini-2.0-flash-exp, gemini-1.5-flash)
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/png") # Assuming PNG, but could be JPEG
            ]
        )
        
        # Parse the response
        if response.text:
            text = response.text.strip()
            logger.info(f"--- GEMINI RAW RESPONSE ---\n{text}\n---------------------------")

            # Handle markdown code blocks if the model ignores the "no markdown" instruction
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            try:
                return json.loads(text.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Gemini response: {e}")
                logger.error(f"Bad JSON content: {text}")
                return {
                    "project": "Uncategorized",
                    "task": "General",
                    "explanation": f"AI response was not valid JSON. Raw: {text[:100]}"
                }
        else:
            return {
                "project": "Uncategorized",
                "task": "General",
                "explanation": "AI returned empty response."
            }

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {
            "project": "Uncategorized",
            "task": "General",
            "explanation": f"AI analysis failed: {str(e)}"
        }
