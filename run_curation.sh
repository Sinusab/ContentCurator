#!/bin/bash

# Telegram Content Curation Runner Script
# This script can be used with cron for scheduled execution

# Change to the project directory
cd "$(dirname "$0")"

# Log the start time
echo "$(date): Starting content curation..." >> curation_cron.log

# Run the content curation
python3 main.py >> curation_cron.log 2>&1

# Log the completion
echo "$(date): Content curation completed" >> curation_cron.log

# Add a separator line
echo "----------------------------------------" >> curation_cron.log