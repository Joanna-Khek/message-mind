import os
from datetime import datetime, time
from zoneinfo import ZoneInfo
from bson import ObjectId
from typing import List
from telegram import Bot


def get_today_utc_date():
    """
    Get the current time in Singapore timezone.
    """
    utc_time = ZoneInfo("UTC")
    today = datetime.now(utc_time).date()
    date = datetime.combine(today, time(0, 0), tzinfo=utc_time)
    return date


def convert_objectids(obj):
    """
    Convert ObjectId instances in a dictionary or list to strings.
    """
    if isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(v) for v in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj


async def notify_telegram(result: dict, cost: float) -> None:
    """
    Notify a Telegram channel with the result of the workflow.

    Args:
        result (dict): The result of the workflow containing the message details.
        cost (float): The cost of the message processing.
    """
    bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))

    text = (
        f"Title: {result['input']['details']}\n"
        f"Category: {result['final_response'].category}\n"
        f"Summary: {result['final_response'].summary}\n"
        f"Cost: ${cost:.2f}"
    )

    async with bot:
        await bot.send_message(
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            text=text,
            parse_mode="markdown",
        )


def calculate_cost(
    ai_messages: List[dict], input_tokens_cost: float, output_tokens_cost: float
) -> float:
    """
    Calculate the cost of a message based on its metadata and token usage.

    Args:
        ai_messages (List[dict]): List of AI messages with metadata.
        input_tokens_cost (float): Cost per million input tokens.
        output_tokens_cost (float): Cost per million output tokens.

    Returns:
        float: Total cost of the messages.
    """
    total_cost = 0

    for msg in ai_messages:
        # Extract the number of tokens from the metadata
        input_tokens = msg.usage_metadata.get("input_tokens", 0)
        output_tokens = msg.usage_metadata.get("output_tokens", 0)

        # Calculate the cost based on the number of tokens
        cost = ((input_tokens_cost / 1000000) * input_tokens) + (
            (output_tokens_cost / 1000000) * output_tokens
        )
        total_cost += cost

    return total_cost
