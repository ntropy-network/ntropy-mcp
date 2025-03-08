# Ntropy MCP server

MCP server for enriching banking data using the Ntropy API. This allows LLM agents that work with financial data to easily call any of the Ntropy API endpoints.

## Components

### Tools

The server implements the following tools to interact with the Ntropy API:

- **create_account_holder**: Create an account holder
  - Parameters: `id` (string/int), `type` (string), `name` (string)
  - Returns: The created account holder details

- **enrich_transaction**: Enrich a bank transaction
  - Parameters: `id` (string/int), `description` (string), `date` (string), `amount` (float), `entry_type` (string), `currency` (string), `account_holder_id` (string/int), `country` (string, optional)
  - Returns: The enriched transaction data

- **get_account_holder**: Get details of an account holder
  - Parameters: `account_holder_id` (string/int)
  - Returns: Account holder details

- **list_transactions**: List transactions for an account holder
  - Parameters: `account_holder_id` (string/int), `limit` (int, default=10), `offset` (int, default=0)
  - Returns: List of transactions

- **get_transaction**: Get details of a specific transaction
  - Parameters: `transaction_id` (string/int)
  - Returns: Transaction details

- **bulk_enrich_transactions**: Enrich multiple transactions at once
  - Parameters: `transactions` (List of transaction objects)
  - Returns: List of enriched transactions

- **delete_account_holder**: Delete an account holder and all associated data
  - Parameters: `account_holder_id` (string/int)
  - Returns: Deletion status

- **delete_transaction**: Delete a specific transaction
  - Parameters: `transaction_id` (string/int)
  - Returns: Deletion status

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
