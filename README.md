# PDF Document Summarization API

A FastAPI service that accepts PDF documents, extracts text, generates summaries using OpenAI, and forwards the summaries to an external API endpoint.

## Features

- **PDF Upload**: Secure endpoint for PDF document uploads
- **Text Extraction**: Uses PyMuPDF for reliable PDF text extraction
- **AI Summarization**: Leverages OpenAI GPT-4 for intelligent document summarization
- **External API Integration**: Forwards summaries to configured external endpoints
- **Authentication**: Bearer token security for API access
- **Error Handling**: Comprehensive error handling and logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/phoenyx08/open-ai-summarizer.git
cd open-ai-summarizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

## Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Authentication
AUTH_TOKEN=your_bearer_token_here

# External API Configuration
EXTERNAL_API_URL=https://external-api.example.com/summaries
EXTERNAL_API_TOKEN=your_external_api_token_here

# Application Configuration (optional)
PORT=8000
HOST=0.0.0.0
```

## Usage

### Starting the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Upload PDF for Summarization

**Endpoint**: `POST /upload`

**Headers**:
```
Authorization: Bearer your_bearer_token_here
Content-Type: multipart/form-data
```

**Request**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer your_bearer_token_here" \
  -F "file=@document.pdf" \
  -F "entityId=123e4567-e89b-12d3-a456-426614174000"
```

**Response**:
```json
{
  "message": "PDF processed and summary forwarded successfully",
  "filename": "document.pdf",
  "entityId": "123e4567-e89b-12d3-a456-426614174000",
  "status": "success"
}
```

### Request Parameters

- `file`: PDF document to be summarized (required)
- `entityId`: UUID string for data traceability (required)

### Response Codes

- `200 OK`: Successful summary transmission
- `400 Bad Request`: Invalid file, empty upload, or invalid entityId format
- `403 Forbidden`: Invalid/missing authentication token
- `422 Unprocessable Entity`: Missing required parameters
- `500 Internal Server Error`: Processing failure

## API Workflow

1. **Upload**: Client uploads PDF with entityId and Bearer token authentication
2. **Validate**: Service validates entityId format (must be valid UUID)
3. **Extract**: Service extracts text from PDF using PyMuPDF
4. **Summarize**: Text is summarized using OpenAI GPT-4
5. **Forward**: Summary with entityId is sent to configured external API endpoint
6. **Response**: Success confirmation with entityId returned to client

## Error Handling

The service includes comprehensive error handling for:
- Invalid file types (non-PDF files)
- Empty files
- Invalid entityId format (must be valid UUID)
- Missing required parameters
- PDF processing errors
- OpenAI API failures
- External API communication issues
- Authentication failures

## Development

### Running Tests

The project includes comprehensive testing capabilities:

#### Quick Test Run
```bash
python run_tests.py
```

#### Manual Test Commands

1. **Install test dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run unit tests**:
```bash
pytest tests/test_unit.py -v
```

3. **Run integration tests**:
```bash
pytest tests/test_integration.py -v
```

4. **Run all tests**:
```bash
pytest tests/ -v
```

#### Test Environment Setup

1. **Create test PDF**:
```bash
python create_test_pdf.py
```

2. **Start mock external API server**:
```bash
python mock_external_api.py
```

3. **Test the full flow manually**:
```bash
# In one terminal - start mock external API
python mock_external_api.py

# In another terminal - start main application
uvicorn main:app --reload

# In a third terminal - test upload
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer test_bearer_token" \
  -F "file=@tests/sample_document.pdf" \
  -F "entityId=123e4567-e89b-12d3-a456-426614174000"
```

#### Test Coverage

The test suite includes:
- **Unit Tests**: Test individual functions (PDF extraction, OpenAI integration, authentication)
- **Integration Tests**: Test API endpoints and full request/response flow
- **End-to-End Tests**: Test complete workflow with mock external API
- **Error Handling Tests**: Test various error conditions and edge cases

#### Test Configuration

- **Test Environment**: Uses `.env.test` for test-specific configuration
- **Mock Services**: Includes mock external API server for testing
- **Sample Data**: Automatically generated test PDF files
- **Test Isolation**: Each test runs independently with proper setup/teardown

### Code Quality

The codebase follows Python best practices with:
- Type hints
- Comprehensive logging
- Error handling
- Security considerations
- Clear documentation
- Comprehensive test coverage

## Security Notes

- Never commit actual API keys to version control
- Use environment variables for sensitive configuration
- Implement proper token validation
- Consider rate limiting for production use

## License

MIT License - see LICENSE file for details
