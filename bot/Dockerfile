FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Copy all files from bot directory
COPY pyproject.toml ./
COPY bot.py ./
COPY config.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/

# Copy uv.lock (will be added by build context)
COPY uv.lock ./

# Sync dependencies using uv
RUN uv sync --frozen --no-dev

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot
CMD ["python", "bot.py"]
