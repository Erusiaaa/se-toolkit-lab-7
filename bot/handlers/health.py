from services.lms_client import LmsClient

async def handle_health(args: dict | None = None, lms_client: LmsClient | None = None) -> str:
    if lms_client is None:
        return "❌ LMS client not configured"
    result = await lms_client.get_health()
    if result.get("healthy"):
        count = result.get("item_count", 0)
        return f"✅ Backend is healthy. {count} items available."
    else:
        error = result.get("error", "Unknown error")
        return f"❌ Backend error: {error}. Check that the services are running."
