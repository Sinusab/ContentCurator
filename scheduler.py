#!/usr/bin/env python3
"""
Scheduler for automatic content curation at regular intervals.
This script runs the main content curation process every few hours.
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime
from main import main as run_content_curation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def scheduled_curation():
    """
    Run the content curation process as a scheduled task.
    """
    try:
        logger.info("🚀 Starting scheduled content curation...")
        await run_content_curation()
        logger.info("✅ Scheduled content curation completed successfully")
    except Exception as e:
        logger.error(f"❌ Scheduled content curation failed: {e}")

def run_async_curation():
    """
    Wrapper to run async function in scheduler.
    """
    asyncio.run(scheduled_curation())

def main():
    """
    Main scheduler function that sets up and runs the scheduled tasks.
    """
    logger.info("📅 Content Curation Scheduler Started")
    logger.info("⏰ Will run every 4 hours")
    
    # Schedule the content curation to run every 4 hours
    schedule.every(4).hours.do(run_async_curation)
    
    # Also run once immediately
    logger.info("🔄 Running initial content curation...")
    run_async_curation()
    
    # Keep the scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    main()