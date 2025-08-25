# Telegram Group Logger Bot

A Telegram bot that logs group information (group name and chat ID) into an Excel file (`group_info.xlsx`) whenever it receives any message from the group.

## Features

- Automatically logs group name, chat ID, and timestamp to an Excel file (`group_info.xlsx`)
- Avoids duplicate logging for the same group
- Periodically prints polling timestamps for monitoring
- Graceful shutdown on Ctrl+C

---

## 1. Create a Telegram Bot

- Find [@BotFather](https://t.me/BotFather) on Telegram.
- Send the command `/newbot`.
- Follow the prompts to set your bot’s name and username (username must end with `bot`).
- Copy the bot token provided.

---

## 2. Prepare the Required Items

- **Install Python**  
  Ensure Python 3.6+ is installed: [Download here](https://www.python.org/downloads/).

- **Install Dependencies**  
  Run the following command in your terminal:  
  ```bash
  pip install python-telegram-bot==13.15 openpyxl
