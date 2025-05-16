import os
from dotenv import load_dotenv
from message_mind.database_management import DatabaseManager
from langfuse.callback import CallbackHandler
from langfuse import Langfuse
from loguru import logger

from message_mind.workflow.graph import create_workflow_graph
from message_mind import utils

load_dotenv()


def setup_langfuse():
    """
    Set up Langfuse for tracking and monitoring.
    """
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST"),
    )
    try:
        langfuse.trace(name="test_trace")
        logger.info("Langfuse setup successful.")
    except Exception as e:
        logger.error(f"Langfuse connection failed: {e}")

    return CallbackHandler()


def convert_category(category: str) -> str:
    """
    Convert category to lowercase and replace hyphens with spaces
    """
    clean_category = category.lower().replace("-", " ")
    return clean_category


langfuse_handler = setup_langfuse()

database_manager = DatabaseManager(
    db_username=os.getenv("DB_USERNAME"),
    db_password=os.getenv("DB_PASSWORD"),
    db_uri=os.getenv("DB_URI"),
    app_name=os.getenv("DB_APP_NAME"),
)


graph = create_workflow_graph()

# Gather all messages that hasn't been categorised
inputs = database_manager.fetch_items(collection_name=os.getenv("DB_COLLECTION_NAME"))
logger.info(f"Fetched {len(inputs)} items requiring categorization from the database.")

thread = {"configurable": {"thread_id": "1"}, "callbacks": [langfuse_handler]}

for item in inputs:
    # Run the workflow graph to get category and summary of message
    result = graph.invoke({"input": utils.convert_objectids(item)}, config=thread)
    logger.info(f"Generated result: {result['final_response']}")

    # Prepare data for update
    update_data = {
        "category": convert_category(result["final_response"].category),
        "summary": result["final_response"].summary,
        "reasoning": result["final_response"].reasoning,
        "completed": False,
    }

    # Update database with result
    database_manager.update_item(
        collection_name=os.getenv("DB_COLLECTION_NAME"),
        item_id=result["input"]["_id"],
        update_data=update_data,
    )
    logger.info("Database updated successfully.")
