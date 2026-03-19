from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str = ""
    message: str


@app.post("/contact")
async def submit_contact(form: ContactForm):
    return {"success": True, "message": "Message received!"}
