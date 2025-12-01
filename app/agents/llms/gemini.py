import os
import dotenv

from langchain_google_genai import ChatGoogleGenerativeAI


dotenv.load_dotenv()
def get_gemini_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite"), 
        api_key=os.environ["GOOGLE_API_KEY"]
    )