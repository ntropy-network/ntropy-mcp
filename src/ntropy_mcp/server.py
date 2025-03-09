from mcp.server.fastmcp import FastMCP, Context
import requests
import os
import logging
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ntropy-mcp")

mcp = FastMCP(
    "MCP server for enriching banking data using the Ntropy API",
    dependencies=["requests"]
)

# Global API key
API_KEY = None

def handle_api_response(response, ctx: Optional[Context] = None):
    """Helper function to handle API responses and errors"""
    try:
        response.raise_for_status()
        if ctx:
            ctx.info(f"API request successful: {response.status_code}")
        return response.json()
    except requests.HTTPError as e:
        error_info = {}
        try:
            error_info = response.json()
        except:
            error_info = {"error": str(e)}
        
        error_message = f"API request failed: {str(e)}"
        if ctx:
            ctx.error(error_message)
        logger.error(error_message)
        
        return {
            "status": "error",
            "status_code": response.status_code,
            "message": error_message,
            "details": error_info
        }

def validate_api_key(api_key: str, ctx: Optional[Context] = None) -> bool:
    """Validate the API key by making a test request to the Ntropy API"""
    if not api_key:
        if ctx:
            ctx.error("API key is empty or invalid")
        return False
        
    headers = {"Accept": "application/json", "X-API-Key": api_key}
    try:
        # Make a simple request that doesn't create or modify anything
        response = requests.get("https://api.ntropy.com/v3/status", headers=headers)
        response.raise_for_status()
        if ctx:
            ctx.info("API key validated successfully")
        return True
    except Exception as e:
        if ctx:
            ctx.error(f"API key validation failed: {str(e)}")
        return False

@mcp.tool()
def check_connection(ctx: Context) -> dict:
    """Check the connection to the Ntropy API
    
    Verifies that the current API key is valid and the Ntropy API is accessible.
    
    Returns:
        dict: Connection status information
            On success, includes 'status', 'message', and API version details
            On failure, includes 'status', 'message', and error details
    """
    global API_KEY
    ctx.info("Checking connection to Ntropy API...")
    
    if not API_KEY:
        ctx.error("No API key is configured")
        return {
            "status": "error",
            "message": "No API key configured. Please set an API key first."
        }
    
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    try:
        response = requests.get("https://api.ntropy.com/v3/status", headers=headers)
        response_data = handle_api_response(response, ctx)
        
        if response.status_code == 200:
            ctx.info("Connection to Ntropy API successful")
            return {
                "status": "success",
                "message": "Connection to Ntropy API successful",
                "api_version": "v3",
                "details": response_data
            }
        else:
            ctx.error(f"Connection to Ntropy API failed: {response.status_code}")
            return {
                "status": "error",
                "message": f"Connection to Ntropy API failed: {response.status_code}",
                "details": response_data
            }
    except Exception as e:
        error_message = f"Error connecting to Ntropy API: {str(e)}"
        ctx.error(error_message)
        return {
            "status": "error",
            "message": error_message
        }

@mcp.tool()
def set_api_key(api_key: str, ctx: Context) -> dict:
    """Set or update the Ntropy API key
    
    Updates the API key used for Ntropy API requests and validates it.
    
    Parameters:
        api_key: The Ntropy API key to use for all API calls
        
    Returns:
        dict: Status of the API key update and validation
            On success, includes 'status' and 'message'
            On failure, includes 'status', 'message', and error details
    """
    global API_KEY
    ctx.info("Setting new API key...")
    
    if not api_key or len(api_key.strip()) == 0:
        ctx.error("API key cannot be empty")
        return {
            "status": "error",
            "message": "API key cannot be empty"
        }
    
    # Store the previous API key in case validation fails
    previous_api_key = API_KEY
    
    # Update the API key
    API_KEY = api_key.strip()
    
    # Validate the new API key
    if validate_api_key(API_KEY, ctx):
        ctx.info("API key updated and validated successfully")
        return {
            "status": "success",
            "message": "API key updated and validated successfully"
        }
    else:
        # Restore the previous API key if the new one is invalid
        API_KEY = previous_api_key
        ctx.error("Invalid API key. Reverting to previous key if available.")
        return {
            "status": "error",
            "message": "Invalid API key. The previous API key has been restored if available."
        }

@mcp.tool()
def create_account_holder(
    id: str | int,
    type: str,
    name: str,
    ctx: Context
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
    ctx.info(f"Creating account holder: {name} (ID: {id}, Type: {type})")
    
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
    return handle_api_response(response, ctx)

@mcp.tool()
def update_account_holder(
    id: str | int,
    name: Optional[str] = None,
    type: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """Update an existing account holder
    
    Updates an existing account holder's information such as name or type.
    
    Parameters:
        id: Unique identifier for the account holder to update
        name: New name for the account holder (optional)
        type: New type for the account holder - must be one of: 'individual', 'business' (optional)
        
    Returns:
        dict: JSON response from API containing the updated account holder information
            On success, includes 'id', 'name', 'type', and other account holder details
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
    ctx.info(f"Updating account holder ID: {id}")
    
    # First, get the current account holder data
    url = f"https://api.ntropy.com/v3/account_holders/{id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY,
    }
    
    get_response = requests.get(url, headers=headers)
    current_data = handle_api_response(get_response, ctx)
    
    # Check if we got valid data back
    if "status" in current_data and current_data["status"] == "error":
        ctx.error(f"Failed to retrieve account holder ID {id}")
        return current_data
    
    # Update the data with new values if provided
    update_data = {}
    if name is not None:
        update_data["name"] = name
        ctx.info(f"Updating name to: {name}")
    
    if type is not None:
        update_data["type"] = type
        ctx.info(f"Updating type to: {type}")
    
    # Only proceed if we have something to update
    if not update_data:
        ctx.warning("No update parameters provided")
        return {
            "status": "warning",
            "message": "No update parameters provided. Account holder remains unchanged.",
            "data": current_data
        }
    
    # Make the update request
    headers["Content-Type"] = "application/json"
    response = requests.patch(url, headers=headers, json=update_data)
    return handle_api_response(response, ctx)

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
    ctx: Context = None
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
    ctx.info(f"Enriching transaction: {description} (ID: {id})")
    
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
        ctx.info(f"Including country information: {country}")
        
    response = requests.post(url, headers=headers, json=data)
    return handle_api_response(response, ctx)

@mcp.tool()
def get_account_holder(account_holder_id: str | int, ctx: Context = None) -> dict:
    """Get details of an existing account holder
    
    Retrieves complete information for an account holder by their ID.
    
    Parameters:
        account_holder_id: ID of the account holder to retrieve (will be converted to string)
        
    Returns:
        dict: JSON response from API containing account holder information
            On success, includes 'id', 'name', 'type', and other account details
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
    ctx.info(f"Getting account holder details for ID: {account_holder_id}")
    
    url = f"https://api.ntropy.com/v3/account_holders/{account_holder_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers)
    return handle_api_response(response, ctx)

@mcp.tool()
def list_transactions(
    account_holder_id: str | int,
    limit: int = 10,
    offset: int = 0,
    ctx: Context = None
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
    ctx.info(f"Listing transactions for account holder ID: {account_holder_id} (limit: {limit}, offset: {offset})")
    
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
    return handle_api_response(response, ctx)

@mcp.tool()
def get_transaction(transaction_id: str | int, ctx: Context = None) -> dict:
    """Get details of a specific transaction
    
    Retrieves complete information for a single transaction by its ID.
    
    Parameters:
        transaction_id: ID of the transaction to retrieve (will be converted to string)
        
    Returns:
        dict: JSON response from API containing detailed transaction information
            On success, includes all transaction fields and enrichment data
            On failure, includes 'status', 'status_code', 'message', and 'details'
    """
    ctx.info(f"Getting transaction details for ID: {transaction_id}")
    
    url = f"https://api.ntropy.com/v3/transactions/{transaction_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers)
    return handle_api_response(response, ctx)

@mcp.tool()
def bulk_enrich_transactions(transactions: List[Dict[str, Any]], ctx: Context = None) -> dict:
    """Enrich multiple transactions in a single API call
    
    Processes a batch of transactions for efficiency when dealing with multiple records.
    Each transaction must contain the same fields as required by the enrich_transaction tool.
    This function reports progress as transactions are processed.
    
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
    transaction_count = len(transactions)
    ctx.info(f"Bulk enriching {transaction_count} transactions")
    
    # Report starting progress
    ctx.report_progress(0, transaction_count)
    
    url = "https://api.ntropy.com/v3/transactions/bulk"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    
    # Make sure all transaction IDs are strings
    for i, tx in enumerate(transactions):
        if i > 0 and i % 10 == 0:
            # Report progress for every 10 transactions processed
            ctx.report_progress(i, transaction_count)
            ctx.info(f"Preparing transaction {i}/{transaction_count}")
            
        if "id" in tx:
            tx["id"] = str(tx["id"])
        if "account_holder_id" in tx:
            tx["account_holder_id"] = str(tx["account_holder_id"])
    
    # Final progress update before API call
    ctx.report_progress(transaction_count - 1, transaction_count)
    ctx.info(f"Sending {transaction_count} transactions to Ntropy API")
    
    data = {"transactions": transactions}
    response = requests.post(url, headers=headers, json=data)
    result = handle_api_response(response, ctx)
    
    # Final progress update after API call
    ctx.report_progress(transaction_count, transaction_count)
    
    return result

@mcp.tool()
def delete_account_holder(account_holder_id: str | int, ctx: Context = None) -> dict:
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
    ctx.info(f"Deleting account holder ID: {account_holder_id}")
    ctx.warning("This operation will permanently delete the account holder and all associated data")
    
    url = f"https://api.ntropy.com/v3/account_holders/{account_holder_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.delete(url, headers=headers)
    return handle_api_response(response, ctx)

@mcp.tool()
def delete_transaction(transaction_id: str | int, ctx: Context = None) -> dict:
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
    ctx.info(f"Deleting transaction ID: {transaction_id}")
    ctx.warning("This operation will permanently delete the transaction")
    
    url = f"https://api.ntropy.com/v3/transactions/{transaction_id}"
    headers = {
        "Accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.delete(url, headers=headers)
    return handle_api_response(response, ctx)

def main(api_key: str):
    global API_KEY
    API_KEY = api_key
    
    # Validate API key
    if not API_KEY:
        logger.error("Ntropy API key is required")
        raise ValueError("Ntropy API key is required")
    
    # Basic API key validation
    if not validate_api_key(API_KEY):
        logger.error("Invalid Ntropy API key")
        raise ValueError("Invalid Ntropy API key. Please check your API key and try again.")
    
    logger.info("Starting Ntropy MCP server...")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Error running MCP server: {str(e)}")
        raise
