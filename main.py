import os
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from openai import OpenAI
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Summarization API",
    description="API service to summarize PDF documents using OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
security = HTTPBearer()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL")
EXTERNAL_API_TOKEN = os.getenv("EXTERNAL_API_TOKEN")

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
if not AUTH_TOKEN:
    raise ValueError("AUTH_TOKEN environment variable is required")
if not EXTERNAL_API_URL:
    raise ValueError("EXTERNAL_API_URL environment variable is required")
if not EXTERNAL_API_TOKEN:
    raise ValueError("EXTERNAL_API_TOKEN environment variable is required")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token authentication"""
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token"
        )
    return credentials.credentials

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        
        for page in doc:
            text += page.get_text()
        
        doc.close()
        
        if not text.strip():
            raise ValueError("No text found in PDF")
        
        return text.strip()
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

async def summarize_text(text: str) -> str:
    """Summarize text using OpenAI GPT-4"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes documents concisely and accurately."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following document in English: {text}"
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Error summarizing text with OpenAI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize text: {str(e)}"
        )

async def forward_summary(summary: str, filename: str) -> bool:
    """Forward summary to external API endpoint"""
    try:
        payload = {
            "filename": filename,
            "summary": summary
        }
        
        headers = {
            "Authorization": f"Bearer {EXTERNAL_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                EXTERNAL_API_URL,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"External API returned status {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"External API error: {response.status_code}"
                )
            
            return True
    
    except httpx.TimeoutException:
        logger.error("Timeout while forwarding summary to external API")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Timeout while forwarding summary"
        )
    except Exception as e:
        logger.error(f"Error forwarding summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to forward summary: {str(e)}"
        )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PDF Summarization API is running"}

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """
    Upload a PDF file for summarization.
    
    - Accepts PDF files via multipart/form-data
    - Requires Bearer token authentication
    - Returns success message after forwarding summary to external API
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        pdf_content = await file.read()
        
        if len(pdf_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
        
        logger.info(f"Processing PDF file: {file.filename}")
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_content)
        
        # Summarize text using OpenAI
        summary = await summarize_text(extracted_text)
        
        # Forward summary to external API
        await forward_summary(summary, file.filename)
        
        logger.info(f"Successfully processed and forwarded summary for: {file.filename}")
        
        return {
            "message": "PDF processed and summary forwarded successfully",
            "filename": file.filename,
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)