import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# Get algorithm, default to HS256 if not set
ALGORITHM = os.getenv("ALGORITHM", "HS256")
