# HubSpot Agentic Workflow Server

This is the backend server for the HubSpot Agentic Workflow application. It provides an API for querying HubSpot data using natural language through Azure OpenAI and LangChain.

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
