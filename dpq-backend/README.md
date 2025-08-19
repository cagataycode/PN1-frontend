# DPQ Backend

Dog Personality Quiz Backend Server - FastAPI-based backend for the DPQ mobile application.

## Features

- FastAPI web framework
- Supabase database integration
- Claude AI API integration
- DPQ analysis algorithms
- Video processing capabilities
- RESTful API endpoints

## Setup

### 1. Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key
- `ANTHROPIC_API_KEY`: Your Claude API key

### 3. Run the Server

```bash
# Development mode with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

### 4. API Documentation

Once running, visit:

- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
dpq-backend/
├── app/                    # Main application package
│   ├── main.py            # FastAPI application entry point
│   ├── config/            # Configuration management
│   ├── api/               # API routes and endpoints
│   ├── services/          # Business logic services
│   └── models/            # Data models and schemas
├── dpq/                   # DPQ analysis logic (migrated)
├── jobs/                  # Video processing jobs (migrated)
├── bin/                   # FFmpeg binaries (migrated)
├── tests/                 # Test files
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Development

### Adding New Endpoints

1. Create route files in `app/api/routes/`
2. Import and include them in the main app
3. Add proper validation and error handling

### Adding New Services

1. Create service files in `app/services/`
2. Implement business logic
3. Add proper error handling and logging

## Testing

Run tests with:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_dpq.py

# Run with coverage
python -m pytest --cov=app
```

## Deployment

The backend is designed to be deployed to platforms like:

- Railway
- Render
- Fly.io
- Heroku

Ensure all environment variables are properly configured in your deployment environment.

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with service information
- `GET /health` - Comprehensive health check
- `GET /api/health` - API-specific health check
- `GET /api/info` - API configuration information

### Documentation

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - ReDoc API documentation

### Health Check Response Example

```json
{
  "status": "healthy",
  "service": "DPQ Backend API",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2024-01-01T00:00:00.000000",
  "checks": {
    "api": "healthy",
    "config": "loaded",
    "logging": "configured"
  }
}
```

## Features

### Environment Configuration

- Automatic environment detection (development/production)
- Environment-specific CORS settings
- Configurable logging levels
- File upload limits per environment

### Error Handling

- Global exception handlers
- Structured error responses
- Request validation error handling
- Comprehensive logging

### Logging

- Environment-based log levels
- File logging in production
- Structured log formatting
- Request/response logging

More endpoints will be added as development progresses.
