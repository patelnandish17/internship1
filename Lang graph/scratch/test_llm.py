import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

async def test_llm():
    try:
        llm = ChatOpenAI(
            model="Meta-Llama-3.3-70B-Instruct",
            api_key=os.getenv("SAMBANOVA_API_KEY"),
            base_url="https://api.sambanova.ai/v1",
            max_tokens=3072,
            temperature=0.1
        )
        response = await llm.ainvoke([
            SystemMessage(content="You always respond in valid JSON format only."), 
            HumanMessage(content="Return {\"status\": \"success\"}")
        ])
        print("Success:", response.content)
    except Exception as e:
        print("Error:", str(e))

asyncio.run(test_llm())
