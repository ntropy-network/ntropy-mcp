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
    """Create an account holder in Ntropy API
    
    Creates a new account holder entity which can be associated with transactions.
    An account holder represents an individual or business with a financial account.
    
    Parameters:
        id: Unique identifier for the account holder (will be converted to string)
        type: Type of account holder - must be one of: 'individual', 'business'
        name: Display name for the account holder
        
    Returns:
        dict: JSON response from API containing the created account holder information
            On success, includes 'id', 'name', 'type', and other account holder details
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
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
    """Enrich a single bank transaction using Ntropy API
    
    Sends transaction data to Ntropy for categorization and enrichment, returning
    detailed information about the transaction including merchant name, category,
    industry, and more.
    
    Parameters:
        id: Unique identifier for the transaction (will be converted to string)
        description: Transaction description as it appears on the bank statement
        date: Transaction date in ISO 8601 format (YYYY-MM-DD)
        amount: Transaction amount (positive for credit, negative for debit)
        entry_type: Transaction type - must be one of: 'credit', 'debit'
        currency: Three-letter currency code (e.g., 'USD', 'EUR', 'GBP')
        account_holder_id: ID of the account holder who made the transaction
        country: Optional two-letter country code (e.g., 'US', 'GB')
        
    Returns:
        dict: JSON response from API containing the enriched transaction data
            On success, includes categorization, merchant details, and confidence scores
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
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
    """Get details of an existing account holder
    
    Retrieves complete information for an account holder by their ID.
    
    Parameters:
        account_holder_id: ID of the account holder to retrieve (will be converted to string)
        
    Returns:
        dict: JSON response from API containing account holder information
            On success, includes 'id', 'name', 'type', and other account details
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
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
    """List transactions for a specific account holder
    
    Retrieves a paginated list of transactions associated with an account holder.
    
    Parameters:
        account_holder_id: ID of the account holder whose transactions to retrieve
        limit: Maximum number of transactions to return (default: 10, max: 100)
        offset: Number of transactions to skip for pagination (default: 0)
        
    Returns:
        dict: JSON response from API containing transaction list
            On success, includes 'data' array of transactions and pagination information
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
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
    """Get details of a specific transaction
    
    Retrieves complete information for a single transaction by its ID.
    
    Parameters:
        transaction_id: ID of the transaction to retrieve (will be converted to string)
        
    Returns:
        dict: JSON response from API containing detailed transaction information
            On success, includes all transaction fields and enrichment data
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
    url = f"https://api.ntropy.com/v3/transactions/{transaction_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers)
    return handle_api_response(response)

@mcp.tool()
def bulk_enrich_transactions(transactions: List[Dict[str, Any]]) -> dict:
    """Enrich multiple transactions in a single API call
    
    Processes a batch of transactions for efficiency when dealing with multiple records.
    Each transaction must contain the same fields as required by the enrich_transaction tool.
    
    Parameters:
        transactions: List of transaction dictionaries, each containing:
            - id: Unique identifier (string or int, will be converted to string)
            - description: Transaction description
            - date: Transaction date (YYYY-MM-DD)
            - amount: Transaction amount
            - entry_type: 'credit' or 'debit'
            - currency: Three-letter currency code
            - account_holder_id: ID of the associated account holder
            - location: Optional dict with 'country' field
        
    Returns:
        dict: JSON response from API containing batch processing results
            On success, includes array of processed transactions with enrichment data
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
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
    """Delete an account holder and all associated data
    
    Permanently removes an account holder and all of their transactions from Ntropy.
    This action cannot be undone.
    
    Parameters:
        account_holder_id: ID of the account holder to delete (will be converted to string)
        
    Returns:
        dict: JSON response from API confirming deletion
            On success, includes confirmation message
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
    url = f"https://api.ntropy.com/v3/account_holders/{account_holder_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.delete(url, headers=headers)
    return handle_api_response(response)

@mcp.tool()
def delete_transaction(transaction_id: str | int) -> dict:
    """Delete a specific transaction
    
    Permanently removes a transaction from Ntropy.
    This action cannot be undone.
    
    Parameters:
        transaction_id: ID of the transaction to delete (will be converted to string)
        
    Returns:
        dict: JSON response from API confirming deletion
            On success, includes confirmation message
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
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
