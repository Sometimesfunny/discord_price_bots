# Discord Admin Bot
Set of bots for cryptocurrency price tracking (Inspired by [DBS DAO](https://t.me/bomzhuem))

# Install
## Requirements
- Python3.8+
## Dependencies
- discord.py 2.0.0+
- cloudscraper 1.2.68+
- beautifulsoup 4.11.2+
- pycoingecko 3.1.0+
## Installation
1. ```sh
    sudo apt update && sudo apt upgrade -y
    sudo apt install git
    git clone git@github.com:Sometimesfunny/discord_price_bots.git
    pip3 install -r requirements.txt
    ```
2. Create *bot_name*_config.ini in the folder with needed bot. Example: btc_price_bot/btc_price_bot_config.ini
3. Insert this template:
```ini
[AUTH]
bot_token = 'YOUR_DISCORD_BOT_TOKEN'
```
4. Save file
## Run
```sh
python3 *bot_name*.py
```
# Features
## btc_price_bot, eth_price_bot, sol_price_bot
Get info from https://coingecko.com and update status with last price of btc, eth, sol. Status updates every 5 minutes.

## chat_price_bot
Every time somebody types number and ticker in chat bot makes request to https://coingecko.com and gets current price of this coin. It is possible to change add/remove chats from bot whitelist using /add_chat or /remove_chat

/list_chats to see chats which bot monitors

## gas_price_bot
Creates autoupdated embed with current gas price in ether network

/create_gas_embed - command to create embed with prices

