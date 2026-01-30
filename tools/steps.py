import asyncio
from typing import Any, Dict, List

import httpx
from api import clean_slug, create_client, make_request
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

    async with create_client() as client:
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


@mcp.tool()
async def delete_step(
    account_slug: str, card_number: int, step_id: int
) -> Dict[str, Any]:
    """
    Delete a specific step.

    Args:
        account_slug: The slug of the account
        card_number: The number of the card
        step_id: The ID of the step to delete
    """
    slug = clean_slug(account_slug)
    endpoint = f"{slug}/cards/{card_number}/steps/{step_id}"
    return await make_request("DELETE", endpoint)
