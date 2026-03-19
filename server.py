import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
DB_PATH = "contacts.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

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
    # Save to SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO contacts (name, email, subject, message) VALUES (?, ?, ?, ?)",
            (form.name, form.email, form.subject, form.message),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Send email via SendGrid
    if SENDGRID_API_KEY and FROM_EMAIL and TO_EMAIL:
        try:
            email_body = f"""
New contact form submission from your portfolio:

Name:    {form.name}
Email:   {form.email}
Subject: {form.subject or '(none)'}

Message:
{form.message}

---
Submitted at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=TO_EMAIL,
                subject=f"Portfolio Contact: {form.subject or 'New message from ' + form.name}",
                plain_text_content=email_body,
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            # Log but don't fail the request — message is already saved to DB
            print(f"SendGrid error: {e}")

    return {"success": True, "message": "Message received!"}


# Serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse("index.html")


# Serve other static assets if needed
app.mount("/", StaticFiles(directory="."), name="static")
