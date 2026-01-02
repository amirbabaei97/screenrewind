from rapidocr_onnxruntime import RapidOCR
import logging

# Initialize RapidOCR engine
# We initialize it once to avoid reloading models on every call
ocr_engine = RapidOCR()

def extract_text(image_path: str) -> str:
    """
    Extracts text from an image using RapidOCR.
    Returns the concatenated text.
    """
    try:
        result, _ = ocr_engine(image_path)
        
        if not result:
            return ""

        # result is a list of items, where each item is [coordinates, text, confidence]
        # We just want the text.
        extracted_text = " ".join([item[1] for item in result])
        return extracted_text
    except Exception as e:
        logging.error(f"Error during OCR processing: {e}")
        return ""
