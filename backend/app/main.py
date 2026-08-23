import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .models import User
from .routes import users, documents, chat, opinions

# Build database tables automatically on startup
Base.metadata.create_all(bind=engine)

# Seed database users from users.json on startup
db = SessionLocal()
try:
    json_path = os.path.join(os.path.dirname(__file__), "users.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            users_list = json.load(f)
            for u in users_list:
                existing = db.query(User).filter(User.username == u["username"]).first()
                if not existing:
                    user = User(
                        username=u["username"],
                        password=u.get("password", ""),
                        role=u["role"]
                    )
                    db.add(user)
                else:
                    existing.password = u.get("password", "")
                    existing.role = u["role"]
            db.commit()
finally:
    db.close()

app = FastAPI(
    title="Enterprise Legal Intelligence Platform API",
    description="Isolated, secure backend servicing the Government Secretariat Law Department",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(opinions.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "online", "system": "Enterprise Legal Intelligence Platform v2"}