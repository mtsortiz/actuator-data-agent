import uuid
from fastapi import APIRouter, HTTPException
from api.schemas.schemas import ChatRequest, ChatResponse
from agent.agent import agent


router = APIRouter()

@router.post("/api/conversation", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    current_thread_id = payload.thread_id or str(uuid.uuid4())

    try:
        config={"configurable":{"thread_id": current_thread_id}}
        result= await agent.ainvoke({"messages": [{"role": "user", "content": payload.query}]}, config=config)

        last_message = result["messages"][-1].content
        sources=[]

        for msg in reversed(result["messages"]):
            if msg.type == "ai" and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    sources.append(f"Tool: {tool_call['name']}")
                break

        if not sources:
            sources.append("No tools were used in this conversation.")

        return ChatResponse(
            thread_id=current_thread_id,
            answer=last_message,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

