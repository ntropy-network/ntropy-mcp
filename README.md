# ntropy-mcp MCP server

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

First, obtain an Ntropy API key by creating an account on ntropy.com.

#### Run the server with uvx

```
uvx run ntropy-mcp --api-key YOUR_NTROPY_API_KEY
```

#### Claude Desktop

The Claude Desktop configuration file is usually located at:

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Add the following to the configuration file:

<details>
  <summary>Published Servers Configuration</summary>
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
</details>
