from services.lms_client import LmsClient

async def handle_scores(args: dict | None = None, lms_client: LmsClient | None = None) -> str:
    if lms_client is None:
        return "❌ LMS client not configured"
    lab = args.get("lab") if args else None
    if not lab:
        return "Usage: /scores <lab-name>\nExample: /scores lab-01"
    try:
        pass_rates = await lms_client.get_pass_rates(lab)
        if not pass_rates:
            return f"📊 No pass rate data found for {lab}."
        result = f"📊 Pass rates for {lab}:\n\n"
        for rate in pass_rates:
            task_name = rate.get("task_name", rate.get("task", "Unknown"))
            pass_rate = rate.get("pass_rate", rate.get("average_score", 0))
            attempts = rate.get("attempts", 0)
            result += f"• {task_name}: {pass_rate:.1f}% ({attempts} attempts)\n"
        return result.strip()
    except Exception as e:
        return f"❌ Error fetching scores: {str(e)}"
