import os

# You should really use a tool like python-dotenv to manage these
# But for this project, we'll use environment variables directly.
# A long, random string is recommended for the secret key.
SECRET_KEY = os.environ.get("SECRET_KEY", "a-super-secret-key-that-should-be-changed")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
