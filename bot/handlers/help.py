async def handle_help(args: dict | None = None) -> str:
    return """📚 LMS Bot Commands:

/start - Welcome message
/help - Show this help message
/health - Check backend status and item count
/labs - List all available labs
/scores <lab> - Show pass rates for a specific lab
       Example: /scores lab-01

You can also ask questions in plain language (coming soon)!"""
