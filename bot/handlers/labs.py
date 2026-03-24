from services.lms_client import LmsClient

async def handle_labs(args: dict | None = None, lms_client: LmsClient | None = None) -> str:
    if lms_client is None:
        return "❌ LMS client not configured"
    try:
        items = await lms_client.get_items()
        labs = [item for item in items if item.get("type") == "lab"]
        if not labs:
            return "📚 No labs found."
        result = "📚 Available Labs:\n\n"
        for lab in labs:
            title = lab.get("title", "Unknown")
            result += f"• {title}\n"
        return result.strip()
    except Exception as e:
        return f"❌ Error fetching labs: {str(e)}"
