import os
import asyncio
from dotenv import load_dotenv
from message_mind.database_management import DatabaseManager
from langfuse.callback import CallbackHandler
from langfuse import Langfuse
from loguru import logger
from langchain_core.messages import AIMessage
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


async def main():
    graph = create_workflow_graph()

    # Gather all messages that hasn't been categorised
    inputs = database_manager.fetch_items(
        collection_name=os.getenv("DB_COLLECTION_NAME")
    )

    unique_categories = database_manager.get_unique_categories(
        collection_name=os.getenv("DB_COLLECTION_NAME")
    )

    logger.info(
        f"Fetched {len(inputs)} items requiring categorization from the database."
    )
    logger.info(f"unique_categories: {unique_categories}")

    thread = {"configurable": {"thread_id": "1"}, "callbacks": [langfuse_handler]}

    for item in inputs:
        # Run the workflow graph to get category and summary of message
        result = graph.invoke(
            {
                "input": utils.convert_objectids(item),
                "unique_categories": unique_categories,
            },
            config=thread,
        )
        logger.info(f"Generated result: {result['final_response']}")

        # Compute cost
        cost = utils.calculate_cost(
            ai_messages=[
                msg for msg in result["messages"] if isinstance(msg, AIMessage)
            ],
            input_tokens_cost=float(os.getenv("INPUT_TOKENS_COST")),
            output_tokens_cost=float(os.getenv("OUTPUT_TOKENS_COST")),
        )
        # Prepare data for update
        update_data = {
            "cost": cost,
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

        # Notify Telegram
        await utils.notify_telegram(result=result, cost=cost)

        logger.info("Database updated successfully.")


if __name__ == "__main__":
    asyncio.run(main())
