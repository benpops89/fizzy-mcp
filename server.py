# Import tools to ensure they are registered with the MCP instance
import tools.boards
import tools.cards
import tools.identity
import tools.steps
import tools.tags
from mcp_instance import mcp

if __name__ == "__main__":
    mcp.run()
