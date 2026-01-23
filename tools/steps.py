import asyncio
from typing import Any, Dict, List

import httpx
from api import clean_slug, make_request
from mcp_instance import mcp


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
                    client=client,
                )
            )

        results = await asyncio.gather(*tasks)

    return {"status": "success", "created_steps": results}
