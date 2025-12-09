# Cube.js MCP Server

A Model Context Protocol (MCP) server implementation for Cube.js, enabling seamless integration between AI assistants and Cube.js analytics platforms.

## Overview

This project provides a FastMCP-based server that exposes Cube.js analytics capabilities through the Model Context Protocol. It allows AI models and applications to:

- List available data cubes and their metadata
- Query data using natural language-friendly interfaces
- Access measures, dimensions, and segments from your Cube.js instance
- Execute complex analytics queries programmatically

## Features

- **Cube Listing**: Retrieve all available cubes with their measures, dimensions, and segments
- **Query Support**: Execute queries against Cube.js with flexible filtering and aggregation
- **Metadata Access**: Get detailed information about cube structure and relationships
- **Async Support**: Built on FastMCP for high-performance async operations
- **Error Handling**: Robust error handling with meaningful error messages
- **Token Authentication**: Secure API access with token-based authentication

## Prerequisites

- Python 3.8 or higher
- Cube.js instance running and accessible
- pip package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zsembek/Cube.js-MCP-server.git
cd Cube.js-MCP-server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your Cube.js configuration:
```bash
CUBEJS_API_BASE_URL=http://localhost:4000/cubejs-api/v1
CUBEJS_API_TOKEN=your_api_token_here
```

## Configuration

### Environment Variables

- `CUBEJS_API_BASE_URL`: The base URL of your Cube.js API (default: `http://localhost:4000/cubejs-api/v1`)
- `CUBEJS_API_TOKEN`: Authentication token for Cube.js API (required if your instance requires authentication)

### Claude Configuration

To use this MCP server with Claude or other compatible clients, add it to your configuration file (`~/.config/Claude/claude_desktop_config.json`):

```json
{
    "mcpServers": {
        "cubejs": {
            "command": "uvx",
            "args": [
                "--with",
                "cubejs-mcp-server @ git+https://github.com/zsembek/Cube.js-MCP-server.git",
                "python",
                "-m",
                "cubejs_mcp.server"
            ],
            "env": {
                "CUBEJS_API_BASE_URL": "http://localhost:4000/cubejs-api/v1",
                "CUBEJS_API_TOKEN": "your_api_token"
            }
        }
    }
}
```

## Usage

### Running the Server

```bash
python server.py
```

The server will start and be ready to accept MCP protocol requests.

### Available Tools

#### 1. `list_cubes()`
Retrieves the list of available cubes with their metadata.

**Returns**: A dictionary containing:
- Cube names and descriptions
- Available measures for each cube
- Available dimensions for each cube
- Available segments for each cube

**Example**:
```python
cubes = await list_cubes()
```

#### 2. `query_cube(cube_name, measures, dimensions, filters)`
Execute a query against a specific cube.

**Parameters**:
- `cube_name` (string): Name of the cube to query
- `measures` (list): List of measures to include in the query
- `dimensions` (list): List of dimensions to group by
- `filters` (optional, list): List of filter conditions

**Returns**: Query results with aggregated data

**Example**:
```python
result = await query_cube(
    cube_name="Orders",
    measures=["Orders.count", "Orders.total"],
    dimensions=["Orders.status"],
    filters=["Orders.created_date > 2024-01-01"]
)
```

## Project Structure

```
.
├── cubejs_mcp/
│   ├── __init__.py        # Package initialization
│   └── server.py          # MCP server implementation
├── server.py              # Legacy entry point (kept for compatibility)
├── config.json            # Configuration file for MCP clients
├── pyproject.toml         # Python package configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Dependencies

- **fastmcp**: FastMCP framework for building MCP servers
- **httpx**: Async HTTP client for making requests to Cube.js
- **python-dotenv**: Environment variable management

See `requirements.txt` for specific versions.

## Error Handling

The server includes comprehensive error handling for:
- Network connectivity issues
- Authentication failures
- Invalid cube or metric names
- API rate limiting
- Malformed queries

Error responses include descriptive messages to help diagnose issues.

## Security Considerations

- Always keep your `CUBEJS_API_TOKEN` secret and never commit it to version control
- Use `.env` files with proper permissions (600 or restricted access)
- Consider using environment variables managed by your deployment platform
- Ensure your Cube.js instance is properly secured behind authentication/firewall

## Development

### Setting up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Edit .env with your local Cube.js instance details
nano .env
```

### Running Tests

Tests can be added to verify functionality. Use pytest or unittest frameworks.

## Troubleshooting

### Connection Issues
- Verify `CUBEJS_API_BASE_URL` is correct and Cube.js is running
- Check network connectivity to the Cube.js instance
- Ensure firewall allows connections

### Authentication Errors
- Confirm `CUBEJS_API_TOKEN` is correct
- Check if your Cube.js instance requires authentication
- Verify token hasn't expired

### Query Errors
- Ensure cube names, measures, and dimensions are spelled correctly
- Check if filters are properly formatted
- Verify you have permission to access the requested cubes

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

## Resources

- [Cube.js Documentation](https://cube.dev/docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlopp/fastmcp)