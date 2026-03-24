#!/usr/bin/env python3
"""
LMS Telegram Bot - Entry point with --test mode support.

Usage:
    uv run bot.py              # Run as Telegram bot
    uv run bot.py --test "/start"  # Test mode (no Telegram connection)
"""

import sys
import asyncio
from typing import Any

from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from services.lms_client import LmsClient


# Command routing
COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def parse_command(input_text: str) -> tuple[str, dict | None]:
    """Parse command and extract arguments."""
    parts = input_text.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = None
    if len(parts) > 1:
        # Extract lab name for /scores command
        if command == "/scores":
            args = {"lab": parts[1]}
    return command, args


async def run_command(command: str, args: dict | None = None) -> str:
    """Execute a command and return the response."""
    handler = COMMANDS.get(command)
    if not handler:
        return f"❌ Unknown command: {command}\nUse /help for available commands."
    
    # Create LMS client for handlers that need it
    lms_client = LmsClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key
    )
    
    try:
        # Call handler with lms_client if it accepts it
        import inspect
        sig = inspect.signature(handler)
        if "lms_client" in sig.parameters:
            result = await handler(args=args, lms_client=lms_client)
        else:
            result = await handler(args=args)
        return result
    finally:
        await lms_client.close()


async def test_mode(input_text: str) -> int:
    """Run in test mode - execute command and print result to stdout."""
    command, args = parse_command(input_text)
    result = await run_command(command, args)
    print(result)
    return 0


async def telegram_mode() -> int:
    """Run as Telegram bot using aiogram."""
    if not settings.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret", file=sys.stderr)
        return 1
    
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync", file=sys.stderr)
        return 1
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        result = await run_command("/start")
        await message.answer(result)
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        result = await run_command("/help")
        await message.answer(result)
    
    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        result = await run_command("/health")
        await message.answer(result)
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        result = await run_command("/labs")
        await message.answer(result)
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        args = {"lab": message.text.split(maxsplit=1)[1]} if len(message.text.split()) > 1 else None
        result = await run_command("/scores", args)
        await message.answer(result)
    
    print(f"Bot started. Polling for updates...")
    await dp.start_polling(bot)
    return 0


async def main() -> int:
    """Main entry point."""
    # Check for --test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test \"/command [args]\"", file=sys.stderr)
            return 1
        input_text = sys.argv[2]
        return await test_mode(input_text)
    
    # Run as Telegram bot
    return await telegram_mode()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
