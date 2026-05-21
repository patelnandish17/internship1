import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

async def test_llms():
    print("--- API KEY STATUS CHECK ---")
    
    # 1. SambaNova
    try:
        print("1. Testing SambaNova...")
        llm_samba = ChatOpenAI(
            model="Meta-Llama-3.3-70B-Instruct",
            api_key=os.getenv("SAMBANOVA_API_KEY"),
            base_url="https://api.sambanova.ai/v1",
            max_tokens=50
        )
        res = await llm_samba.ainvoke([HumanMessage(content="Say OK")])
        print("SambaNova: \033[92mWORKING\033[0m")
    except Exception as e:
        print(f"SambaNova: \033[91mEXHAUSTED / ERROR\033[0m - {str(e)[:200]}")
        
    # 2. Groq
    try:
        print("2. Testing Groq...")
        llm_groq = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_tokens=50)
        res = await llm_groq.ainvoke([HumanMessage(content="Say OK")])
        print("Groq: \033[92mWORKING\033[0m")
    except Exception as e:
        print(f"Groq: \033[91mEXHAUSTED / ERROR\033[0m - {str(e)[:200]}")
        
    # 3. Gemini
    try:
        print("3. Testing Gemini...")
        llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_tokens=50)
        res = await llm_gemini.ainvoke([HumanMessage(content="Say OK")])
        print("Gemini: \033[92mWORKING\033[0m")
    except Exception as e:
        print(f"Gemini: \033[91mEXHAUSTED / ERROR\033[0m - {str(e)[:200]}")

asyncio.run(test_llms())
