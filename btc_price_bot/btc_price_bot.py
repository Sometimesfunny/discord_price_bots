# discord bot for btc price
# it calls coingecko api to get the price of btc
# and set price in bot status

# imports
import datetime
import discord
import pycoingecko
import asyncio
import configparser

# in string put . every three characters
def format_price(price):
    return "{:,.2f}".format(price)

# create bot class
class MyClient(discord.Client):
    coingecko_api : pycoingecko.CoinGeckoAPI = pycoingecko.CoinGeckoAPI()
    price = None

    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        super().__init__(intents=intents ,*args, **kwargs)

    async def on_ready(self):
        print('Logged on as', self.user)
        await self.update_status()
        print('bot is ready')

    # update bot status every 5 minutes
    async def update_status(self):
        while True:
            try:
                self.price = self.coingecko_api.get_price('bitcoin', 'usd')
                try:
                    await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{format_price(self.price['bitcoin']['usd'])} $"), status=discord.Status.online)
                    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), f"Price updated {format_price(self.price['bitcoin']['usd'])} $")
                except Exception as e:
                    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), e)
            except Exception as e:
                print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'Error getting price')
                print(e)
            await asyncio.sleep(300)
    
# get token from config file btc_price_bot_config.ini
config = configparser.ConfigParser()
config.read('btc_price_bot_config.ini')
token = config['AUTH']['bot_token']

# run bot with token
client = MyClient()
client.run(token)

