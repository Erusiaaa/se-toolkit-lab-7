from services.lms_client import LmsClient

async def handle_health(args: dict | None = None, lms_client: LmsClient | None = None) -> str:
    if lms_client is None:
        return "❌ LMS client not configured"
    is_healthy = await lms_client.get_health()
    if is_healthy:
        return "✅ Backend is healthy!"
    return "⚠️ Backend is not responding"
