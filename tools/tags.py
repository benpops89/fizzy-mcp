import asyncio
from typing import Any, Dict, List

import httpx
from api import clean_slug, make_request
from mcp_instance import mcp


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
                    client=client,
                )
            )

        await asyncio.gather(*tasks)

    return {"status": "success", "toggled_tags": tags}
