from typing import Any, Dict, List, Optional

from api import clean_slug, make_request
from mcp_instance import mcp


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
async def update_card(
    account_slug: str,
    card_number: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update a card's details.

    Args:
        account_slug: The slug of the account
        card_number: The number of the card to update
        title: Optional new title
        description: Optional new description
        status: Optional new status
    """
    slug = clean_slug(account_slug)

    card_data = {}
    if title:
        card_data["title"] = title
    if description:
        card_data["description"] = description
    if status:
        card_data["status"] = status

    if not card_data:
        raise ValueError(
            "At least one field (title, description, status) must be provided to update"
        )

    payload = {"card": card_data}
    endpoint = f"{slug}/cards/{card_number}"

    return await make_request("PUT", endpoint, json_data=payload)


@mcp.tool()
async def delete_card(account_slug: str, card_number: int) -> Dict[str, Any]:
    """
    Archive (delete) a specific card.

    Args:
        account_slug: The slug of the account
        card_number: The number of the card to archive
    """
    slug = clean_slug(account_slug)
    endpoint = f"{slug}/cards/{card_number}"
    return await make_request("DELETE", endpoint)
