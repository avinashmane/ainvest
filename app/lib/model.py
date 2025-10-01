# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# will use the API key from environment variables

import os

def get_model(
        id=os.environ.get("MODEL", "gemini-2.0-flash-001")
        ):
    m_id=id.split("/").pop()

    if id.startswith("gemini"):
        from agno.models.google import Gemini

        return Gemini(id=m_id)
    else:

        from agno.models.ollama import Ollama

        return Ollama(id=m_id)

model= get_model()
