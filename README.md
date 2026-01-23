# Fizzy MCP Server

This is a Model Context Protocol (MCP) server for the [Fizzy Kanban app](https://github.com/basecamp/fizzy). It allows LLMs to interact with Fizzy to manage boards, cards, tags, and steps.

## Features

- **Identity**: View current user and accessible accounts.
- **Boards**: Create, list, and delete boards.
- **Cards**: List, view, create, update, and delete cards (tasks).
- **Details**: Manage tags and steps (todo items) on cards.

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

You must set the `FIZZY_API_TOKEN` and `FIZZY_API_BASE_URL` environment variables.

```bash
export FIZZY_API_TOKEN="your_access_token_here"
export FIZZY_API_BASE_URL="https://fizzy.yourdomain.com"
```

To generate a token:
1. Go to your Fizzy profile.
2. Click on "Personal access tokens".
3. Click "Generate new access token".

## Available Tools

- **`get_user_identity`**
  Get the current user's identity and accessible accounts.

- **`list_boards`**
  List all boards for a specific account.
  - `account_slug`: The slug of the account.

- **`create_board`**
  Create a new board in an account.
  - `account_slug`: The slug of the account.
  - `name`: The name of the new board.

- **`delete_board`**
  Delete a specific board.
  - `account_slug`: The slug of the account.
  - `board_id`: The ID of the board to delete.

- **`list_cards`**
  List cards for an account, optionally filtered by board.
  - `account_slug`: The slug of the account.
  - `board_id`: (Optional) Filter by specific board ID.
  - `limit`: (Optional) Max cards to return (default 50).

- **`get_card`**
  Get details for a specific card.
  - `account_slug`: The slug of the account.
  - `card_number`: The unique number of the card.

- **`create_card`**
  Create a new card in a specific board.
  - `account_slug`: The slug of the account.
  - `board_id`: The ID of the board.
  - `title`: Card title.
  - `description`: (Optional) Rich text description.
  - `status`: (Optional) 'published' (default) or 'drafted'.

- **`update_card`**
  Update a card's details.
  - `account_slug`: The slug of the account.
  - `card_number`: The card number.
  - `title`: (Optional) New title.
  - `description`: (Optional) New description.
  - `status`: (Optional) New status.

- **`delete_card`**
  Archive (delete) a specific card.
  - `account_slug`: The slug of the account.
  - `card_number`: The card number.

- **`toggle_tags`**
  Toggle tags on a card (add if missing, remove if present).
  - `account_slug`: The slug of the account.
  - `card_number`: The card number.
  - `tags`: List of tag strings.

- **`add_steps`**
  Add todo steps to a card.
  - `account_slug`: The slug of the account.
  - `card_number`: The card number.
  - `steps`: List of step content strings.
