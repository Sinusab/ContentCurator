import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from telethon import TelegramClient
from config import API_ID, API_HASH, SESSION_NAME
from utils import calculate_interaction_score

# Configure logging for this module
logger = logging.getLogger(__name__)

# Directory and file for storing scraped content
CONTENT_DIR = Path("content")
CONTENT_FILE = CONTENT_DIR / "posts.json"

# Ensure content directory exists
CONTENT_DIR.mkdir(exist_ok=True)

async def fetch_top_posts_last_24h(channels, limit_per_channel=50):
    """
    Fetch and analyze posts from specified Telegram channels in the last 24 hours.
    Returns the top 20% of posts based on interaction score (views + forwards).
    
    Args:
        channels (list): List of channel usernames to scrape
        limit_per_channel (int): Maximum number of posts to fetch per channel
        
    Returns:
        list: Top 20% of posts sorted by interaction score in descending order
    """
    logger.info(f"Starting to fetch posts from {len(channels)} channels")
    
    # Initialize Telethon client for scraping
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    
    all_posts = []
    current_time = datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(hours=24)
    
    logger.info(f"Fetching posts newer than {cutoff_time}")
    
    # Process each channel
    for channel in channels:
        try:
            logger.info(f"Processing channel: @{channel}")
            
            # Get channel entity
            entity = await client.get_entity(channel)
            
            # Fetch recent messages from the channel
            messages = await client.get_messages(entity, limit=limit_per_channel)
            
            posts_from_channel = 0
            
            # Process each message
            for msg in messages:
                # Only process messages from the last 24 hours
                if msg.date >= cutoff_time:
                    # Extract engagement metrics
                    views = getattr(msg, 'views', 0) or 0
                    forwards = getattr(msg, 'forwards', 0) or 0
                    
                    # Calculate interaction score using utility function
                    interaction_score = calculate_interaction_score(views, forwards)
                    
                    # Create post data structure
                    post_data = {
                        "channel": channel,
                        "text": msg.message or "",
                        "views": views,
                        "forwards": forwards,
                        "interaction_score": interaction_score,
                        "date": msg.date.isoformat(),
                        "id": msg.id,
                        "has_media": bool(msg.media)
                    }
                    
                    all_posts.append(post_data)
                    posts_from_channel += 1
                else:
                    # Messages are ordered by date, so we can break early
                    break
            
            logger.info(f"Fetched {posts_from_channel} recent posts from @{channel}")
            
        except Exception as e:
            logger.error(f"Failed to fetch messages from @{channel}: {e}")
            continue
    
    # Disconnect the client
    await client.disconnect()
    
    # Sort posts by interaction score in descending order
    all_posts.sort(key=lambda x: x['interaction_score'], reverse=True)
    
    # Calculate top 20% (minimum 1 post)
    total_posts = len(all_posts)
    top_percentage = 0.2  # 20%
    top_count = max(1, int(total_posts * top_percentage))
    
    # Select top posts
    top_posts = all_posts[:top_count]
    
    logger.info(f"Selected {top_count} top posts out of {total_posts} total posts")
    
    # Save all posts to JSON file for debugging and analysis
    try:
        with open(CONTENT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": current_time.isoformat(),
                "total_posts": total_posts,
                "top_posts_count": top_count,
                "top_posts": top_posts,
                "all_posts": all_posts  # Include all posts for analysis
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved post data to {CONTENT_FILE}")
        
    except Exception as e:
        logger.error(f"Failed to save post data: {e}")
    
    return top_posts

async def get_channel_info(channel_username):
    """
    Get basic information about a Telegram channel.
    
    Args:
        channel_username (str): Channel username without @
        
    Returns:
        dict: Channel information including title, member count, etc.
    """
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    
    try:
        entity = await client.get_entity(channel_username)
        
        channel_info = {
            "username": channel_username,
            "title": entity.title,
            "id": entity.id,
            "participants_count": getattr(entity, 'participants_count', 0),
            "verified": getattr(entity, 'verified', False),
            "scam": getattr(entity, 'scam', False)
        }
        
        await client.disconnect()
        return channel_info
        
    except Exception as e:
        logger.error(f"Failed to get info for @{channel_username}: {e}")
        await client.disconnect()
        return None
