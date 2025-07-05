#!/usr/bin/env python3
"""
Script to create a test PDF file for testing the summarization service
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_test_pdf():
    """Create a simple test PDF with sample content"""
    
    # Create tests directory if it doesn't exist
    os.makedirs("tests", exist_ok=True)
    
    # Create the PDF
    pdf_path = "tests/sample_document.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Content for the PDF
    content = []
    
    # Title
    content.append(Paragraph("Test Document for PDF Summarization", title_style))
    content.append(Spacer(1, 0.5*inch))
    
    # Introduction
    content.append(Paragraph("Introduction", heading_style))
    content.append(Paragraph(
        "This is a test document created specifically for testing the PDF summarization service. "
        "The document contains multiple sections with different types of content to verify "
        "that the text extraction and summarization process works correctly.",
        normal_style
    ))
    content.append(Spacer(1, 0.25*inch))
    
    # Main Content
    content.append(Paragraph("Main Content", heading_style))
    content.append(Paragraph(
        "The PDF summarization service is designed to accept PDF documents via a secure API endpoint, "
        "extract text content using PyMuPDF, and generate intelligent summaries using OpenAI's GPT-4 model. "
        "The service then forwards these summaries to an external API endpoint for further processing.",
        normal_style
    ))
    content.append(Spacer(1, 0.25*inch))
    
    content.append(Paragraph(
        "Key features of the service include: Bearer token authentication for security, "
        "comprehensive error handling for robust operation, logging capabilities for monitoring, "
        "and support for various PDF formats and structures.",
        normal_style
    ))
    content.append(Spacer(1, 0.25*inch))
    
    # Technical Details
    content.append(Paragraph("Technical Implementation", heading_style))
    content.append(Paragraph(
        "The service is built using FastAPI framework, which provides automatic API documentation "
        "and high performance. PDF text extraction is handled by PyMuPDF (fitz), which is reliable "
        "and efficient for processing various PDF formats. The OpenAI integration uses the latest "
        "API client to communicate with GPT-4 for generating high-quality summaries.",
        normal_style
    ))
    content.append(Spacer(1, 0.25*inch))
    
    # Conclusion
    content.append(Paragraph("Conclusion", heading_style))
    content.append(Paragraph(
        "This test document demonstrates the typical structure and content that the PDF summarization "
        "service should be able to process effectively. The service should extract all this text "
        "and generate a concise summary highlighting the key points about the PDF summarization API.",
        normal_style
    ))
    
    # Build the PDF
    doc.build(content)
    
    print(f"Test PDF created: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    create_test_pdf()