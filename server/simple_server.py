from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Tuple, Union
import os
from dotenv import load_dotenv
import json
import requests
from requests.exceptions import RequestException
import re
import sys

# Try to import LangChain modules with error handling
try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import AzureChatOpenAI, ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain.tools import BaseTool
    from langchain_core.tools import Tool
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LangChain import error: {e}")
    LANGCHAIN_AVAILABLE = False

# Load environment variables
load_dotenv()

app = FastAPI(title="HubSpot Agent API Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize HubSpot API configuration
bearer_token = os.getenv("HUBSPOT_BEARER_TOKEN")
api_key = os.getenv("HUBSPOT_API_KEY")

# We'll always use real data from HubSpot
USE_MOCK_DATA = False

# Check if we have valid authentication credentials
if (not bearer_token or bearer_token == "your_developer_ai_bearer_token_here") and \
   (not api_key or api_key == "your_hubspot_api_key_here"):
    print("WARNING: Neither HubSpot Bearer Token nor API Key is set correctly.")
    print("Please set valid HubSpot credentials in the .env file.")

# HubSpot API base URL
HUBSPOT_API_BASE = "https://api.hubapi.com"

# Set up headers for API requests
headers = {
    "Content-Type": "application/json"
}

# Add authorization header if bearer token is available
if bearer_token and bearer_token != "your_developer_ai_bearer_token_here":
    headers["Authorization"] = f"Bearer {bearer_token}"

# Initialize LLM configuration if LangChain is available
if LANGCHAIN_AVAILABLE:
    # Check for Groq API key first
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
    
    # Check for Azure OpenAI configuration
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Initialize LLM based on available configuration
    if GROQ_API_KEY:
        print("Groq API configuration detected")
        try:
            # Initialize the Groq LLM
            llm = ChatOpenAI(
                model=GROQ_MODEL,
                api_key=GROQ_API_KEY,
                temperature=0.7,
                base_url="https://api.groq.com/openai/v1"
            )
            print(f"Groq LLM initialized successfully with model: {GROQ_MODEL}")
        except Exception as e:
            print(f"Error initializing Groq LLM: {e}")
            LANGCHAIN_AVAILABLE = False
    elif all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_BASE, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME]):
        print("Azure OpenAI configuration detected")
        try:
            # Initialize the Azure OpenAI LLM
            llm = AzureChatOpenAI(
                openai_api_version=AZURE_OPENAI_API_VERSION,
                azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
                azure_endpoint=AZURE_OPENAI_API_BASE,
                api_key=AZURE_OPENAI_API_KEY,
                temperature=0.7
            )
            print("Azure OpenAI LLM initialized successfully")
        except Exception as e:
            print(f"Error initializing Azure OpenAI LLM: {e}")
            LANGCHAIN_AVAILABLE = False
    else:
        print("WARNING: Neither Groq nor Azure OpenAI configuration is complete. LangChain agent will not be available.")
        LANGCHAIN_AVAILABLE = False

# Function to generate conversational responses using the configured LLM (Groq or Azure OpenAI)
def generate_conversational_response(query: str, data: Dict[str, Any], object_type: str) -> Tuple[str, Dict[str, Any]]:
    """Generate a conversational response using the configured LLM (Groq or Azure OpenAI) based on the query and data"""
    # Default response if LLM is not available
    default_response = f"Found {len(data.get('results', []))} {object_type}."
    
    # If LLM (Groq or Azure OpenAI) is available, use it to generate a conversational response
    if LANGCHAIN_AVAILABLE and 'llm' in globals():
        try:
            # Extract basic information about the results
            results = data.get('results', [])
            result_count = len(results)
            
            # Create a prompt for the LLM
            prompt = f"""
            You are a helpful assistant that provides concise, conversational responses about HubSpot CRM data.
            
            The user asked: "{query}"
            
            Here is the data retrieved from HubSpot ({result_count} {object_type}):
            {json.dumps(data, indent=2)}
            
            Provide a friendly, conversational response in 1-2 sentences that summarizes the key information.
            Focus on being helpful and concise. Don't list all details, just highlight the most important points.
            """
            
            # Get the response from Azure OpenAI
            response = llm.invoke(prompt)
            conversational_response = response.content if hasattr(response, 'content') else str(response)
            
            return conversational_response.strip(), data
        except Exception as e:
            print(f"Error generating conversational response: {e}")
            return default_response, data
    
    return default_response, data

print(f"HubSpot API configuration initialized successfully. Using {'mock data' if USE_MOCK_DATA else 'live API'}.")
print(f"LangChain integration is {'available' if LANGCHAIN_AVAILABLE else 'NOT available'}.")

# Helper function to make HubSpot API requests
def make_hubspot_request(endpoint, method="GET", params=None, data=None):
    """Make a request to the HubSpot API"""
    url = f"{HUBSPOT_API_BASE}{endpoint}"
    
    # Create a copy of params to avoid modifying the original
    request_params = params.copy() if params else {}
    
    # Add API key to params if we're using API key authentication
    if api_key and api_key != "your_hubspot_api_key_here" and "Authorization" not in headers:
        request_params["hapikey"] = api_key
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=request_params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, params=request_params, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Print response status for debugging
        print(f"HubSpot API response status: {response.status_code}")
        
        if response.status_code == 401:
            print("Authentication failed. Check your HubSpot API key or Bearer Token.")
            # Return empty results instead of failing
            return {"results": [], "total": 0, "message": "Authentication failed"}
            
        response.raise_for_status()  # Raise exception for other 4XX/5XX responses
        return response.json()
    except RequestException as e:
        print(f"Error making request to HubSpot API: {e}")
        # Return empty results with error message
        return {"results": [], "total": 0, "error": str(e)}

# Since we're not using mock data anymore, we don't need these functions
# We'll handle API errors directly in the make_hubspot_request function

# API Models
class QueryRequest(BaseModel):
    query: str
    object_type: str = "contacts"
    limit: int = 25  # Increased default limit
    properties: Optional[List[str]] = None

class QueryResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None
    
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None
    conversation_id: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Simple HubSpot API Server"}

# Helper function to analyze query intent using the configured LLM
def analyze_query_intent(query: str) -> Tuple[str, Dict[str, Any]]:
    """Analyze the intent of a natural language query and extract relevant parameters using the configured LLM (Groq or Azure OpenAI)"""
    # Default values
    intent = "list"
    intent_data = {}
    
    # First try using Azure OpenAI if available
    if LANGCHAIN_AVAILABLE and 'llm' in globals():
        try:
            # Simple direct approach using the LLM
            prompt = f"""
            Analyze this query about HubSpot CRM data: "{query}"
            
            Determine the user's intent from these options:
            - list: List records (default)
            - lookup: Check if a specific record exists
            - search: Search for records matching criteria
            - count: Count records matching criteria
            - filter: Filter records by specific criteria
            
            Also extract these parameters when relevant:
            - object_type: The type of object (contacts, companies, deals)
            - Any search criteria (name, email, industry, etc.)
            - limit: Number of records to return
            
            Format your response as a JSON object with 'intent' and 'intent_data' fields.
            Example: {{"intent": "lookup", "intent_data": {{"object_type": "contacts", "contact_name": "John Smith"}}}}
            
            JSON response:
            """
            
            # Call the LLM directly with a simple string prompt
            response = llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from the response
            try:
                # Look for JSON in code blocks first
                json_match = re.search(r'```(?:json)?\s*(.+?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                else:
                    # Otherwise clean the text and try to extract JSON
                    json_str = re.sub(r'^[^{]*', '', response_text)
                    json_str = re.sub(r'[^}]*$', '', json_str)
                
                # Parse the JSON
                result = json.loads(json_str)
                
                # Extract intent and intent_data
                if 'intent' in result:
                    intent = result['intent']
                if 'intent_data' in result:
                    intent_data = result['intent_data']
                
                print(f"Azure OpenAI intent analysis: {intent}, {json.dumps(intent_data)}")
            except Exception as e:
                print(f"Error parsing Azure OpenAI response: {e}")
                print(f"Raw response: {response_text}")
                # Fall back to basic intent detection
                intent, intent_data = fallback_analyze_query_intent(query)
        except Exception as e:
            print(f"Error using Azure OpenAI for intent analysis: {e}")
            # Fall back to basic intent detection
            intent, intent_data = fallback_analyze_query_intent(query)
    else:
        # Fall back to basic intent detection if Azure OpenAI is not available
        print("Azure OpenAI not available, using fallback intent analysis")
        intent, intent_data = fallback_analyze_query_intent(query)
    
    # Print the detected intent and data for debugging
    print(f"Query Intent: {intent}")
    print(f"Intent Data: {json.dumps(intent_data)}")
    
    return intent, intent_data

# Fallback function for intent analysis when Azure OpenAI is not available
def fallback_analyze_query_intent(query: str) -> Tuple[str, Dict[str, Any]]:
    """Basic rule-based fallback for analyzing query intent"""
    query = query.lower()
    intent_data = {}
    
    # Default intent
    intent = "list"
    
    # Check for existence/lookup intent
    if any(pattern in query for pattern in ["is there", "do we have", "do you have", "exists", "named", "called"]):
        intent = "lookup"
        
        # Try to extract company name
        company_match = re.search(r'company(?:\s+named|\s+called)?\s+([\w\s&-]+)', query)
        if company_match:
            intent_data["company_name"] = company_match.group(1).strip()
            intent_data["object_type"] = "companies"
        
        # Try to extract contact name
        contact_match = re.search(r'contact(?:\s+named|\s+called)?\s+([\w\s&-]+)', query)
        if contact_match:
            intent_data["contact_name"] = contact_match.group(1).strip()
            intent_data["object_type"] = "contacts"
    
    # Check for search intent
    elif any(term in query for term in ["find", "search", "look for", "where", "who has"]):
        intent = "search"
    
    # Check for count intent
    elif any(term in query for term in ["how many", "count", "total number"]):
        intent = "count"
    
    # Check for filter intent
    elif any(term in query for term in ["filter", "only", "with", "that have"]):
        intent = "filter"
    
    # Try to extract filter conditions
    industry_match = re.search(r'industry(?:\s+is)?\s+([\w\s&-]+)', query)
    if industry_match:
        intent_data["industry"] = industry_match.group(1).strip()
        
    # Extract other potential filters
    email_match = re.search(r'email(?:\s+contains)?\s+([\w@.]+)', query)
    if email_match:
        intent_data["email"] = email_match.group(1).strip()
    
    # Check for limit intent
    limit_match = re.search(r'(\d+)\s+(?:contacts|companies|deals)', query)
    if limit_match:
        intent_data["limit"] = int(limit_match.group(1))
    
    # Extract specific object type if mentioned
    if "contact" in query and "object_type" not in intent_data:
        intent_data["object_type"] = "contacts"
    elif "compan" in query and "object_type" not in intent_data:
        intent_data["object_type"] = "companies"
    elif "deal" in query and "object_type" not in intent_data:
        intent_data["object_type"] = "deals"
    
    return intent, intent_data

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        # Analyze the intent of the query
        intent, intent_data = analyze_query_intent(request.query)
        
        # Override object_type if specified in intent_data
        object_type = intent_data.get("object_type", request.object_type.lower())
        
        # Use intent-based limit if available, otherwise use the request limit
        if "limit" in intent_data:
            limit = min(intent_data["limit"], 100)  # Cap at 100 for safety
        else:
            limit = min(request.limit, 100)  # Cap at 100 for safety
        
        # Set default properties based on object type
        properties = request.properties
        if properties is None:
            if object_type == "contacts":
                properties = ["firstname", "lastname", "email", "phone", "company"]
            elif object_type == "companies":
                properties = ["name", "domain", "industry", "website", "phone"]
            elif object_type == "deals":
                properties = ["dealname", "amount", "dealstage", "closedate", "pipeline"]
        
        # Validate object type
        if object_type not in ["contacts", "companies", "deals"]:
            return {
                "response": f"Invalid object_type: {object_type}. Must be one of: contacts, companies, deals",
                "data": None
            }
        
        # Handle lookup intent (e.g., "is there a company named acme?")
        if intent == "lookup":
            search_data = {
                "filterGroups": [{
                    "filters": []
                }],
                "limit": limit
            }
            
            # Add filters based on intent data
            filters = []
            if "company_name" in intent_data and object_type == "companies":
                company_name = intent_data["company_name"]
                filters.append({
                    "propertyName": "name",
                    "operator": "CONTAINS_TOKEN",
                    "value": company_name
                })
            elif "contact_name" in intent_data and object_type == "contacts":
                contact_name = intent_data["contact_name"]
                # Try to match against first or last name
                filters.append({
                    "propertyName": "firstname",
                    "operator": "CONTAINS_TOKEN",
                    "value": contact_name
                })
                
            if filters:
                search_data["filterGroups"][0]["filters"] = filters
                endpoint = f"/crm/v3/objects/{object_type}/search"
                response_dict = make_hubspot_request(endpoint, method="POST", data=search_data)
                
                result_count = len(response_dict.get('results', []))
                if result_count > 0:
                    if object_type == "companies":
                        company_name = intent_data.get("company_name", "the company")
                        response_message = f"Yes, I found {result_count} {'company' if result_count == 1 else 'companies'} matching '{company_name}'."
                    else:
                        contact_name = intent_data.get("contact_name", "the contact")
                        response_message = f"Yes, I found {result_count} {'contact' if result_count == 1 else 'contacts'} matching '{contact_name}'."
                else:
                    if object_type == "companies":
                        company_name = intent_data.get("company_name", "the company")
                        response_message = f"No, I couldn't find any companies matching '{company_name}'."
                    else:
                        contact_name = intent_data.get("contact_name", "the contact")
                        response_message = f"No, I couldn't find any contacts matching '{contact_name}'."
                
                return {
                    "response": response_message,
                    "data": response_dict
                }
        
        # Handle filter intent
        elif intent == "filter" and intent_data:
            # If we have filter conditions, we'll use the search endpoint instead
            search_data = {
                "filterGroups": [{
                    "filters": []
                }],
                "limit": limit
            }
            
            # Add filters based on intent data
            filters = []
            if "industry" in intent_data and object_type == "companies":
                filters.append({
                    "propertyName": "industry",
                    "operator": "CONTAINS_TOKEN",
                    "value": intent_data["industry"]
                })
            if "email" in intent_data and object_type == "contacts":
                filters.append({
                    "propertyName": "email",
                    "operator": "CONTAINS_TOKEN",
                    "value": intent_data["email"]
                })
                
            if filters:
                search_data["filterGroups"][0]["filters"] = filters
                endpoint = f"/crm/v3/objects/{object_type}/search"
                response_dict = make_hubspot_request(endpoint, method="POST", data=search_data)
                
                result_count = len(response_dict.get('results', []))
                response_message = f"Found {result_count} {object_type} matching your filter criteria."
                
                return {
                    "response": response_message,
                    "data": response_dict
                }
        
        # Build query parameters
        params = {
            "limit": limit,
            "archived": "false"
        }
        
        # For contacts, only add properties if explicitly requested
        # This matches the working curl command format
        if object_type != "contacts" and properties:
            params["properties"] = ",".join(properties)
        
        # Make API request to HubSpot
        endpoint = f"/crm/v3/objects/{object_type}"
        print(f"Making request to: {HUBSPOT_API_BASE}{endpoint} with params: {params}")
        response_dict = make_hubspot_request(endpoint, params=params)
        
        # Generate a conversational response using Azure OpenAI
        conversational_response, formatted_data = generate_conversational_response(request.query, response_dict, object_type)
        
        return {
            "response": conversational_response,
            "data": formatted_data
        }
    except Exception as e:
        print(f"Error processing query: {e}")
        return {
            "response": f"An error occurred while processing your query: {str(e)}",
            "data": None
        }

@app.post("/search", response_model=QueryResponse)
async def search_hubspot(request: QueryRequest):
    try:
        # Analyze the intent of the query
        intent, intent_data = analyze_query_intent(request.query)
        
        # Override object_type if specified in intent_data
        object_type = intent_data.get("object_type", request.object_type.lower())
        
        # Use intent-based limit if available, otherwise use the request limit
        if "limit" in intent_data:
            limit = min(intent_data["limit"], 100)  # Cap at 100 for safety
        else:
            limit = min(request.limit, 100)  # Cap at 100 for safety
            
        search_query = request.query.lower()
        
        # Validate object type
        if object_type not in ["contacts", "companies", "deals"]:
            return {
                "response": f"Invalid object_type: {object_type}. Must be one of: contacts, companies, deals",
                "data": None
            }
        
        # Prepare search request data
        search_data = {
            "query": request.query,
            "limit": limit
        }
        
        # Make API request to HubSpot search endpoint
        endpoint = f"/crm/v3/objects/{object_type}/search"
        response_dict = make_hubspot_request(endpoint, method="POST", data=search_data)
        
        # Generate a conversational response using Azure OpenAI
        conversational_response, formatted_data = generate_conversational_response(request.query, response_dict, object_type)
        
        return {
            "response": conversational_response,
            "data": formatted_data
        }
    except Exception as e:
        print(f"Error searching HubSpot: {e}")
        return {
            "response": f"An error occurred while searching HubSpot: {str(e)}",
            "data": None
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# LangChain Agent Setup
if LANGCHAIN_AVAILABLE:
    # Define HubSpot tools with enhanced capabilities
    class HubSpotContactsTool(BaseTool):
        name: str = "get_hubspot_contacts"
        description: str = "Get contacts from HubSpot. Useful for finding contact information. You can search for specific contacts by name, email, or other properties."
        
        def _run(self, limit: int = 25, query: str = None, properties: List[str] = None):
            try:
                # Analyze query intent if provided
                if query:
                    # Use search endpoint with enhanced capabilities
                    search_data = {"query": query, "limit": limit}
                    
                    # Check if we need to add specific filters
                    if "@" in query:
                        # Likely looking for a specific email
                        search_data["filterGroups"] = [{
                            "filters": [{
                                "propertyName": "email",
                                "operator": "CONTAINS_TOKEN",
                                "value": query
                            }]
                        }]
                    
                    endpoint = "/crm/v3/objects/contacts/search"
                    response = make_hubspot_request(endpoint, method="POST", data=search_data)
                else:
                    # Use list endpoint with minimal parameters to match working curl command
                    params = {"limit": limit, "archived": "false"}
                    
                    # Don't add properties parameter for contacts as it may cause issues
                    # This matches the working curl command format
                    endpoint = "/crm/v3/objects/contacts"
                    print(f"HubSpotContactsTool making request to: {HUBSPOT_API_BASE}{endpoint} with params: {params}")
                    response = make_hubspot_request(endpoint, params=params)
                
                # Format the response for better readability
                results = response.get("results", [])
                if results:
                    formatted_results = []
                    for contact in results:
                        props = contact.get("properties", {})
                        formatted_contact = {
                            "id": contact.get("id"),
                            "name": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                            "email": props.get("email", ""),
                            "phone": props.get("phone", ""),
                            "company": props.get("company", "")
                        }
                        formatted_results.append(formatted_contact)
                    
                    return json.dumps({"count": len(formatted_results), "contacts": formatted_results}, indent=2)
                else:
                    return json.dumps({"count": 0, "contacts": [], "message": "No contacts found"}, indent=2)
            except Exception as e:
                return f"Error retrieving contacts: {str(e)}"
    
    class HubSpotCompaniesTool(BaseTool):
        name: str = "get_hubspot_companies"
        description: str = "Get companies from HubSpot. Useful for finding company information. You can search for specific companies by name, domain, industry, or other properties."
        
        def _run(self, limit: int = 25, query: str = None, properties: List[str] = None):
            try:
                # Analyze query intent if provided
                if query:
                    # Use search endpoint with enhanced capabilities
                    search_data = {"query": query, "limit": limit}
                    
                    # Check if we need to add specific filters
                    if ".com" in query or ".org" in query or ".net" in query:
                        # Likely looking for a specific domain
                        search_data["filterGroups"] = [{
                            "filters": [{
                                "propertyName": "domain",
                                "operator": "CONTAINS_TOKEN",
                                "value": query
                            }]
                        }]
                    
                    endpoint = "/crm/v3/objects/companies/search"
                    response = make_hubspot_request(endpoint, method="POST", data=search_data)
                else:
                    # Use list endpoint with properties
                    params = {"limit": limit, "archived": "false"}
                    
                    # Set default properties if not specified
                    if not properties:
                        properties = ["name", "domain", "industry", "website", "phone"]
                    
                    params["properties"] = ",".join(properties)
                    endpoint = "/crm/v3/objects/companies"
                    response = make_hubspot_request(endpoint, params=params)
                
                # Format the response for better readability
                results = response.get("results", [])
                if results:
                    formatted_results = []
                    for company in results:
                        props = company.get("properties", {})
                        formatted_company = {
                            "id": company.get("id"),
                            "name": props.get("name", ""),
                            "domain": props.get("domain", ""),
                            "industry": props.get("industry", ""),
                            "website": props.get("website", "")
                        }
                        formatted_results.append(formatted_company)
                    
                    return json.dumps({"count": len(formatted_results), "companies": formatted_results}, indent=2)
                else:
                    return json.dumps({"count": 0, "companies": [], "message": "No companies found"}, indent=2)
            except Exception as e:
                return f"Error retrieving companies: {str(e)}"
    
    class HubSpotDealsTool(BaseTool):
        name: str = "get_hubspot_deals"
        description: str = "Get deals from HubSpot. Useful for finding deal information. You can search for specific deals by name, amount, stage, or other properties."
        
        def _run(self, limit: int = 25, query: str = None, properties: List[str] = None):
            try:
                # Analyze query intent if provided
                if query:
                    # Use search endpoint with enhanced capabilities
                    search_data = {"query": query, "limit": limit}
                    
                    # Check if we need to add specific filters
                    if any(stage in query.lower() for stage in ["closed", "won", "lost", "negotiation", "proposal"]):
                        # Likely looking for deals in a specific stage
                        stage_map = {
                            "closed won": "closed_won",
                            "closed lost": "closed_lost",
                            "negotiation": "negotiation",
                            "proposal": "proposal"
                        }
                        
                        for key, value in stage_map.items():
                            if key in query.lower():
                                search_data["filterGroups"] = [{
                                    "filters": [{
                                        "propertyName": "dealstage",
                                        "operator": "EQ",
                                        "value": value
                                    }]
                                }]
                                break
                    
                    endpoint = "/crm/v3/objects/deals/search"
                    response = make_hubspot_request(endpoint, method="POST", data=search_data)
                else:
                    # Use list endpoint with properties
                    params = {"limit": limit, "archived": "false"}
                    
                    # Set default properties if not specified
                    if not properties:
                        properties = ["dealname", "amount", "dealstage", "closedate", "pipeline"]
                    
                    params["properties"] = ",".join(properties)
                    endpoint = "/crm/v3/objects/deals"
                    response = make_hubspot_request(endpoint, params=params)
                
                # Format the response for better readability
                results = response.get("results", [])
                if results:
                    formatted_results = []
                    for deal in results:
                        props = deal.get("properties", {})
                        formatted_deal = {
                            "id": deal.get("id"),
                            "name": props.get("dealname", ""),
                            "amount": props.get("amount", ""),
                            "stage": props.get("dealstage", ""),
                            "close_date": props.get("closedate", "")
                        }
                        formatted_results.append(formatted_deal)
                    
                    return json.dumps({"count": len(formatted_results), "deals": formatted_results}, indent=2)
                else:
                    return json.dumps({"count": 0, "deals": [], "message": "No deals found"}, indent=2)
            except Exception as e:
                return f"Error retrieving deals: {str(e)}"
    
    # Create tools
    tools = [
        HubSpotContactsTool(),
        HubSpotCompaniesTool(),
        HubSpotDealsTool()
    ]
    
    # Create system message with more detailed instructions
    system_message_content = """
    You are an intelligent HubSpot assistant powered by Azure OpenAI GPT-4o. Your purpose is to help users query and understand their HubSpot data through natural language conversations.
    
    You have access to the following HubSpot data through specialized tools:
    1. Contacts - Information about individuals in the CRM
    2. Companies - Business entities in the CRM
    3. Deals - Sales opportunities and their stages
    
    When responding to user queries:
    - Understand the user's intent and use the appropriate tool to retrieve relevant information
    - Provide concise, well-formatted responses that highlight the key information
    - For company or contact searches, try to identify the specific entity the user is looking for
    - When presenting data, format it in a readable way (not raw JSON)
    - If you can't find what the user is looking for, suggest alternatives or ask clarifying questions
    - Always maintain a conversational, helpful tone
    
    Examples of queries you can handle:
    - "Find contacts at Acme Corp"
    - "Show me deals in the negotiation stage"
    - "Is there a company named Fusion in our database?"
    - "Get me contact information for anyone with a gmail address"
    
    Remember to analyze the query intent and use the most appropriate tool with the right parameters.
    """
    
    # Create a proper ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message_content),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create the agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # Create conversation memory
    memory = ConversationBufferMemory(return_messages=True)
    
    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
    
    # Dictionary to store conversation memories for different users
    conversation_memories = {}

def natural_language_search(query: str) -> str:
    """Process a natural language query and search HubSpot for relevant information"""
    try:
        # Analyze the intent of the query
        intent, intent_data = analyze_query_intent(query)
        
        # Set default response
        response = "I couldn't understand what you're looking for. Please try to be more specific."
        
        if intent == "lookup" and "company_name" in intent_data:
            # Looking up a specific company
            company_name = intent_data["company_name"]
            endpoint = "/crm/v3/objects/companies/search"
            data = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "name",
                        "operator": "CONTAINS_TOKEN",
                        "value": company_name
                    }]
                }],
                "properties": ["name", "domain", "industry", "website", "phone"],
                "limit": 5
            }
            result = make_hubspot_request(endpoint, method="POST", data=data)
            
            if result.get("total", 0) > 0:
                companies = result.get("results", [])
                response = f"I found {len(companies)} companies matching '{company_name}':\n"
                for company in companies:
                    props = company.get("properties", {})
                    name = props.get('name', 'Unknown')
                    domain = props.get('domain', 'No domain')
                    industry = props.get('industry', 'Unknown industry')
                    response += f"- {name} (Domain: {domain}, Industry: {industry})\n"
            else:
                response = f"I couldn't find any company matching '{company_name}'."
        
        elif intent == "lookup" and "contact_name" in intent_data:
            # Looking up a specific contact
            contact_name = intent_data["contact_name"]
            endpoint = "/crm/v3/objects/contacts/search"
            data = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "firstname",
                        "operator": "CONTAINS_TOKEN",
                        "value": contact_name
                    }]
                }],
                "properties": ["firstname", "lastname", "email", "phone", "company"],
                "limit": 5
            }
            result = make_hubspot_request(endpoint, method="POST", data=data)
            
            if result.get("total", 0) > 0:
                contacts = result.get("results", [])
                response = f"I found {len(contacts)} contacts matching '{contact_name}':\n"
                for contact in contacts:
                    props = contact.get("properties", {})
                    name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
                    email = props.get("email", "No email")
                    company = props.get("company", "")
                    phone = props.get("phone", "No phone")
                    response += f"- {name} ({email}, {company}, {phone})\n"
            else:
                response = f"I couldn't find any contacts matching '{contact_name}'."
        
        elif intent == "list" and intent_data.get("object_type") == "deals":
            # List deals, possibly filtered by stage
            endpoint = "/crm/v3/objects/deals"
            params = {
                "limit": intent_data.get("limit", 5),
                "properties": "dealname,amount,dealstage,closedate"
            }
            
            # Add stage filter if specified
            if "stage" in intent_data:
                stage = intent_data["stage"]
                endpoint = "/crm/v3/objects/deals/search"
                params = {}
                data = {
                    "filterGroups": [{
                        "filters": [{
                            "propertyName": "dealstage",
                            "operator": "EQ",
                            "value": stage
                        }]
                    }],
                    "properties": ["dealname", "amount", "dealstage", "closedate"],
                    "limit": intent_data.get("limit", 5)
                }
                result = make_hubspot_request(endpoint, method="POST", data=data)
            else:
                result = make_hubspot_request(endpoint, params=params)
            
            if result.get("total", 0) > 0 or len(result.get("results", [])) > 0:
                deals = result.get("results", [])
                response = f"I found {len(deals)} deals:\n"
                for deal in deals:
                    props = deal.get("properties", {})
                    name = props.get("dealname", "Unnamed deal")
                    amount = props.get("amount", "Unknown amount")
                    stage = props.get("dealstage", "Unknown stage")
                    close_date = props.get("closedate", "No close date")
                    response += f"- {name} (Amount: {amount}, Stage: {stage}, Close date: {close_date})\n"
            else:
                response = "I couldn't find any deals matching your criteria."
        
        elif intent == "list" and intent_data.get("object_type") in ["contacts", "companies"]:
            # List contacts or companies, possibly filtered
            object_type = intent_data.get("object_type")
            endpoint = f"/crm/v3/objects/{object_type}"
            params = {
                "limit": intent_data.get("limit", 5)
            }
            
            # Set properties based on object type
            if object_type == "contacts":
                params["properties"] = "firstname,lastname,email,phone,company"
            else:  # companies
                params["properties"] = "name,domain,industry,website,phone"
            
            # Add filters if specified
            filters = []
            if "industry" in intent_data and object_type == "companies":
                filters.append({
                    "propertyName": "industry",
                    "operator": "CONTAINS_TOKEN",
                    "value": intent_data["industry"]
                })
            
            if "email" in intent_data and object_type == "contacts":
                filters.append({
                    "propertyName": "email",
                    "operator": "CONTAINS_TOKEN",
                    "value": intent_data["email"]
                })
            
            if filters:
                endpoint = f"/crm/v3/objects/{object_type}/search"
                params = {}
                data = {
                    "filterGroups": [{
                        "filters": filters
                    }],
                    "limit": intent_data.get("limit", 5)
                }
                
                # Set properties based on object type
                if object_type == "contacts":
                    data["properties"] = ["firstname", "lastname", "email", "phone", "company"]
                else:  # companies
                    data["properties"] = ["name", "domain", "industry", "website", "phone"]
                
                result = make_hubspot_request(endpoint, method="POST", data=data)
            else:
                result = make_hubspot_request(endpoint, params=params)
            
            if result.get("total", 0) > 0 or len(result.get("results", [])) > 0:
                items = result.get("results", [])
                response = f"I found {len(items)} {object_type}:\n"
                
                for item in items:
                    props = item.get("properties", {})
                    if object_type == "contacts":
                        name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
                        email = props.get("email", "No email")
                        company = props.get("company", "")
                        response += f"- {name} ({email}, {company})\n"
                    else:  # companies
                        name = props.get("name", "Unknown")
                        industry = props.get("industry", "Unknown industry")
                        domain = props.get("domain", "No domain")
                        response += f"- {name} (Industry: {industry}, Domain: {domain})\n"
            else:
                response = f"I couldn't find any {object_type} matching your criteria."
        
        return response
    except Exception as e:
        return f"Error processing your query: {str(e)}"

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the LangChain agent to query HubSpot data conversationally"""
    conversation_id = request.conversation_id or f"conv_{len(conversation_memories) + 1}"
    
    if not LANGCHAIN_AVAILABLE:
        return {
            "response": "LangChain integration is not available. Please install the required packages.",
            "data": None,
            "conversation_id": conversation_id
        }
    
    try:
        # Get or create conversation memory for this user
        if conversation_id not in conversation_memories:
            conversation_memories[conversation_id] = ConversationBufferMemory(return_messages=True)
            print(f"Created new conversation memory for conversation {conversation_id}")
        
        # Create a new agent executor with this conversation's memory
        user_agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=conversation_memories[conversation_id],
            verbose=True
        )
        
        # Log the incoming message for debugging
        print(f"Processing message from conversation {conversation_id}: {request.message}")
        
        # Run the agent with the user's message
        response = user_agent_executor.run(request.message)
        
        # Log the response for debugging
        print(f"Agent response: {response[:100]}..." if len(response) > 100 else f"Agent response: {response}")
        
        # Try to extract structured data if available
        data = None
        try:
            # Look for JSON in the response
            json_start = response.find('```json') + 7
            json_end = response.find('```', json_start)
            if json_start > 7 and json_end > json_start:
                json_str = response[json_start:json_end].strip()
                data = json.loads(json_str)
        except Exception as json_error:
            print(f"Could not extract JSON data: {json_error}")
        
        return {
            "response": response,
            "data": data,
            "conversation_id": conversation_id
        }
    except Exception as e:
        error_message = str(e)
        print(f"Error in LangChain agent: {error_message}")
        
        # Check if this is an authentication error with Azure OpenAI
        if "authentication" in error_message.lower() or "api key" in error_message.lower():
            return {
                "response": "There seems to be an issue with the Azure OpenAI authentication. Please check your API keys and try again.",
                "data": None,
                "conversation_id": conversation_id
            }
        
        # Check if this is a rate limit error
        elif "rate limit" in error_message.lower() or "too many requests" in error_message.lower():
            return {
                "response": "I'm currently experiencing high demand. Please try again in a moment.",
                "data": None,
                "conversation_id": conversation_id
            }
        
        # Fall back to the simple search method for other errors
        try:
            print("Falling back to simple search method")
            result = natural_language_search(request.message)
            return {
                "response": f"I encountered an issue with the advanced AI agent, so I'm using a simpler method to answer your question: {result}",
                "data": None,
                "conversation_id": conversation_id
            }
        except Exception as fallback_error:
            return {
                "response": f"I'm sorry, but I encountered an error processing your request. Please try again with a different query or check your HubSpot connection. Error details: {str(fallback_error)}",
                "data": None,
                "conversation_id": conversation_id
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_server:app", host="0.0.0.0", port=8000, reload=True)
