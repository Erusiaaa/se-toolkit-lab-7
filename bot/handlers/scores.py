async def handle_scores(args: dict | None = None, lms_client=None) -> str:
    lab = args.get("lab") if args else None
    if not lab:
        return "Usage: /scores <lab-name>\nExample: /scores lab-01"
    return f"📊 Scores for {lab}:\n\nNot implemented yet."
