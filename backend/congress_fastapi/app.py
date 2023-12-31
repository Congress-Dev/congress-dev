from fastapi import FastAPI
from congress_fastapi.routes.members import router as members_router

app = FastAPI()
app.include_router(members_router)
print("Loaded")