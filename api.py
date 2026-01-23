import os
import sys
from typing import Any, Dict, Optional

import httpx

# Constants
API_BASE_URL = os.environ.get("FIZZY_API_BASE_URL")
API_TOKEN = os.environ.get("FIZZY_API_TOKEN")


def get_headers() -> Dict[str, str]:
    """Get the headers for API requests."""
    if not API_TOKEN:
        raise ValueError("FIZZY_API_TOKEN environment variable is not set")
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "fizzy-mcp/0.1.0",
    }


def clean_slug(slug: str) -> str:
    """Ensure slug does not have a leading slash."""
    return slug.lstrip("/")


async def make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Any:
    """Make a request to the Fizzy API."""
    if not API_BASE_URL:
        raise ValueError("FIZZY_API_BASE_URL environment variable is not set")

    headers = get_headers()
    # Ensure correct slash handling
    url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    # Debug print to stderr (visible in MCP logs)
    print(f"Requesting: {url}", file=sys.stderr)

    should_close = False
    if client is None:
        client = httpx.AsyncClient()
        should_close = True

    try:
        response = await client.request(
            method, url, headers=headers, params=params, json=json_data
        )

        if response.status_code == 401:
            raise ValueError("Unauthorized: Invalid API token")

        response.raise_for_status()

        if response.status_code == 204:
            return {"status": "success", "code": 204}

        if response.status_code == 201:
            content = response.content.strip()
            if not content:
                return {
                    "status": "created",
                    "location": response.headers.get("Location"),
                }
            try:
                return response.json()
            except Exception:
                return {
                    "status": "created",
                    "location": response.headers.get("Location"),
                }

        return response.json()

    finally:
        if should_close:
            await client.aclose()
