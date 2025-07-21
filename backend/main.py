from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .utils.neo4j_driver import close_neo4j_driver
from .routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("shutdown")
async def shutdown_event():
    close_neo4j_driver()