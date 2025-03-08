# Ntropy MCP server

MCP server for enriching banking data using the Ntropy API. This allows LLM agents that work with financial data to easily call any of the Ntropy API endpoints.

## Components

### Tools

The server implements the following tools to interact with the Ntropy API:

- **check_connection**: Verify connection to the Ntropy API
  - Returns: Connection status information

- **set_api_key**: Set or update the Ntropy API key at runtime
  - Parameters: `api_key` (string)
  - Returns: Status of the API key update and validation

- **create_account_holder**: Create an account holder
  - Parameters: `id` (string/int), `type` (string), `name` (string)
  - Returns: The created account holder details

- **update_account_holder**: Update an existing account holder
  - Parameters: `id` (string/int), `name` (string, optional), `type` (string, optional)
  - Returns: The updated account holder details

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

## Example Usage

### Check Connection

```python
# Check if your API key is valid and the Ntropy API is accessible
connection_status = check_connection()
print(connection_status)
```

### Create and Update Account Holders

```python
# Create a new account holder
account_holder = create_account_holder(
    id="user123",
    type="individual",
    name="John Doe"
)

# Update an existing account holder
updated_account = update_account_holder(
    id="user123",
    name="John Smith"
)
```

### Enrich Transactions

```python
# Enrich a single transaction
enriched_transaction = enrich_transaction(
    id="tx123",
    description="AMAZON.COM*MK1AB6TE1",
    date="2023-05-15",
    amount=-29.99,
    entry_type="debit",
    currency="USD",
    account_holder_id="user123",
    country="US"
)

# Bulk enrich multiple transactions
transactions = [
    {
        "id": "tx124",
        "description": "NETFLIX.COM",
        "date": "2023-05-16",
        "amount": -13.99,
        "entry_type": "debit",
        "currency": "USD",
        "account_holder_id": "user123"
    },
    {
        "id": "tx125",
        "description": "Starbucks Coffee",
        "date": "2023-05-17",
        "amount": -5.65,
        "entry_type": "debit",
        "currency": "USD",
        "account_holder_id": "user123"
    }
]
enriched_transactions = bulk_enrich_transactions(transactions)
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
