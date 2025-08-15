#!/usr/bin/env python3
"""
Utility script to help find Telegram group IDs.
Run this script after adding your bot to the target group.
"""

import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()

async def get_group_info():
    """
    Get information about groups where the bot has been added.
    This helps you find the correct FORWARD_GROUP_ID.
    """
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print("❌ BOT_TOKEN not found in environment variables!")
        print("Please set BOT_TOKEN in your .env file first.")
        return
    
    bot = Bot(token=bot_token)
    
    try:
        # Get bot information
        bot_info = await bot.get_me()
        print(f"🤖 Bot: @{bot_info.username} ({bot_info.first_name})")
        print("\n" + "="*50)
        
        # Get recent updates to find groups
        print("📋 Looking for recent group interactions...")
        updates = await bot.get_updates(limit=100)
        
        groups_found = {}
        
        for update in updates:
            if update.message and update.message.chat:
                chat = update.message.chat
                
                # Only show groups and supergroups
                if chat.type in ['group', 'supergroup']:
                    groups_found[chat.id] = {
                        'title': chat.title,
                        'type': chat.type,
                        'id': chat.id
                    }
        
        if groups_found:
            print(f"\n✅ Found {len(groups_found)} group(s):")
            print("\nCopy one of these IDs to your .env file as FORWARD_GROUP_ID:")
            print("-" * 60)
            
            for group_id, info in groups_found.items():
                print(f"📁 Group: {info['title']}")
                print(f"🆔 ID: {group_id}")
                print(f"📝 Type: {info['type']}")
                print(f"💾 For .env file: FORWARD_GROUP_ID={group_id}")
                print("-" * 60)
        else:
            print("\n⚠️  No groups found in recent updates!")
            print("\n📝 To find your group ID:")
            print("1. Add your bot to the target group")
            print("2. Send a message in the group (like /start)")
            print("3. Run this script again")
            print("\n🔗 Alternative: Use @userinfobot or @RawDataBot in your group")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("1. Make sure BOT_TOKEN is correct")
        print("2. Make sure the bot is added to your target group")
        print("3. Send a message in the group first")

if __name__ == "__main__":
    print("🔍 Telegram Group ID Finder")
    print("=" * 30)
    asyncio.run(get_group_info())