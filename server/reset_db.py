import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

# Set env var if not present (fallback)
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql://screenuser:screenuser123@localhost/screenrewind"

from src.core.database import engine, Base
# Import models to populate Base.metadata
from src.models.snapshot import Snapshot
from src.models.project import Project, Task
from src.models.rule import Rule

def reset():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")

if __name__ == "__main__":
    reset()
