import pytest
import os
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import fitz

# Import functions from main module
from main import (
    app, 
    extract_text_from_pdf, 
    summarize_text, 
    forward_summary,
    verify_token
)

class TestPDFExtraction:
    """Test PDF text extraction functionality"""
    
    def test_extract_text_from_pdf_success(self):
        """Test successful PDF text extraction"""
        # Create a simple PDF in memory
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((100, 100), "This is a test PDF document with sample content.")
        pdf_bytes = doc.write()
        doc.close()
        
        # Test extraction
        result = extract_text_from_pdf(pdf_bytes)
        assert "This is a test PDF document with sample content." in result
        assert len(result.strip()) > 0
    
    def test_extract_text_from_pdf_empty(self):
        """Test PDF with no text content"""
        # Create an empty PDF
        doc = fitz.open()
        doc.new_page()  # Empty page
        pdf_bytes = doc.write()
        doc.close()
        
        # Test extraction - should raise exception for empty content
        with pytest.raises(HTTPException) as exc_info:
            extract_text_from_pdf(pdf_bytes)
        assert exc_info.value.status_code == 500
    
    def test_extract_text_from_pdf_invalid(self):
        """Test invalid PDF content"""
        invalid_pdf = b"This is not a PDF file"
        
        with pytest.raises(HTTPException) as exc_info:
            extract_text_from_pdf(invalid_pdf)
        assert exc_info.value.status_code == 500

class TestOpenAIIntegration:
    """Test OpenAI summarization functionality"""
    
    @pytest.mark.asyncio
    async def test_summarize_text_success(self):
        """Test successful text summarization"""
        test_text = "This is a long document that needs to be summarized for testing purposes."
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "This is a test summary."
        
        with patch('main.openai_client.chat.completions.create', return_value=mock_response):
            result = await summarize_text(test_text)
            assert result == "This is a test summary."
    
    @pytest.mark.asyncio
    async def test_summarize_text_api_error(self):
        """Test OpenAI API error handling"""
        test_text = "Test text for summarization"
        
        with patch('main.openai_client.chat.completions.create', side_effect=Exception("API Error")):
            with pytest.raises(HTTPException) as exc_info:
                await summarize_text(test_text)
            assert exc_info.value.status_code == 500

class TestExternalAPIIntegration:
    """Test external API forwarding functionality"""
    
    @pytest.mark.asyncio
    async def test_forward_summary_success(self):
        """Test successful summary forwarding"""
        test_summary = "Test summary content"
        test_filename = "test.pdf"
        test_entity_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Mock httpx response
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await forward_summary(test_summary, test_filename, test_entity_id)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_forward_summary_api_error(self):
        """Test external API error handling"""
        test_summary = "Test summary content"
        test_filename = "test.pdf"
        test_entity_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Mock httpx response with error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(HTTPException) as exc_info:
                await forward_summary(test_summary, test_filename, test_entity_id)
            assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_forward_summary_timeout(self):
        """Test timeout handling"""
        test_summary = "Test summary content"
        test_filename = "test.pdf"
        test_entity_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Timeout")
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await forward_summary(test_summary, test_filename, test_entity_id)
            assert exc_info.value.status_code == 500

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_verify_token_success(self):
        """Test successful token verification"""
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Mock credentials with correct token
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = os.getenv("AUTH_TOKEN", "test_bearer_token")
        
        with patch.dict(os.environ, {"AUTH_TOKEN": "test_bearer_token"}):
            result = verify_token(mock_credentials)
            assert result == "test_bearer_token"
    
    def test_verify_token_invalid(self):
        """Test invalid token handling"""
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Mock credentials with wrong token
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "invalid_token"
        
        with patch.dict(os.environ, {"AUTH_TOKEN": "test_bearer_token"}):
            with pytest.raises(HTTPException) as exc_info:
                verify_token(mock_credentials)
            assert exc_info.value.status_code == 403