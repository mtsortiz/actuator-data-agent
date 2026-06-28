from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.router import router

app = FastAPI(title="Actuator Data Agent API", description="API for interacting with the Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, limitar a los dominios del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)