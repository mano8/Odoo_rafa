"""
Utility functions for handling file paths in the auth_user_service.
"""
# auth_user_service/utils/paths.py
from pathlib import Path
from os.path import join as join_path

ROOT_DIR = Path(__file__).resolve()


def find_dotenv(start_path: Path = ROOT_DIR) -> Path:
    """Find the .env file in the directory tree starting from start_path."""
    print(f"Looking for .env file starting from: {start_path}")
    for parent in [start_path] + list(start_path.parents):
        print(f"Checking parent directory: {parent}")
        potential = parent / '.env'
        if potential.exists():
            return join_path(parent, '.env')
    raise FileNotFoundError(f".env file not found from {start_path}")
