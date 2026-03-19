from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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


@app.get("/")
async def serve_index():
    return FileResponse("index.html")


app.mount("/", StaticFiles(directory="."), name="static")
