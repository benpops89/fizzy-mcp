import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("fizzy")

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
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
) -> Any:
    """Make a request to the Fizzy API."""
    headers = get_headers()
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    # Debug print to stderr (visible in MCP logs)
    print(f"Requesting: {url}", file=sys.stderr)

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method, url, headers=headers, params=params, json=json_data
        )

        if response.status_code == 401:
            raise ValueError("Unauthorized: Invalid API token")

        response.raise_for_status()

        if response.status_code == 204:
            return None

        return response.json()


@mcp.tool()
async def get_user_identity() -> Dict[str, Any]:
    """
    Get the current user's identity and accessible accounts.
    Returns details about the authenticated user and a list of accounts they can access.
    """
    return await make_request("GET", "my/identity")


@mcp.tool()
async def list_boards(account_slug: str) -> List[Dict[str, Any]]:
    """
    List all boards for a specific account.

    Args:
        account_slug: The slug of the account (e.g., "897362094")
    """
    slug = clean_slug(account_slug)
    return await make_request("GET", f"{slug}/boards")


@mcp.tool()
async def list_cards(
    account_slug: str, board_id: Optional[str] = None, limit: int = 50
) -> List[Dict[str, Any]]:
    """
    List cards for an account, optionally filtered by board.

    Args:
        account_slug: The slug of the account
        board_id: Optional ID of a specific board to filter by
        limit: Maximum number of cards to return (default 50)
    """
    slug = clean_slug(account_slug)
    params = {}
    if board_id:
        params["board_ids[]"] = board_id

    # Note: API does not strictly specify a 'limit' param in docs,
    # but uses pagination. We'll just return the first page for now.
    # If the API supported per_page, we'd use it.

    return await make_request("GET", f"{slug}/cards", params=params)


@mcp.tool()
async def get_card(account_slug: str, card_number: int) -> Dict[str, Any]:
    """
    Get a specific card by its number.

    Args:
        account_slug: The slug of the account
        card_number: The number of the card to retrieve
    """
    slug = clean_slug(account_slug)
    return await make_request("GET", f"{slug}/cards/{card_number}")


@mcp.tool()
async def create_card(
    account_slug: str,
    board_id: str,
    title: str,
    description: Optional[str] = None,
    status: str = "published",
) -> Dict[str, Any]:
    """
    Create a new card (task) in a specific board.

    Args:
        account_slug: The slug of the account
        board_id: The ID of the board to create the card in
        title: The title of the card
        description: Optional rich text description
        status: Initial status ('published' or 'drafted', default: 'published')
    """
    slug = clean_slug(account_slug)

    payload = {"card": {"title": title, "status": status}}

    if description:
        payload["card"]["description"] = description

    # The API returns 201 Created and a Location header, but often body too?
    # Docs say "Returns 201 Created with a Location header pointing to the new card."
    # Let's assume it might return the card body or we might need to fetch it.
    # Our make_request helper returns JSON if available.

    # Note: make_request raises on non-2xx.

    endpoint = f"{slug}/boards/{board_id}/cards"
    result = await make_request("POST", endpoint, json_data=payload)

    # If result is empty (some APIs just return headers), we might want to return a success message.
    if not result:
        return {"status": "created", "message": "Card created successfully"}

    return result


if __name__ == "__main__":
    mcp.run()
