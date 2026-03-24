from services.lms_client import LmsClient

async def handle_labs(args: dict | None = None, lms_client: LmsClient | None = None) -> str:
    if lms_client is None:
        return "❌ LMS client not configured"
    items = await lms_client.get_items()
    labs = [item for item in items if item.get("type") == "lab"]
    if labs:
        result = "📚 Available Labs:\n\n"
        for lab in labs:
            result += f"• {lab['title']}\n"
        return result
    return "No labs found."
