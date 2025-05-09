# HubSpot Agentic Workflow Server

This is the backend server for the HubSpot Agentic Workflow application. It provides an API for querying HubSpot data using natural language through LangChain with either Groq API or Azure OpenAI.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Create a `.env` file based on the `.env.example` template and add your API keys:
```
cp .env.example .env
```

3. Edit the `.env` file with your actual API keys and configuration.

## LLM Configuration

The server supports two LLM providers:

### Groq API (Recommended)

To use Groq API, set the following environment variables in your `.env` file:
```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
```

The system will automatically use Groq if a valid API key is provided.

### Azure OpenAI (Alternative)

If Groq API key is not provided, the system will fall back to Azure OpenAI if configured:
```
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_API_BASE=your_azure_endpoint
AZURE_OPENAI_API_VERSION=your_api_version
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

## Running the Server

Start the server with:
```
python main.py
```

The server will be available at http://localhost:8000

## API Endpoints

- `GET /`: Welcome message
- `POST /query`: Main endpoint for querying HubSpot data
- `GET /health`: Health check endpoint

## Query Example

```json
POST /query
{
  "query": "Find all contacts from the technology industry",
  "history": []
}
```
