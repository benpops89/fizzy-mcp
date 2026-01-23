from typing import Any, Dict

from api import make_request
from mcp_instance import mcp


@mcp.tool()
async def get_user_identity() -> Dict[str, Any]:
    """
    Get the current user's identity and accessible accounts.
    Returns details about the authenticated user and a list of accounts they can access.
    """
    return await make_request("GET", "my/identity")
