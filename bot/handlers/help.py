async def handle_help(args: dict | None = None) -> str:
    return """📚 LMS Bot Commands:

/start - Welcome message
/help - Show this help
/health - Check backend status
/labs - List available labs
/scores <lab> - Show task pass rates"""
