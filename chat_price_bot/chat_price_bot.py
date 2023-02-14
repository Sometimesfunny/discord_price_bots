# bot for finding currency in chat and send price in chat
import discord
import pycoingecko
import configparser
import datetime
import json
from discord import app_commands

# in string put . every three characters
def format_price(price):
    return "{:,.2f}".format(price)

try:
    with open('price_chats_ids.json', 'r') as f:
        price_chats_ids = json.load(f)
    print('price_chats_ids loaded')
except FileNotFoundError:
    price_chats_ids = []

# create bot class
class MyClient(discord.Client):
    coingecko_api : pycoingecko.CoinGeckoAPI = pycoingecko.CoinGeckoAPI()
    price = None
    last_request = datetime.datetime.now()
    coins_list = coingecko_api.get_coins_list()

    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents ,*args, **kwargs)
        self.synced = False
    
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        if not self.synced:
            commands = await tree.sync()
            # print commands names
            for command in commands:
                print(command.name)
            self.synced = True


    async def prices(self, message : discord.Message):
        content : str = message.content.lower()
        # split words in message with space numericals and symbols
        words : list = content.split()
        if datetime.datetime.now() - self.last_request > datetime.timedelta(days=1):
            self.coins_list = self.coingecko_api.get_coins_list()
            self.last_request = datetime.datetime.now()
        previous_word = ''
        all_found_prices = {}
        for word in words:
            for currency in self.coins_list:
                if word == currency['symbol']:
                    price = self.coingecko_api.get_price(currency['id'], ['usd', 'rub', 'uah'])
                    try:
                        amount = float(previous_word)
                        currency_symbol_upper = currency['symbol'].upper()
                        while currency_symbol_upper in all_found_prices.keys():
                            currency_symbol_upper = currency_symbol_upper + '*'
                        all_found_prices[currency_symbol_upper] = {
                            'amount': amount,
                            'usd': price[currency["id"]]["usd"]*amount,
                            'rub': price[currency["id"]]["rub"]*amount,
                            'uah': price[currency["id"]]["uah"]*amount
                        }
                        break
                    except ValueError:
                        break
            previous_word = word
        if len(all_found_prices) > 0:
            # create embed with all found prices
            embed = discord.Embed(
                title='MENTIONED CURRENCIES PRICES', 
                description='*****',
                color=0x335cd0
                )
            for currency in all_found_prices:
                embed.add_field(name=f'{all_found_prices[currency]["amount"]} {currency.replace("*", "")}', value=format_price(all_found_prices[currency]['usd']) + ' $\n' + format_price(all_found_prices[currency]['rub']) + ' ₽\n' + format_price(all_found_prices[currency]['uah']) + ' ₴', inline=False)
            await message.reply(embed=embed)
    
    # create command to add chat id in price_chats_ids
    def add_chat(self, chat_id : int):
        if chat_id in price_chats_ids:
            return False
        else:
            price_chats_ids.append(chat_id)
            with open('price_chats_ids.json', 'w') as f:
                json.dump(price_chats_ids, f, indent=2)
            print('price_chats_ids saved')
            return True
    
    # remove chat id from price_chats_ids
    def remove_chat(self, chat_id : int):
        if chat_id in price_chats_ids:
            price_chats_ids.remove(chat_id)
            with open('price_chats_ids.json', 'w') as f:
                json.dump(price_chats_ids, f, indent=2)
            print('price_chats_ids saved')
            return True
        else:
            return False

    async def on_message(self, message : discord.Message):
        if message.author == self.user:
            return
        if message.channel.id in price_chats_ids:
            await self.prices(message)


# get token from config file btc_price_bot_config.ini
config = configparser.ConfigParser()
config.read('chat_price_bot_config.ini')
token = config['AUTH']['bot_token']

# run bot with token
client = MyClient(command_prefix='!')

tree = app_commands.CommandTree(client)

GUILD_ID = 1006200270176407582
GUILD = client.get_guild(GUILD_ID)

# command to add chat id in price_chats_ids
@tree.command(name='add_chat', description='Add chat id to price_chats_ids', guild=GUILD)
async def add_chat(interaction : discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return
    if client.add_chat(interaction.channel_id):
        await interaction.response.send_message(f'Chat {interaction.channel.mention} added', ephemeral=True)
    else:
        await interaction.response.send_message(f'Chat {interaction.channel.mention} already added', ephemeral=True)

# command to remove chat id from price_chats_ids
@tree.command(name='remove_chat', description='Remove chat id from price_chats_ids', guild=GUILD)
async def remove_chat(interaction : discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return
    if client.remove_chat(interaction.channel_id):
        await interaction.response.send_message(f'Chat {interaction.channel.mention} removed', ephemeral=True)
    else:
        await interaction.response.send_message(f'Chat {interaction.channel.mention} not found', ephemeral=True)

# command to list price_chats_ids mentions
@tree.command(name='list_chats', description='List price chats', guild=GUILD)
async def list_chats(interaction : discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return
    if len(price_chats_ids) == 0:
        await interaction.response.send_message(f'No chats added', ephemeral=True)
    else:
        await interaction.response.send_message(f'Chats: {", ".join([f"{client.get_channel(chat_id).mention}" for chat_id in price_chats_ids])}', ephemeral=True)
    

client.run(token)


with open('price_chats_ids.json', 'w') as f:
    json.dump(price_chats_ids, f, indent=2)
print('price_chats_ids saved')
