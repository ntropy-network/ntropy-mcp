from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP(
    "MCP server for enriching banking data using the Ntropy API",
    dependencies=["requests"]
)

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
    return response.json()

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
        "location": {
            "country": country
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def main(api_key: str):
    global API_KEY
    API_KEY = api_key

    mcp.run()
