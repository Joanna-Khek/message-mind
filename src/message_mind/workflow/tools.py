import os
from loguru import logger
from urllib.parse import urlparse, parse_qs
from typing import Tuple, Optional
from langchain_community.document_loaders import UnstructuredURLLoader
from googleapiclient.discovery import build, Resource
from langchain.tools import tool

# TODO: Tool for linkedin post (title)
# TODO: Tool for to do list


@tool
def html_to_text(url: str) -> str:
    """
    Takes a URL and converts the HTML content to plain text.
    Returns the first 1000 characters for brevity.

    Args:
        url (str): The URL to fetch and convert.

    Returns:
        str: The plain text content of the webpage, truncated to 1000 characters.
    """
    try:
        # Load HTML content
        loader = UnstructuredURLLoader(urls=[url])
        doc = loader.load()

        text = doc[0].page_content
        return text[:1000]

    except Exception as e:
        return f"Failed to fetch or process the URL. Error: {str(e)}"


def parse_youtube_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Takes a Youtube URL and extract the video ID (if any) and playlist ID (if any)

    Args:
        url (str): The Youtube URL to parse.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the video ID and/or playlist ID.
    """
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]
        playlist_id = query.get("list", [None])[0]
        return video_id, playlist_id
    except Exception as e:
        logger.error(f"Failed to fetch or process the URL. Error: {str(e)}")
        return None, None


def get_video_info(youtube: Resource, video_id: str) -> dict:
    """
    Fetches youtube video information given a video ID.

    Args:
        youtube (Resource): The YouTube API resource object.
        video_id (str): The ID of the YouTube video.

    Returns:
        dict: A dictionary containing the video's title, description, tags, and channel title.
    """
    try:
        response = (
            youtube.videos()
            .list(part="snippet,contentDetails,statistics", id=video_id)
            .execute()
        )

        if not response["items"]:
            print(f"[!] No video found with ID: {video_id}")
            return

        info = response["items"][0]
        snippet = info["snippet"]
        saved_info = {
            "title": snippet["title"],
            "description": snippet["description"],
            "tags": snippet.get("tags", []),
            "channel_title": snippet["channelTitle"],
        }

        return saved_info
    except Exception as e:
        logger.error(f"Failed to fetch video info. Error: {str(e)}")
        return None


def get_playlist_info(youtube: Resource, playlist_id: str) -> dict:
    """
    Fetches youtube playlist information given a playlist ID.

    Args:
        youtube (Resource): The YouTube API resource object.
        playlist_id (str): The ID of the YouTube playlist.

    Returns:
        dict: A dictionary containing the playlist's title, description, and video count.

    """
    try:
        response = (
            youtube.playlists()
            .list(part="snippet,contentDetails", id=playlist_id)
            .execute()
        )

        if not response["items"]:
            print(f"[!] No playlist found with ID: {playlist_id}")
            return

        playlist = response["items"][0]
        saved_info = {
            "title": playlist["snippet"]["title"],
            "description": playlist["snippet"]["description"],
            "video_count": playlist["contentDetails"]["itemCount"],
        }
        return saved_info
    except Exception as e:
        logger.error(f"Failed to fetch playlist info. Error: {str(e)}")
        return None


@tool
def get_youtube_info(url: str) -> dict:
    """
    Takes a Youtube URL and extract the video information such as title, description, and other metadata.

    Args:
        url (str): The Youtube URL to parse.

    Returns:
        dict: Keys are 'playlist_info' and 'video_info', each containing the respective information.
    """
    try:
        video_id, playlist_id = parse_youtube_url(url)
        youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

        video_info = {}

        if playlist_id:
            video_info["playlist_info"] = get_playlist_info(youtube, playlist_id)
        if video_id:
            video_info["video_info"] = get_video_info(youtube, video_id)
        return video_info

    except Exception as e:
        logger.info(f"Failed to fetch or process the URL. Error: {str(e)}")
        return None


tools = [html_to_text, get_youtube_info]
