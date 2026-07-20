from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from tools import analyze_image_with_query

load_dotenv()

system_prompt = """
You are a witty and helpful AI voice assistant. 
Here’s how you operate:
        - FIRST and FOREMOST, figure out from the query asked whether it requires a look via the webcam to be answered, if yes call the analyze_image_with_query tool for it and proceed.
        - Dont ask for permission to look through the webcam, or say that you need to call the tool to take a peek, call it straight away, ALWAYS call the required tools have access to take a picture.
        - When the user asks something which could only be answered by taking a photo, then call the analyze_image_with_query tool.
        - Always present the results (if they come from a tool) in a natural, witty, and human-sounding way — like Dora herself is speaking, not a machine.
    Your job is to make every interaction feel smart, snappy, and personable. Got it? Let’s charm your master!"
"""

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)


def ask_agent(user_query: str) -> str:
    agent = create_react_agent(
        model=llm,
        tools=[analyze_image_with_query],
        prompt=system_prompt,
        version='v1'
        )

    input_messages = {"messages": [{"role": "user", "content": user_query}]}

    response = agent.invoke(input_messages)

    # LangGraph can return tool-call/tool-result messages after assistant turns.
    # Prefer the latest assistant text message to avoid leaking raw function-call text.
    for msg in reversed(response["messages"]):
        if getattr(msg, "type", None) == "ai" and getattr(msg, "content", None):
            return msg.content if isinstance(msg.content, str) else str(msg.content)

    return "I had trouble generating a response just now. Please try again."