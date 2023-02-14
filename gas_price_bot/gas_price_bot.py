# imports
import discord
import configparser
from discord import app_commands
import json
from discord.ext import tasks
from bs4 import BeautifulSoup
import cloudscraper
import datetime

def load_data(filename : str):
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data, filename : str):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# in string put . every three characters
def format_price(price):
    return "{:,.2f}".format(price)

# create bot class
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        super().__init__(intents=intents ,*args, **kwargs)
        self.sync = False

    async def on_ready(self):
        print('Logged on as', self.user)
        if not self.sync:
            await tree.sync()
            self.sync = True
        print('Bot is ready')
        update_gas_embed.start()

def process_list(full_list, ban_list = []):
    full_list.sort(key=lambda x: x[1])
    if ban_list != []:
        full_list = [x for x in full_list if x[0].split(':')[0].lower() not in ban_list]
    return full_list

def complete_list(full_list):
    # remain only strings with Swap endings
    final_transfer_list = process_list([x for x in full_list if x[0].endswith("Transfer")])
    final_swap_list = process_list([x for x in full_list if x[0].endswith("Swap")], ['balancer', 'bancor', '0x', 'cow protocol', 'kyberswap'])
    final_bridge_list = process_list([x for x in full_list if x[0].endswith("Bridge")])
    final_list = final_transfer_list + final_swap_list + final_bridge_list
    return final_list

def get_embed():
    # save page into file
    scraper = cloudscraper.create_scraper()
    response = scraper.get("https://etherscan.io/gastracker")
    if response.status_code != 200:
        print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "Error getting page")
        return None
    soup = BeautifulSoup(response.content, "html.parser")
    # get gas price
    try:
        gas_price = soup.find("div", {"class": "row text-center mb-4"})
        low_price = soup.find('div', {'id': 'divLowPrice'}).find_all('span')
        avg_price = soup.find('div', {'id': 'divAvgPrice'}).find_all('span')
        high_price = soup.find('div', {'id': 'divHighPrice'}).find_all('span')
        low_price_dollars = soup.find('div', {'id': 'divLowPrice'}).find_all('div', {'class': 'text-secondary'})
        avg_price_dollars = soup.find('div', {'id': 'divLowPrice'}).find_all('div', {'class': 'text-secondary'})
        high_price_dollars = soup.find('div', {'id': 'divLowPrice'}).find_all('div', {'class': 'text-secondary'})
    except AttributeError:
        print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "Error getting gas price")
        return None
    # save gas price into file
    low_price_gwei = 0
    avg_price_gwei = 0
    high_price_gwei = 0
    for row in low_price:
        try:
            low_price_gwei = int(row.text)
            break
        except ValueError:
            continue
    for row in avg_price:
        try:
            avg_price_gwei = int(row.text)
            break
        except ValueError:
            continue
    for row in high_price:
        try:
            high_price_gwei = int(row.text)
            break
        except ValueError:
            continue
    for row in low_price_dollars:
        if '$' in row.text:
            low_price_dollars = row.text.split(' ')[0]
            break
    for row in avg_price_dollars:
        if '$' in row.text:
            avg_price_dollars = row.text.split(' ')[0]
            break
    for row in high_price_dollars:
        if '$' in row.text:
            high_price_dollars = row.text.split(' ')[0]
            break
    table = soup.find("table", {"class": "table table-sm1 mb-0"})
    rows = table.find_all("tr")
    embed = discord.Embed(title="Ethereum Gas Price", color=0x335cd0, description="Showing the current transaction price for different actions", timestamp=datetime.datetime.now())
    embed.add_field(name="🐢Slow", value=f"{low_price_gwei} Gwei\n{low_price_dollars} USD", inline=True)
    embed.add_field(name="🚶‍♂️Normal", value=f"{avg_price_gwei} Gwei\n{avg_price_dollars} USD", inline=True)
    embed.add_field(name="🏎️Fast", value=f"{high_price_gwei} Gwei\n{high_price_dollars} USD", inline=True)
    remain_text_list = []
    for row in rows:
        row = row.find_all("td")
        if row == []:
            continue
        if row[0].text == '':
            continue
        remain_text_list.append([row[0].text[1:], row[1].text, row[2].text, row[3].text])
    final_list = complete_list(remain_text_list)
    for row in final_list:
        value = '\n'.join(['🐢'+row[1], '🚶‍♂️'+row[2], '🏎️'+row[3]])
        embed.add_field(name=row[0], value=value)
    embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ethereum_logo_2014.svg/1257px-Ethereum_logo_2014.svg.png')
    return embed

    
# get token from config file btc_price_bot_config.ini
config = configparser.ConfigParser()
config.read('gas_price_bot_config.ini')
token = config['AUTH']['bot_token']

# load data from json file
data = load_data("data.json")

# run bot with token
client = MyClient()

tree = app_commands.CommandTree(client)

first_start = False

@tree.command(name="create_gas_embed", description="Create a gas embed")
async def create_gas_embed(interaction : discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return
    if ('channel_id' in data) and 'message_id' in data:
        if data['channel_id'] is not None:
            if data['message_id'] is not None:
                old_channel = interaction.guild.get_channel(data['channel_id'])
                old_message = await old_channel.fetch_message(data['message_id'])
                await old_message.delete()
                update_gas_embed.cancel()
    
    embed = get_embed()
    if embed is None:
        await interaction.response.send_message("Error getting gas price", ephemeral=True)
        return
    await interaction.response.send_message('Embed created', ephemeral=True)
    message = await interaction.channel.send(embed=embed)
    data['channel_id'] = message.channel.id
    data['message_id'] = message.id
    save_data(data, "data.json")
    global first_start
    first_start = True
    update_gas_embed.start()

@tasks.loop(minutes=5)
async def update_gas_embed():
    global first_start
    if ('channel_id' in data) and 'message_id' in data:
        if data['channel_id'] is not None:
            if data['message_id'] is not None:
                if first_start:
                    first_start = False
                    return
                channel = client.get_channel(data['channel_id'])
                message = await channel.fetch_message(data['message_id'])
                embed = get_embed()
                if embed is None:
                    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'Error getting gas price. Retrying in 5 minutes')
                    return
                await message.edit(embed=embed)
                print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 'Embed updated')
                return
            else:
                print('message_id is None')
        else:
            print('channel_id is None')
    else:
        print('No setup completed')
    update_gas_embed.cancel()
    
# get_embed()


client.run(token)

