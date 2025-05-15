import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from loguru import logger

from message_mind.database_management import DatabaseManager, MessageManager
from message_mind import utils

load_dotenv()

message_manager = MessageManager(
    client_session=os.getenv("USER_TELETHON_SESSION"),
    bot_session=os.getenv("BOT_TELETHON_SESSION"),
    api_id=os.getenv("TELEGRAM_CHAT_API_ID"),
    api_hash=os.getenv("TELEGRAM_CHAT_API_HASH"),
    bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
)


database_manager = DatabaseManager(
    db_username=os.getenv("DB_USERNAME"),
    db_password=os.getenv("DB_PASSWORD"),
    db_uri=os.getenv("DB_URI"),
    app_name=os.getenv("DB_APP_NAME"),
)

sgt_time = ZoneInfo("Asia/Singapore")


async def main():
    # Start both client and bot
    async with message_manager.client, message_manager.bot:
        await message_manager.start()

        start_date = utils.get_today_utc_date()
        logger.info(f"Start date: {start_date}")
        messages = await message_manager.get_new_messages(start_date=start_date)

        for message in messages:
            json_msg = await message_manager.extract_message(message)
            # str_msg = message_manager.json_to_str(json_msg)

            # Check if the message already exists in the database
            if not database_manager.check_message_exist(
                message=json_msg, collection_name=os.getenv("DB_COLLECTION_NAME")
            ):
                logger.info(f"Message: {json_msg}")

                # Save to database
                database_manager.save_to_database(
                    collection_name=os.getenv("DB_COLLECTION_NAME"),
                    message=json_msg,
                )

                # # Send message to the bot
                # await message_manager.client.send_message(
                #     os.getenv("BOT_NAME"),
                #     str_msg,
                #     parse_mode="markdown",
                # )


# Run the main function
try:
    message_manager.client.loop.run_until_complete(main())
finally:
    database_manager.close()  # Ensure MongoDB connection is closed
