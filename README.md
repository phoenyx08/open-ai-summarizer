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
  -F "file=@document.pdf"
```

**Response**:
```json
{
  "message": "PDF processed and summary forwarded successfully",
  "filename": "document.pdf",
  "status": "success"
}
```

### Response Codes

- `200 OK`: Successful summary transmission
- `400 Bad Request`: Invalid file or empty upload
- `403 Forbidden`: Invalid/missing authentication token
- `500 Internal Server Error`: Processing failure

## API Workflow

1. **Upload**: Client uploads PDF with Bearer token authentication
2. **Extract**: Service extracts text from PDF using PyMuPDF
3. **Summarize**: Text is summarized using OpenAI GPT-4
4. **Forward**: Summary is sent to configured external API endpoint
5. **Response**: Success confirmation returned to client

## Error Handling

The service includes comprehensive error handling for:
- Invalid file types (non-PDF files)
- Empty files
- PDF processing errors
- OpenAI API failures
- External API communication issues
- Authentication failures

## Development

### Running Tests

```bash
pytest  # If tests are implemented
```

### Code Quality

The codebase follows Python best practices with:
- Type hints
- Comprehensive logging
- Error handling
- Security considerations
- Clear documentation

## Security Notes

- Never commit actual API keys to version control
- Use environment variables for sensitive configuration
- Implement proper token validation
- Consider rate limiting for production use

## License

MIT License - see LICENSE file for details
