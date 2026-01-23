from typing import Any, Dict, List

from api import clean_slug, make_request
from mcp_instance import mcp


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
async def create_board(account_slug: str, name: str) -> Dict[str, Any]:
    """
    Create a new board in an account.

    Args:
        account_slug: The slug of the account
        name: The name of the new board
    """
    slug = clean_slug(account_slug)
    payload = {"board": {"name": name}}
    return await make_request("POST", f"{slug}/boards", json_data=payload)


@mcp.tool()
async def delete_board(account_slug: str, board_id: str) -> Dict[str, Any]:
    """
    Delete a specific board.

    Args:
        account_slug: The slug of the account
        board_id: The ID of the board to delete
    """
    slug = clean_slug(account_slug)
    endpoint = f"{slug}/boards/{board_id}"
    return await make_request("DELETE", endpoint)
