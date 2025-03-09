import asyncio
import os
import sys
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
        
    async def connect_to_server(self, server_command: str, server_args: List[str] = None):
        """Connect to the Ntropy MCP server
        
        Args:
            server_command: Command to run the server (e.g., "python", "uvx")
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

async def demo():
    """Run a demonstration of the Ntropy MCP client"""
    # Use API key from environment variable if available
    api_key = os.environ.get("NTROPY_API_KEY")
    
    if len(sys.argv) > 1:
        server_command = sys.argv[1]
        server_args = sys.argv[2:]
    else:
        # Default to uvx for running the server
        server_command = "uvx"
        server_args = ["ntropy-mcp"]
        
        # Add API key if available and not already in args
        if api_key and "--api-key" not in server_args:
            server_args.extend(["--api-key", api_key])
    
    client = NtropyMCPClient()
    
    try:
        # Connect to the server
        await client.connect_to_server(server_command, server_args)
        
        # Check connection to Ntropy API
        await client.check_connection()
        
        # Create an account holder
        account_holder = await client.create_account_holder(
            id="test_user_123",
            type="individual",
            name="Test User"
        )
        
        account_holder_id = account_holder.get("id", "test_user_123")
        
        # Enrich a single transaction
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
        await client.list_transactions(account_holder_id)
        
    finally:
        # Clean up resources
        await client.cleanup()

async def interactive():
    """Run an interactive session with the Ntropy MCP client"""
    # Use API key from environment variable if available
    api_key = os.environ.get("NTROPY_API_KEY")
    
    if len(sys.argv) > 1:
        server_command = sys.argv[1]
        server_args = sys.argv[2:]
    else:
        # Default to uvx for running the server
        server_command = "uvx"
        server_args = ["ntropy-mcp"]
        
        # Add API key if available and not already in args
        if api_key and "--api-key" not in server_args:
            server_args.extend(["--api-key", api_key])
    
    client = NtropyMCPClient()
    
    try:
        # Connect to the server
        tools = await client.connect_to_server(server_command, server_args)
        tool_names = [tool.name for tool in tools]
        
        print("\nNtropy MCP Interactive Client")
        print("Type 'exit' to quit, or 'help' to see available commands")
        
        while True:
            command = input("\nCommand: ").strip()
            
            if command.lower() in ['exit', 'quit']:
                break
                
            if command.lower() == 'help':
                print("\nAvailable commands:")
                print("- tool <tool_name> <json_args>: Call a tool with JSON arguments")
                print("- check: Check connection to Ntropy API")
                print("- create_account <id> <type> <name>: Create an account holder")
                print("- list_tools: List available tools")
                print("- exit: Exit the client")
                continue
                
            if command.lower() == 'list_tools':
                print("\nAvailable tools:", ", ".join(tool_names))
                continue
                
            if command.lower() == 'check':
                await client.check_connection()
                continue
                
            if command.startswith('create_account '):
                parts = command.split(' ', 3)
                if len(parts) != 4:
                    print("Usage: create_account <id> <type> <name>")
                    continue
                    
                _, acct_id, acct_type, acct_name = parts
                await client.create_account_holder(acct_id, acct_type, acct_name)
                continue
                
            if command.startswith('tool '):
                parts = command.split(' ', 2)
                if len(parts) < 2:
                    print("Usage: tool <tool_name> <json_args>")
                    continue
                    
                _, tool_name = parts[0:2]
                args_json = parts[2] if len(parts) > 2 else "{}"
                
                if tool_name not in tool_names:
                    print(f"Unknown tool: {tool_name}")
                    print(f"Available tools: {', '.join(tool_names)}")
                    continue
                    
                try:
                    args = json.loads(args_json)
                    await client.call_tool(tool_name, **args)
                except json.JSONDecodeError:
                    print(f"Invalid JSON arguments: {args_json}")
                    continue
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' to see available commands")
    
    finally:
        # Clean up resources
        await client.cleanup()

if __name__ == "__main__":
    # Run the interactive client by default, or demo with demo arg
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        sys.argv.pop(1)  # Remove the "demo" argument
        asyncio.run(demo())
    else:
        asyncio.run(interactive()) 