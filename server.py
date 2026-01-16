import asyncio
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

    endpoint = f"{slug}/boards/{board_id}/cards"
    result = await make_request("POST", endpoint, json_data=payload)

    # Handle cases where the API returns headers only or empty body
    if not result:
        return {"status": "created", "message": "Card created successfully"}

    return result


@mcp.tool()
async def toggle_tags(
    account_slug: str, card_number: int, tags: List[str]
) -> Dict[str, Any]:
    """
    Toggle tags on a card.
    The API toggles tags: if present it removes, if absent it adds.

    Args:
        account_slug: The slug of the account
        card_number: The number of the card
        tags: List of tags to toggle
    """
    slug = clean_slug(account_slug)
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for tag in tags:
            tasks.append(
                make_request(
                    "POST",
                    f"{slug}/cards/{card_number}/taggings",
                    json_data={"tag_title": tag},
                    client=client
                )
            )
        
        await asyncio.gather(*tasks)

    return {"status": "success", "toggled_tags": tags}


@mcp.tool()
async def add_steps(
    account_slug: str, card_number: int, steps: List[str]
) -> Dict[str, Any]:
    """
    Add steps (todo items) to a card.

    Args:
        account_slug: The slug of the account
        card_number: The number of the card
        steps: List of step contents to add
    """
    slug = clean_slug(account_slug)

    async with httpx.AsyncClient() as client:
        tasks = []
        for step_content in steps:
            tasks.append(
                make_request(
                    "POST",
                    f"{slug}/cards/{card_number}/steps",
                    json_data={"step": {"content": step_content}},
                    client=client
                )
            )
        
        results = await asyncio.gather(*tasks)

    return {"status": "success", "created_steps": results}


if __name__ == "__main__":
    mcp.run()
