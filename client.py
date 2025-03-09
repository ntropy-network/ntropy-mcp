import asyncio
import os
import json
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class NtropyMCPClient:
    """Client for testing the Ntropy MCP server"""
    
    def __init__(self):
        """Initialize the client"""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
    async def connect_to_server(self, server_command: str = "uvx", server_args: List[str] = None):
        """Connect to the Ntropy MCP server
        
        Args:
            server_command: Command to run the server (default: "uvx")
            server_args: Arguments for the server command
        """
        if server_args is None:
            server_args = []
            
        print(f"Connecting to server: {server_command} {' '.join(server_args)}")
        
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command=server_command,
            args=server_args,
            env=None
        )
        
        # Set up the connection
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        
        # Initialize the connection
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        
        print("\nAvailable tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        return tools
    
    async def call_tool(self, tool_name: str, **kwargs):
        """Call a tool on the server
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
        
        Returns:
            The result of the tool call
        """
        if not self.session:
            raise ValueError("Not connected to server. Call connect_to_server first.")
        
        print(f"\nCalling tool: {tool_name}")
        print(f"Arguments: {json.dumps(kwargs, indent=2)}")
        
        result = await self.session.call_tool(tool_name, kwargs)
        
        print("\nResult:")
        print(json.dumps(result.content, indent=2))
        
        return result.content
    
    async def check_connection(self):
        """Check connection to the Ntropy API"""
        return await self.call_tool("check_connection")
    
    async def create_account_holder(self, id: str, type: str, name: str):
        """Create an account holder"""
        return await self.call_tool("create_account_holder", id=id, type=type, name=name)
    
    async def enrich_transaction(self, id: str, description: str, date: str, 
                                amount: float, entry_type: str, currency: str,
                                account_holder_id: str, country: str = None):
        """Enrich a transaction"""
        args = {
            "id": id,
            "description": description,
            "date": date,
            "amount": amount,
            "entry_type": entry_type,
            "currency": currency,
            "account_holder_id": account_holder_id
        }
        
        if country:
            args["country"] = country
            
        return await self.call_tool("enrich_transaction", **args)
    
    async def list_transactions(self, account_holder_id: str, limit: int = 10, offset: int = 0):
        """List transactions for an account holder"""
        return await self.call_tool("list_transactions", 
                                   account_holder_id=account_holder_id,
                                   limit=limit, 
                                   offset=offset)
    
    async def bulk_enrich_transactions(self, transactions: List[Dict[str, Any]]):
        """Bulk enrich multiple transactions"""
        return await self.call_tool("bulk_enrich_transactions", transactions=transactions)
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def run_demo():
    """Run a demonstration of the Ntropy MCP client"""
    # Use API key from environment variable if available
    api_key = os.environ.get("NTROPY_API_KEY")
    
    # Default server configuration
    server_command = "uvx"
    server_args = ["ntropy-mcp"]
    
    # Add API key if available
    if api_key:
        server_args.extend(["--api-key", api_key])
    else:
        print("Warning: No NTROPY_API_KEY found in environment variables.")
        print("Please set this environment variable or add --api-key to the server arguments.")
    
    print("=== Ntropy MCP Client Demo ===")
    print(f"Server command: {server_command} {' '.join(server_args)}")
    
    client = NtropyMCPClient()
    
    try:
        # Connect to the server
        await client.connect_to_server(server_command, server_args)
        
        # Check connection to Ntropy API
        print("\n1. Checking connection to Ntropy API...")
        await client.check_connection()
        
        # Create an account holder
        print("\n2. Creating account holder...")
        account_holder = await client.create_account_holder(
            id="test_user_123",
            type="individual",
            name="Test User"
        )
        
        account_holder_id = account_holder.get("id", "test_user_123")
        
        # Enrich a single transaction
        print("\n3. Enriching a single transaction...")
        await client.enrich_transaction(
            id="tx_001",
            description="AMAZON.COM*MK1AB6TE1",
            date="2023-05-15",
            amount=-29.99,
            entry_type="debit",
            currency="USD",
            account_holder_id=account_holder_id,
            country="US"
        )
        
        # Enrich a batch of transactions
        print("\n4. Bulk enriching multiple transactions...")
        transactions = [
            {
                "id": "tx_002",
                "description": "NETFLIX.COM",
                "date": "2023-05-16",
                "amount": -13.99,
                "entry_type": "debit",
                "currency": "USD",
                "account_holder_id": account_holder_id
            },
            {
                "id": "tx_003",
                "description": "Starbucks Coffee",
                "date": "2023-05-17",
                "amount": -5.65,
                "entry_type": "debit",
                "currency": "USD",
                "account_holder_id": account_holder_id
            }
        ]
        
        await client.bulk_enrich_transactions(transactions)
        
        # List transactions for the account holder
        print("\n5. Listing transactions for account holder...")
        await client.list_transactions(account_holder_id)
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
    finally:
        # Clean up resources
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(run_demo()) 