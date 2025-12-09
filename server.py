import os
import httpx
from fastmcp import FastMCP, Context
from mcp.types import TextContent
from typing import Optional, Dict, Any, List
import json

# Initialize FastMCP server
mcp = FastMCP("cubejs")

# Configuration
CUBEJS_API_BASE_URL = os.getenv("CUBEJS_API_BASE_URL", "http://localhost:4000/cubejs-api/v1")
CUBEJS_API_TOKEN = os.getenv("CUBEJS_API_TOKEN", "")

def get_headers() -> Dict[str, str]:
    """Get headers for Cube.js API requests."""
    headers = {"Content-Type": "application/json"}
    if CUBEJS_API_TOKEN:
        headers["Authorization"] = CUBEJS_API_TOKEN
    return headers

async def make_request(method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Helper to make async requests to Cube.js API."""
    url = f"{CUBEJS_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=get_headers(),
                params=params,
                json=json_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Try to return the error message from Cube.js if available
            try:
                error_data = e.response.json()
                return {"error": error_data.get("error", str(e))}
            except:
                raise RuntimeError(f"API Request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Request failed: {str(e)}")

@mcp.tool()
async def list_cubes() -> TextContent:
    """
    Retrieves the list of available cubes, including their measures, dimensions, and segments.
    Returns the full metadata object from Cube.js.
    """
    result = await make_request("GET", "meta")
    return TextContent(type="text", text=json.dumps(result))

@mcp.tool()
async def execute_query(query: Dict[str, Any]) -> TextContent:
    """
    Executes a query against the Cube.js API and returns the results.
    
    Args:
        query: The Cube.js query object (JSON). Example:
               {
                 "measures": ["Stories.count"],
                 "dimensions": ["Stories.category"],
                 "timeDimensions": [{
                   "dimension": "Stories.time",
                   "dateRange": ["2015-01-01", "2015-12-31"],
                   "granularity": "month"
                 }]
               }
    """
    result = await make_request("GET", "load", params={"query": json.dumps(query)})
    return TextContent(type="text", text=json.dumps(result)) 

@mcp.tool()
async def execute_query_post(query: Dict[str, Any]) -> TextContent:
    """
    Executes a query against the Cube.js API using POST method (recommended for complex queries).
    
    Args:
        query: The Cube.js query object.
    """
    result = await make_request("POST", "load", json_data={"query": query})
    return TextContent(type="text", text=json.dumps(result))

@mcp.tool()
async def get_sql(query: Dict[str, Any]) -> TextContent:
    """
    Returns the generated SQL for a given query without executing it.
    
    Args:
        query: The Cube.js query object.
    """
    result = await make_request("GET", "sql", params={"query": json.dumps(query)})
    return TextContent(type="text", text=json.dumps(result))

@mcp.tool()
async def check_health() -> TextContent:
    """
    Checks the health status of the Cube.js server.
    """
    # readyz is usually at the root, not under /v1 base path
    # We need to adjust the URL construction for this specific call
    base_url_parts = CUBEJS_API_BASE_URL.split("/cubejs-api")
    root_url = base_url_parts[0] if base_url_parts else "http://localhost:4000"
    
    url = f"{root_url.rstrip('/')}/readyz"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                status = "OK"
            else:
                status = f"Unhealthy: {response.status_code}"
        except Exception as e:
            status = f"Unreachable: {str(e)}"

    return TextContent(type="text", text=status)

@mcp.resource("cube://meta")
async def get_meta_resource() -> str:
    """
    A resource that provides the full metadata of the Cube.js schema.
    """
    data = await make_request("GET", "meta")
    return json.dumps(data, indent=2)


@mcp.tool()
async def get_schema() -> TextContent:
    """Get the schema representation from Cube.js (GET /schema)."""
    data = await make_request("GET", "schema")
    return TextContent(type="text", text=json.dumps(data))


@mcp.tool()
async def refresh(query: Dict[str, Any]) -> TextContent:
    """Trigger a refresh for the given query (POST /refresh)."""
    data = await make_request("POST", "refresh", json_data={"query": query})
    return TextContent(type="text", text=json.dumps(data))


@mcp.tool()
async def refresh_pre_aggregations(payload: Dict[str, Any]) -> TextContent:
    """Refresh pre-aggregations (POST /pre-aggregations/refresh)."""
    data = await make_request("POST", "pre-aggregations/refresh", json_data=payload)
    return TextContent(type="text", text=json.dumps(data))


@mcp.tool()
async def scheduled_refresh(schedule: Dict[str, Any]) -> TextContent:
    """Trigger scheduled refresh (POST /refresh/schedule or similar)."""
    data = await make_request("POST", "refresh/schedule", json_data=schedule)
    return TextContent(type="text", text=json.dumps(data))


@mcp.tool()
async def raw_request(method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> TextContent:
    """
    Generic request tool to call arbitrary Cube.js REST endpoints.

    method: HTTP method name (GET, POST, PUT, DELETE)
    endpoint: API endpoint relative to base (e.g. "meta", "load", "sql", "schema")
    params: query string parameters
    json_data: JSON body for POST/PUT
    """
    method = method.upper()
    data = await make_request(method, endpoint, params=params, json_data=json_data)
    return TextContent(type="text", text=json.dumps(data))

def main():
    mcp.run()

if __name__ == "__main__":
    main()
