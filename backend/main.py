from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.neo4j_driver import close_neo4j_driver
import backend.routes as routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

@app.on_event("shutdown")
async def shutdown_event():
    close_neo4j_driver()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)