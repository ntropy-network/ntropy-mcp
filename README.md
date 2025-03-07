# Ntropy MCP server

MCP server for enriching banking data using the Ntropy API. This allows LLM agents that work with financial data to easily call any of the Ntropy API endpoints.

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

First, obtain your Ntropy API key by creating an account on [ntropy.com](https://ntropy.com). Make sure to replace `YOUR_NTROPY_API_KEY` below with your actual API key.

#### Run the server with uvx

```
uvx ntropy-mcp --api-key YOUR_NTROPY_API_KEY
```

#### Claude Desktop

The Claude Desktop configuration file is usually located at:

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Add the following to the configuration file if using uvx:

```json
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

and the following if using docker:

```json
"mcpServers": {
  "ntropy-mcp": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "ntropy-mcp"
      "--api-key",
      "YOUR_NTROPY_API_KEY"
    ]
  }
}
```

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```bash
npx @modelcontextprotocol/inspector uvx ntropy-mcp --api-key YOUR_NTROPY_API_KEY
```

## Build

Docker build:

```bash
docker build -t ntropy-mcp .
```

## Contributing

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements.

## License

ntropy-mcp is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
