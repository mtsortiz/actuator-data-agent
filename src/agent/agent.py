import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from src.agent.tools import tools
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0.0
)

memory = MemorySaver()

agent = create_agent(
    model=ChatOpenAI(
        model="gpt-5-mini",
        temperature=0.1,
    ),
    tools=tools,
    checkpointer=memory,
    system_prompt = """
You are the Konecto Intelligent Actuator Data Agent. Your job is to assist clients 
in finding and specifying the correct actuator models from the Series 76 catalog.
Rules for your execution:
1. You have tools to query the local SQLite database. Always use them when asked about specific technical data, parts, or specifications.
2. If the user asks about a specific part number, call `query_by_part_number`.
3. If the user provides physical requirements (voltage, phase, torque, speed, motor power), call `query_by_specs`.
4. Be polite, precise, and reply based on the technical specifications retrieved.
"""
)