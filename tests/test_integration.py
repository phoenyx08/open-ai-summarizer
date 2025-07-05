import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
import fitz

# Import the FastAPI app
from main import app

class TestIntegrationAPI:
    """Integration tests for the PDF summarization API"""
    
    def setup_method(self):
        """Set up test environment"""
        self.client = TestClient(app)
        self.test_token = "test_bearer_token"
        
        # Set up test environment variables
        os.environ["AUTH_TOKEN"] = self.test_token
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        os.environ["EXTERNAL_API_URL"] = "http://localhost:8001/mock-api"
        os.environ["EXTERNAL_API_TOKEN"] = "test_external_token"
    
    def create_test_pdf(self) -> bytes:
        """Create a test PDF file in memory"""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "This is a test PDF document for integration testing.")
        page.insert_text((100, 150), "It contains sample content that should be extracted and summarized.")
        pdf_bytes = doc.write()
        doc.close()
        return pdf_bytes
    
    def test_root_endpoint(self):
        """Test the root health check endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "PDF Summarization API is running"}
    
    def test_upload_without_auth(self):
        """Test upload endpoint without authentication"""
        pdf_content = self.create_test_pdf()
        
        response = self.client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")}
        )
        assert response.status_code == 403
    
    def test_upload_with_invalid_auth(self):
        """Test upload endpoint with invalid authentication"""
        pdf_content = self.create_test_pdf()
        
        response = self.client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 403
    
    def test_upload_non_pdf_file(self):
        """Test upload endpoint with non-PDF file"""
        text_content = b"This is not a PDF file"
        
        response = self.client.post(
            "/upload",
            files={"file": ("test.txt", text_content, "text/plain")},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        assert response.status_code == 400
        assert "Only PDF files are supported" in response.json()["detail"]
    
    def test_upload_empty_file(self):
        """Test upload endpoint with empty file"""
        response = self.client.post(
            "/upload",
            files={"file": ("test.pdf", b"", "application/pdf")},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        assert response.status_code == 400
        assert "Empty file uploaded" in response.json()["detail"]
    
    @patch('main.openai_client.chat.completions.create')
    @patch('httpx.AsyncClient')
    def test_upload_success_flow(self, mock_http_client, mock_openai):
        """Test successful PDF upload and processing flow"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "This is a test summary of the PDF content."
        mock_openai.return_value = mock_response
        
        # Mock external API response
        mock_external_response = Mock()
        mock_external_response.status_code = 200
        mock_http_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_external_response
        )
        
        # Create test PDF
        pdf_content = self.create_test_pdf()
        
        # Make request
        response = self.client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "PDF processed and summary forwarded successfully"
        assert response_data["filename"] == "test.pdf"
        assert response_data["status"] == "success"
        
        # Verify OpenAI was called
        mock_openai.assert_called_once()
        
        # Verify external API was called
        mock_http_client.return_value.__aenter__.return_value.post.assert_called_once()
    
    @patch('main.openai_client.chat.completions.create')
    def test_upload_openai_error(self, mock_openai):
        """Test handling of OpenAI API errors"""
        # Mock OpenAI error
        mock_openai.side_effect = Exception("OpenAI API Error")
        
        # Create test PDF
        pdf_content = self.create_test_pdf()
        
        # Make request
        response = self.client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        
        # Verify error response
        assert response.status_code == 500
        assert "Failed to summarize text" in response.json()["detail"]
    
    @patch('main.openai_client.chat.completions.create')
    @patch('httpx.AsyncClient')
    def test_upload_external_api_error(self, mock_http_client, mock_openai):
        """Test handling of external API errors"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test summary"
        mock_openai.return_value = mock_response
        
        # Mock external API error
        mock_external_response = Mock()
        mock_external_response.status_code = 500
        mock_external_response.text = "Internal Server Error"
        mock_http_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_external_response
        )
        
        # Create test PDF
        pdf_content = self.create_test_pdf()
        
        # Make request
        response = self.client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        
        # Verify error response
        assert response.status_code == 500
        assert "Failed to forward summary" in response.json()["detail"]
    
    def test_upload_invalid_pdf(self):
        """Test upload with invalid PDF content"""
        invalid_pdf = b"This is not a valid PDF content"
        
        response = self.client.post(
            "/upload",
            files={"file": ("test.pdf", invalid_pdf, "application/pdf")},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        
        # Should get 500 error due to PDF processing failure
        assert response.status_code == 500
        assert "Failed to extract text from PDF" in response.json()["detail"]

class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def setup_method(self):
        """Set up test environment"""
        self.client = TestClient(app)
    
    def test_docs_endpoint(self):
        """Test Swagger UI documentation endpoint"""
        response = self.client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self):
        """Test ReDoc documentation endpoint"""
        response = self.client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "PDF Summarization API"