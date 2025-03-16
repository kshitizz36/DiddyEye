import os
from dotenv import load_dotenv

# 1) Load the .env file into environment variables
load_dotenv()  # By default, load_dotenv() looks for a .env file in the current or parent directories

# 2) Get the OPENAI_API_KEY from the environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# You can load other env vars similarly:
# OTHER_API_KEY = os.getenv("OTHER_API_KEY")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
