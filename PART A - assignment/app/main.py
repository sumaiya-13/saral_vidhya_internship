from fastapi import FastAPI
from app.database import Base, engine
from app.routes import users, auth, materials

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PDF Learning API",
    description="JWT-authenticated PDF OCR, summarization and quiz generation API",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(materials.router)

@app.get("/")
def root():
    return {"message": "PDF Learning API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
