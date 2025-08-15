# Telegram Content Curator

A Python-based Telegram content curation bot that automatically fetches top posts from specified channels and forwards them to a target group with proper formatting.

## Features

- **Automated Content Curation**: Fetches posts from the last 24 hours from specified Telegram channels
- **Smart Selection**: Selects top 20% of posts based on interaction score (views + forwards)
- **Anonymous Forwarding**: Sends posts without showing the original sender
- **Media Support**: Forwards posts with media (photos, videos, documents) along with their content
- **Custom Formatting**: Adds "powered by Sinus-Alpha" as a blockquote to all forwarded posts
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Secure Configuration**: Environment variable-based configuration for sensitive data

## Requirements

- Python 3.7 or higher
- Telegram Bot API token
- Telethon API credentials (API ID and API Hash)
- Access to target channels and destination group

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd telegram-content-curator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your credentials:
```env
BOT_TOKEN=your_bot_token_here
FORWARD_GROUP_ID=your_group_id_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
CHANNELS=channel1,channel2,channel3
```

## Configuration

### Required Environment Variables

- `BOT_TOKEN`: Your Telegram bot token from @BotFather
- `FORWARD_GROUP_ID`: Numeric ID of the target group where posts will be sent
- `API_ID`: Your Telegram API ID from https://my.telegram.org
- `API_HASH`: Your Telegram API Hash from https://my.telegram.org

### Optional Environment Variables

- `SESSION_NAME`: Name for the Telethon session file (default: "contentcurator_session")
- `CHANNELS`: Comma-separated list of channel usernames to monitor (default: "gizmiztel")
- `LIMIT_PER_CHANNEL`: Maximum posts to fetch per channel (default: 50)

## Usage

Run the content curator:
```bash
python main.py
```

The application will:
1. Connect to Telegram using your credentials
2. Fetch recent posts from specified channels
3. Calculate interaction scores for each post
4. Select the top 20% of posts
5. Forward them anonymously to your target group
6. Add the "powered by Sinus-Alpha" footer as a blockquote

## Project Structure

```
telegram-content-curator/
├── main.py                 # Main application entry point
├── config.py              # Configuration management
├── telegram_bot.py        # Telegram Bot API wrapper
├── utils.py               # Utility functions
├── scrapers/
│   └── telegram_scraper.py # Channel scraping functionality
├── content/               # Generated content storage
│   └── posts.json        # Scraped posts data
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (create this)
└── README.md            # This file
```

## Logging

The application generates comprehensive logs:
- Console output for real-time monitoring
- Log file (`content_curator.log`) for persistent logging
- Structured logging with timestamps and severity levels

## Security

- All sensitive data is managed through environment variables
- No hardcoded credentials in the source code
- Session files are stored locally and not committed to version control

## How It Works

1. **Channel Monitoring**: The scraper connects to specified Telegram channels using Telethon
2. **Content Analysis**: Posts from the last 24 hours are analyzed for engagement metrics
3. **Score Calculation**: Interaction score = views + (forwards × 2) + (reactions × 3)
4. **Top Selection**: Top 20% of posts by interaction score are selected
5. **Anonymous Forwarding**: Posts are sent using `send_file` and `send_message` instead of forwarding
6. **Custom Formatting**: Each post gets the "powered by Sinus-Alpha" footer in blockquote format

## Error Handling

The application includes comprehensive error handling:
- Network connectivity issues
- API rate limiting
- Invalid channel access
- Missing media files
- Configuration errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions, please open an issue in the repository.