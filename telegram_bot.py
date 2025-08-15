import logging
from telegram import Bot
from telegram.error import TelegramError
from config import BOT_TOKEN, FORWARD_GROUP_ID

# Configure logging for this module
logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Telegram Bot wrapper class for sending messages to the target group.
    This class provides a simple interface for bot operations.
    """
    
    def __init__(self):
        """
        Initialize the Telegram Bot with configuration from environment variables.
        
        Raises:
            ValueError: If required configuration is missing
        """
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required but not provided")
        
        if not FORWARD_GROUP_ID:
            raise ValueError("FORWARD_GROUP_ID is required but not provided")
        
        self.forward_group_id = FORWARD_GROUP_ID
        self.bot = Bot(token=BOT_TOKEN)
        
        logger.info("TelegramBot initialized successfully")

    async def send_message(self, text: str, parse_mode: str = "HTML"):
        """
        Send a formatted text message to the configured target group.
        
        Args:
            text (str): Message text to send
            parse_mode (str): Parse mode for message formatting (HTML, Markdown, or None)
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            message = await self.bot.send_message(
                chat_id=self.forward_group_id,
                text=text,
                parse_mode=parse_mode
            )
            
            logger.info(f"Message sent successfully (ID: {message.message_id})")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram API error while sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending message: {e}")
            return False

    async def send_photo(self, photo, caption: str = None, parse_mode: str = "HTML"):
        """
        Send a photo with optional caption to the target group.
        
        Args:
            photo: Photo file or URL to send
            caption (str): Optional caption for the photo
            parse_mode (str): Parse mode for caption formatting
            
        Returns:
            bool: True if photo was sent successfully, False otherwise
        """
        try:
            message = await self.bot.send_photo(
                chat_id=self.forward_group_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode
            )
            
            logger.info(f"Photo sent successfully (ID: {message.message_id})")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram API error while sending photo: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending photo: {e}")
            return False

    async def get_info(self):
        """
        Get information about the bot account.
        
        Returns:
            dict: Bot information or None if failed
        """
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Bot info retrieved: @{bot_info.username}")
            return {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name,
                "is_bot": bot_info.is_bot
            }
        except TelegramError as e:
            logger.error(f"Telegram API error while getting bot info: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while getting bot info: {e}")
            return None

    async def get_chat_info(self):
        """
        Get information about the target chat/group.
        
        Returns:
            dict: Chat information or None if failed
        """
        try:
            chat_info = await self.bot.get_chat(chat_id=self.forward_group_id)
            logger.info(f"Chat info retrieved: {chat_info.title}")
            return {
                "id": chat_info.id,
                "title": chat_info.title,
                "type": chat_info.type,
                "member_count": getattr(chat_info, 'member_count', None)
            }
        except TelegramError as e:
            logger.error(f"Telegram API error while getting chat info: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while getting chat info: {e}")
            return None
