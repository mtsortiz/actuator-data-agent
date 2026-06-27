import uuid
from fastapi import APIRouter, HTTPException
from api.schemas import ChatRequest, ChatResponse


router = APIRouter()

@router.post("/api/conversation", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    current_thread_id = payload.thread_id or str(uuid.uuid4())

    try:
        #TODO: Connect the graph
        #result = await agent_graph.ainvoke({"messages": [payload.message]}, config={"configurable":{"thread_id": current_thread_id}})

        #MOCK DE PRUEBA
        user_message = payload.message.lower()
        if "762" in user_message:
            mock_reply = "The actuator 762 serie operates with 40 watts motor power"
            mock_sources = ["Table: actuators"]
        else:
            mock_reply = f"Hi, I received your message: '{payload.message}'. But I have not the graph connected yet"
            mock_sources = ["Database: connected"]

            return ChatResponse(response=mock_reply, thread_id=current_thread_id, sources=mock_sources)
    except Exception as e:
        print(f"Error processing the request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")