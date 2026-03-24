#!/usr/bin/env python3
import sys
import asyncio
from config import settings
from handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores
from services.lms_client import LmsClient
from services.llm_client import LLMClient

COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}

def parse_command(input_text: str):
    parts = input_text.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = None
    if len(parts) > 1 and command == "/scores":
        args = {"lab": parts[1]}
    return command, args

async def run_command(command: str, args=None):
    handler = COMMANDS.get(command)
    if not handler:
        return f"Unknown command: {command}. Use /help for available commands."
    lms_client = LmsClient(settings.lms_api_base_url, settings.lms_api_key)
    try:
        import inspect
        sig = inspect.signature(handler)
        if "lms_client" in sig.parameters:
            return await handler(args=args, lms_client=lms_client)
        return await handler(args=args)
    finally:
        await lms_client.close()

async def run_intent_router(user_message: str) -> str:
    from services.intent_router import IntentRouter
    llm_client = LLMClient(settings.llm_api_key, settings.llm_api_base_url, settings.llm_api_model)
    lms_client = LmsClient(settings.lms_api_base_url, settings.lms_api_key)
    router = IntentRouter(llm_client, lms_client)
    try:
        return await router.route(user_message)
    finally:
        await llm_client.close()
        await lms_client.close()

async def test_mode(input_text: str) -> int:
    command, args = parse_command(input_text)
    if command.startswith("/"):
        result = await run_command(command, args)
    else:
        result = await run_intent_router(input_text)
    print(result)
    return 0

async def telegram_mode() -> int:
    if not settings.bot_token:
        print("Error: BOT_TOKEN not set", file=sys.stderr)
        return 1
    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import Command
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    except ImportError:
        print("Error: aiogram not installed", file=sys.stderr)
        return 1
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        result = await run_command("/start")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏥 Health", callback_data="health"),
             InlineKeyboardButton(text="📚 Labs", callback_data="labs")],
            [InlineKeyboardButton(text="📊 Scores lab-01", callback_data="scores_lab-01"),
             InlineKeyboardButton(text="📊 Scores lab-04", callback_data="scores_lab-04")],
            [InlineKeyboardButton(text="👥 Top Learners", callback_data="top_learners")],
        ])
        await message.answer(result, reply_markup=keyboard)
    
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        result = await run_command("/help")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏥 Health", callback_data="health"),
             InlineKeyboardButton(text="📚 Labs", callback_data="labs")],
            [InlineKeyboardButton(text="📊 Scores", callback_data="scores_lab-01")],
        ])
        await message.answer(result, reply_markup=keyboard)
    
    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        await message.answer(await run_command("/health"))
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        await message.answer(await run_command("/labs"))
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        args = {"lab": message.text.split(maxsplit=1)[1]} if len(message.text.split()) > 1 else None
        await message.answer(await run_command("/scores", args))
    
    @dp.callback_query(lambda c: c.data)
    async def process_callback_query(callback_query: types.CallbackQuery):
        data = callback_query.data
        if data == "health":
            result = await run_command("/health")
        elif data == "labs":
            result = await run_command("/labs")
        elif data.startswith("scores_"):
            lab = data.replace("scores_", "")
            result = await run_command("/scores", {"lab": lab})
        elif data == "top_learners":
            result = await run_intent_router("who are the top 5 students in lab-01")
        else:
            result = "Unknown action"
        await callback_query.message.answer(result)
        await callback_query.answer()
    
    @dp.message()
    async def handle_message(message: types.Message):
        result = await run_intent_router(message.text)
        await message.answer(result)
    
    print("Bot started...")
    await dp.start_polling(bot)
    return 0

async def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test \"/command\"", file=sys.stderr)
            return 1
        return await test_mode(sys.argv[2])
    return await telegram_mode()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
