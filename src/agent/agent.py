from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools import tools


agent = create_agent(
    model=ChatOpenAI(
        model="gpt-5-mini",
        temperature=0.1,
    ),
    tools=tools,
    system_prompt = """
You are the Konecto Intelligent Actuator Data Agent. Your job is to assist clients 
in finding and specifying the correct actuator models from the Series 76 catalog.
You have tools to query the local SQLite database. Always use them when asked about specific technical data.
"""
)