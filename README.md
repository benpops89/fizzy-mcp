# Fizzy MCP Server

This is a Model Context Protocol (MCP) server for the [Fizzy Kanban app](https://github.com/basecamp/fizzy). It allows LLMs to interact with Fizzy to list boards, view cards, and create new tasks.

## Features

- **Get Identity**: View current user and accessible accounts.
- **List Boards**: View all boards for an account.
- **List Cards**: View cards (tasks) in an account or specific board.
- **Create Card**: Create new tasks in a specific board.

## Installation & Usage with uv

This project is designed to be used with [uv](https://github.com/astral-sh/uv), a fast Python package installer and resolver.

1.  **Install uv** (if you haven't already):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Run the Server**:
    You can run the server directly with `uv`, which will automatically handle creating the virtual environment and installing dependencies:
    ```bash
    uv run server.py
    ```

## Configuration

You must set the `FIZZY_API_TOKEN` environment variable. If you are self-hosting Fizzy, you can also set `FIZZY_API_BASE_URL`.

```bash
export FIZZY_API_TOKEN="your_access_token_here"

# Optional: For self-hosted instances (defaults to https://app.fizzy.do)
export FIZZY_API_BASE_URL="https://fizzy.yourdomain.com"
```

To generate a token:
1. Go to your Fizzy profile.
2. Click on "Personal access tokens".
3. Click "Generate new access token".

## Tools

- `get_user_identity()`: Returns user identity and accounts.
- `list_boards(account_slug)`: Returns boards for an account.
- `list_cards(account_slug, board_id=None, limit=50)`: Returns cards.
- `get_card(account_slug, card_number)`: Returns a specific card.
- `create_card(account_slug, board_id, title, description=None, status='published')`: Creates a card.
