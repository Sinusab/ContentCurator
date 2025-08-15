import asyncio
import logging
from telethon import TelegramClient
from telegram_bot import TelegramBot
from scrapers.telegram_scraper import fetch_top_posts_last_24h
from utils import format_post_caption, validate_post_data
from config import API_ID, API_HASH, SESSION_NAME, CHANNELS, LIMIT_PER_CHANNEL, FORWARD_GROUP_ID
import math

# Configure logging for better debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('content_curator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def send_post_with_media(client, post):
    """
    Send a post with media to the target group anonymously.
    
    Args:
        client: Telethon client instance
        post (dict): Post data containing media and text information
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the original message from the source channel
        original_msg = await client.get_messages(post['channel'], ids=post['id'])
        
        if not original_msg:
            logger.error(f"Could not retrieve message {post['id']} from @{post['channel']}")
            return False
        
        # Format the caption with proper HTML formatting
        caption = format_post_caption(post)
        
        # Send media with caption anonymously (using send_file instead of forward)
        await client.send_file(
            entity=FORWARD_GROUP_ID,
            file=original_msg.media,
            caption=caption,
            parse_mode="html"  # Enable HTML parsing for blockquote
        )
        
        logger.info(f"Successfully sent media post from @{post['channel']} (ID: {post['id']})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send media post from @{post['channel']} (ID: {post['id']}): {e}")
        return False

async def send_text_post(client, post):
    """
    Send a text-only post to the target group.
    
    Args:
        client: Telethon client instance
        post (dict): Post data containing text information
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Format the message with proper HTML formatting
        message = format_post_caption(post)
        
        # Send text message with HTML parsing enabled
        await client.send_message(
            entity=FORWARD_GROUP_ID,
            message=message,
            parse_mode="html"
        )
        
        logger.info(f"Successfully sent text post from @{post['channel']} (ID: {post['id']})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send text post from @{post['channel']} (ID: {post['id']}): {e}")
        return False

async def main():
    """
    Main application function that orchestrates the content curation process.
    
    Process:
    1. Fetch top posts from the last 24 hours from target channels
    2. Select top 20% based on interaction score
    3. Send posts anonymously to the target group with proper formatting
    """
    logger.info("Starting content curation process...")
    
    # Use a single Telethon client instance for the entire process
    client = None
    
    try:
        # Initialize Telethon client for both scraping and sending
        logger.info("Initializing Telethon client...")
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        await client.start()
        logger.info("Telethon client started successfully")
        
        # Fetch top posts from the last 24 hours using the same client
        logger.info(f"Fetching posts from channels: {CHANNELS}")
        posts = await fetch_top_posts_with_client(client, CHANNELS, LIMIT_PER_CHANNEL)
        
        if not posts:
            logger.warning("No posts found to process")
            return
        
        logger.info(f"Found {len(posts)} top posts to process")
        
        # Process each post
        successful_sends = 0
        failed_sends = 0
        
        for post in posts:
            # Validate post data before processing
            if not validate_post_data(post):
                logger.warning(f"Invalid post data from @{post.get('channel', 'unknown')}")
                failed_sends += 1
                continue
            
            try:
                if post['has_media']:
                    # Send post with media anonymously
                    success = await send_post_with_media(client, post)
                else:
                    # Send text-only post
                    success = await send_text_post(client, post)
                
                if success:
                    successful_sends += 1
                else:
                    failed_sends += 1
                    
                # Add a small delay between posts to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error processing post from @{post['channel']}: {e}")
                failed_sends += 1
        
        # Log final statistics
        logger.info(f"Content curation completed. Success: {successful_sends}, Failed: {failed_sends}")
        
    except Exception as e:
        logger.error(f"Critical error in main process: {e}")
        raise
    
    finally:
        # Ensure client is properly disconnected
        if client and client.is_connected():
            try:
                await client.disconnect()
                logger.info("Telethon client disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting client: {e}")

async def fetch_top_posts_with_client(client, channels, limit_per_channel=50):
    """
    Fetch top posts using an existing client to avoid session conflicts.
    Selects top 20% of posts from EACH channel individually to ensure fair representation.
    
    Args:
        client: Already connected Telethon client
        channels: List of channel usernames
        limit_per_channel: Max posts per channel
        
    Returns:
        list: Top 20% posts from each channel combined and sorted by interaction score
    """
    from datetime import datetime, timedelta, timezone
    from utils import calculate_interaction_score
    import json
    from pathlib import Path
    
    logger.info(f"Starting to fetch posts from {len(channels)} channels")
    
    all_posts_by_channel = {}  # Store posts grouped by channel
    current_time = datetime.now(timezone.utc)
    cutoff_time = current_time - timedelta(hours=24)
    
    logger.info(f"Fetching posts newer than {cutoff_time}")
    
    # Process each channel separately
    for channel in channels:
        try:
            logger.info(f"Processing channel: @{channel}")
            
            # Get channel entity
            entity = await client.get_entity(channel)
            
            # Fetch recent messages from the channel
            messages = await client.get_messages(entity, limit=limit_per_channel)
            
            channel_posts = []
            
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
                    
                    channel_posts.append(post_data)
                else:
                    # Messages are ordered by date, so we can break early
                    break
            
            # Sort posts from this channel by interaction score
            channel_posts.sort(key=lambda x: x['interaction_score'], reverse=True)
            
            # Select top 20% from this channel (minimum 1 post if any exist)
            if channel_posts:
                top_percentage = 0.2  # 20%
                channel_top_count = max(1, math.ceil(len(channel_posts) * top_percentage))
                channel_top_posts = channel_posts[:channel_top_count]
                
                all_posts_by_channel[channel] = {
                    'total_posts': len(channel_posts),
                    'selected_posts': channel_top_count,
                    'posts': channel_top_posts
                }
                
                logger.info(f"Selected {channel_top_count} top posts from {len(channel_posts)} recent posts in @{channel}")
            else:
                logger.info(f"No recent posts found in @{channel}")
                all_posts_by_channel[channel] = {
                    'total_posts': 0,
                    'selected_posts': 0,
                    'posts': []
                }
            
        except Exception as e:
            logger.error(f"Failed to fetch messages from @{channel}: {e}")
            all_posts_by_channel[channel] = {
                'total_posts': 0,
                'selected_posts': 0,
                'posts': [],
                'error': str(e)
            }
            continue
    
    # Combine all selected posts from all channels
    all_selected_posts = []
    total_posts_all_channels = 0
    total_selected_posts = 0
    
    for channel, data in all_posts_by_channel.items():
        all_selected_posts.extend(data['posts'])
        total_posts_all_channels += data['total_posts']
        total_selected_posts += data['selected_posts']
    
    # Sort the combined selected posts by interaction score for final ordering
    all_selected_posts.sort(key=lambda x: x['interaction_score'], reverse=True)
    
    logger.info(f"Final selection: {total_selected_posts} posts from {total_posts_all_channels} total posts across {len(channels)} channels")
    
    # Log selection summary for each channel
    for channel, data in all_posts_by_channel.items():
        if data['selected_posts'] > 0:
            logger.info(f"  📊 @{channel}: {data['selected_posts']}/{data['total_posts']} posts selected")
        elif 'error' in data:
            logger.warning(f"  ❌ @{channel}: Error - {data['error']}")
        else:
            logger.info(f"  📭 @{channel}: No recent posts found")
    
    # Save detailed analysis to JSON file
    try:
        content_dir = Path("content")
        content_dir.mkdir(exist_ok=True)
        content_file = content_dir / "posts.json"
        
        analysis_data = {
            "timestamp": current_time.isoformat(),
            "selection_method": "top_20_percent_per_channel",
            "total_channels": len(channels),
            "total_posts_found": total_posts_all_channels,
            "total_posts_selected": total_selected_posts,
            "channels_analysis": all_posts_by_channel,
            "final_selected_posts": all_selected_posts
        }
        
        with open(content_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved detailed analysis to {content_file}")
        
    except Exception as e:
        logger.error(f"Failed to save post data: {e}")
    
    return all_selected_posts

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        exit(1)
