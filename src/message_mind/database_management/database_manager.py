from dotenv import load_dotenv
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from pymongo.server_api import ServerApi
from loguru import logger


load_dotenv()


class DatabaseManager:
    def __init__(self, db_username: str, db_password: str, db_uri: str, app_name: str):
        self.app_name = app_name

        # Initialize the MongoDB client
        uri = f"mongodb+srv://{db_username}:{db_password}@{db_uri}/?retryWrites=true&w=majority&appName={self.app_name}"

        self.client = MongoClient(uri, server_api=ServerApi("1"))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command("ping")
            logger.info(
                "Pinged your deployment. You successfully connected to MongoDB!"
            )
        except Exception as e:
            logger.info(f"Error pinging MongoDB: {e}")

    def _setup_collection(self, collection_name: str) -> Collection:
        db = self.client[self.app_name]
        collection = db[collection_name]
        return collection

    def check_message_exist(self, message: dict, collection_name: str) -> bool:
        """
        Check if a message already exists in the database.

        Args:
            message (dict): The message to check.
            collection_name (str): The name of the collection.

        Returns:
            bool: True if the message exists, False otherwise.
        """
        collection = self._setup_collection(collection_name)

        # Define the criteria for a duplicate
        query = {
            "title": message.get("title"),
            "details": message.get("details"),
        }

        # Check if the document already exists
        if collection.find_one(query):
            return True
        return False

    def fetch_items(self, collection_name: str, start_date: datetime = None) -> list:
        """
        Fetch all items from the specified collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            list: A list of items in the collection.
        """
        collection = self._setup_collection(collection_name)

        if start_date:
            query = {"date_saved": {"$gte": start_date}}
            return list(collection.find(query))

        # If no start_date is provided, fetch all items
        return list(collection.find())

    def save_to_database(
        self,
        collection_name: str,
        message: dict,
    ) -> None:
        """
        Save a json message to the database

        Args:
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
            message (dict): The message to be saved in JSON format.

        """
        # Assuming you have a database and collection to save the data
        collection = self._setup_collection(collection_name)

        # Insert the document if it doesn't exist
        try:
            collection.insert_one(message)
        except Exception as e:
            logger.error(f"Error inserting document: {e}")

    def close(self):
        """
        Close the MongoDB client connection.
        """
        self.client.close()
