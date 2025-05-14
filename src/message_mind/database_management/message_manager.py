from typing import List
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from zoneinfo import ZoneInfo


class MessageManager:
    def __init__(
        self,
        client_session: str,
        bot_session: str,
        api_id: str,
        api_hash: str,
        bot_token: str,
    ):
        self.client = TelegramClient(
            session=client_session,
            api_id=api_id,
            api_hash=api_hash,
        )

        self.bot = TelegramClient(
            session=bot_session,
            api_id=api_id,
            api_hash=api_hash,
        )

        self.bot_token = bot_token
        self.timezone = ZoneInfo("Asia/Singapore")

    async def start(self):
        """
        Start both the client and bot asynchronously.
        """
        await self.client.start()
        await self.bot.start(bot_token=self.bot_token)

    async def get_new_messages(self, start_date: datetime) -> List:
        """
        Get new messages from the Telegram client beginning from a specific date.
        This method uses the Telethon library to fetch messages from the user's own account.

        Args:
            start_date (datetime): The date from which to start fetching messages.

        Returns:
            List: A list of new messages.
        """
        new_messages = []
        async for message in self.client.iter_messages("me"):
            if message.date >= start_date:
                new_messages.append(message)
            else:
                break
        return new_messages

    def check_photo_image(self, message: object) -> bool:
        """
        Check if the message contains a photo or image.

        Args:
            message (object): The message object to check.

        Returns:
            bool: True if the message contains a photo or image, False otherwise.
        """
        return isinstance(message.media, MessageMediaPhoto)

    async def extract_message(self, message: object) -> str:
        """
        Extract the message content from the message object.

        Args:
            message (object): The message object to format.

        Returns:
            str: The formatted message.
            {
                "date_saved": "2023-10-01 12:00:00 +08",
                "date_detail": "2023-10-01 12:00:00 +08",
                "details": "Hello World",
                "title": "Message Title",
                "description": "Message Description"
            }
        """

        message_doc = {
            "date_saved": datetime.now(self.timezone),
            "date_detail": message.date.astimezone(self.timezone),
            "details": message.message,
        }

        if message.media and getattr(message.media, "webpage", None):
            webpage = message.media.webpage

            title = getattr(webpage, "title", None)
            description = getattr(webpage, "description", None)

            if title:
                message_doc["title"] = title

            if description:
                message_doc["description"] = description

        # As the image binary is too long, LLM cost will
        # be very high, so for now we will not save the
        # image binary
        if self.check_photo_image(message):
            # image_buffer = BytesIO()
            # await self.client.download_media(message, file=image_buffer)
            # image_buffer.seek(0)
            # message_doc["image"] = Binary(image_buffer.getvalue())

            raise ValueError("Message cannot contain a photo or image.")
        return message_doc

    def json_to_str(self, message_doc: dict) -> str:
        """
        Take the json message and format it into a string for sending to the bot.

        Args:
            message_doc (dict): The message document to format.

        Returns:
            str: The formatted message as a JSON string.
        """
        msg_to_send = f"""**Date:** {message_doc["date_detail"]}\n**Message:** {message_doc["details"]}"""

        if message_doc.get("title"):
            msg_to_send += f"\n**Title:** {message_doc['title']}"
        if message_doc.get("description"):
            msg_to_send += f"\n**Description:** {message_doc['description']}"
        if message_doc.get("image"):
            msg_to_send += "\n**Image:** [Saved to database]"
        return msg_to_send
