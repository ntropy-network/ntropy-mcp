# Ntropy MCP server

MCP server for enriching banking data using the Ntropy API

## Components

### Tools

The server implements two tools:
- create_account_holder: Create an account holder using the Ntropy API
  - Takes "id", "type", "name" as required string arguments
  - Returns the created account holder
- enrich_transaction: Enrich a transaction using the Ntropy API
  - Takes "id", "description", "date", "amount", "entry_type", "currency",
  "account_holder_id" as required string arguments, and "country" as an optional
  argument
  - Returns the enriched transaction

## Quickstart

### Install

First, obtain your Ntropy API key by creating an account on [ntropy.com](https://ntropy.com). Make sure to replace `YOUR_NTROPY_API_KEY` below with your actual api key.

#### Run the server with uvx

```
uvx run ntropy-mcp --api-key YOUR_NTROPY_API_KEY
```

#### Claude Desktop

The Claude Desktop configuration file is usually located at:

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Add the following to the configuration file:

```
  "mcpServers": {
    "ntropy-mcp": {
      "command": "uvx",
      "args": [
        "ntropy-mcp",
        "--api-key",
        "YOUR_NTROPY_API_KEY"
      ]
    }
  }
 ```
