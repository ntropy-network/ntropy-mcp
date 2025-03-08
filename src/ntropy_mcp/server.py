from mcp.server.fastmcp import FastMCP, Context
import requests
import os
from typing import List, Optional, Dict, Any

mcp = FastMCP(
    "MCP server for enriching banking data using the Ntropy API",
    dependencies=["requests"]
)

# Global API key
API_KEY = None

def handle_api_response(response):
    """Helper function to handle API responses and errors"""
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        error_info = {}
        try:
            error_info = response.json()
        except:
            error_info = {"error": str(e)}
        
        return {
            "status": "error",
            "status_code": response.status_code,
            "message": f"API request failed: {str(e)}",
            "details": error_info
        }

@mcp.tool()
def create_account_holder(
    id: str | int,
    type: str,
    name: str
) -> dict:
    """Create an account holder"""
    url = "https://api.ntropy.com/v3/account_holders"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": API_KEY,
    }
    data = {
        "type": type,
        "name": name,
        "id": str(id)
    }
    response = requests.post(url, headers=headers, json=data)
    return handle_api_response(response)

@mcp.tool()
def enrich_transaction(
    id: str | int,
    description: str,
    date: str,
    amount: float,
    entry_type: str,
    currency: str,
    account_holder_id: str | int,
    country: str = None,
) -> dict:
    """Enrich a bank transaction"""

    url = "https://api.ntropy.com/v3/transactions"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    data = {
        "id": str(id),
        "description": description,
        "date": date,
        "amount": amount,
        "entry_type": entry_type,
        "currency": currency,
        "account_holder_id": str(account_holder_id),
    }
    
    if country:
        data["location"] = {"country": country}
        
    response = requests.post(url, headers=headers, json=data)
    return handle_api_response(response)

@mcp.tool()
def get_account_holder(account_holder_id: str | int) -> dict:
    """Get details of an account holder"""
    url = f"https://api.ntropy.com/v3/account_holders/{account_holder_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers)
    return handle_api_response(response)

@mcp.tool()
def list_transactions(
    account_holder_id: str | int,
    limit: int = 10,
    offset: int = 0
) -> dict:
    """List transactions for an account holder"""
    url = f"https://api.ntropy.com/v3/transactions"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    params = {
        "account_holder_id": str(account_holder_id),
        "limit": limit,
        "offset": offset
    }
    response = requests.get(url, headers=headers, params=params)
    return handle_api_response(response)

@mcp.tool()
def get_transaction(transaction_id: str | int) -> dict:
    """Get details of a specific transaction"""
    url = f"https://api.ntropy.com/v3/transactions/{transaction_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers)
    return handle_api_response(response)

@mcp.tool()
def bulk_enrich_transactions(transactions: List[Dict[str, Any]]) -> dict:
    """Enrich multiple transactions at once"""
    url = "https://api.ntropy.com/v3/transactions/bulk"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    
    # Make sure all transaction IDs are strings
    for tx in transactions:
        if "id" in tx:
            tx["id"] = str(tx["id"])
        if "account_holder_id" in tx:
            tx["account_holder_id"] = str(tx["account_holder_id"])
    
    data = {"transactions": transactions}
    response = requests.post(url, headers=headers, json=data)
    return handle_api_response(response)

@mcp.tool()
def delete_account_holder(account_holder_id: str | int) -> dict:
    """Delete an account holder and all associated data"""
    url = f"https://api.ntropy.com/v3/account_holders/{account_holder_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.delete(url, headers=headers)
    return handle_api_response(response)

@mcp.tool()
def delete_transaction(transaction_id: str | int) -> dict:
    """Delete a specific transaction"""
    url = f"https://api.ntropy.com/v3/transactions/{transaction_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.delete(url, headers=headers)
    return handle_api_response(response)

def main(api_key: str):
    global API_KEY
    API_KEY = api_key
    
    # Validate API key
    if not API_KEY:
        raise ValueError("Ntropy API key is required")
    
    print("Starting Ntropy MCP server...")
    try:
        mcp.run()
    except Exception as e:
        print(f"Error running MCP server: {str(e)}")
        raise
