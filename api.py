import requests
from bs4 import BeautifulSoup
import discord
import asyncio
import datetime

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

post_id = 41291
# replace id 0123456789 with your own
channel_id = 0123456789

async def check_for_updates(post_id):
    url = f'https://blog.counter-strike.net/wp-json/wp/v2/posts/{post_id}'
    response = requests.get(url)
    if response.status_code == 200:
        # set your own server's ID
        server = client.get_guild(0123456789)
        #set the role you want the bot to ping upon the 200 (request successful) replace 0123456789
        role = discord.utils.get(server.roles, id=0123456789)
        message = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | STATUS {response.status_code}: A new blog post was published with ID {post_id}! {role.mention} URL: https://blog.counter-strike.net/index.php/2023/02/41291/'
        channel = client.get_channel(channel_id)
        if channel:
            await asyncio.create_task(channel.send(message))
            return True
        else:
            print(f'Error: Could not find channel with ID {channel_id}')
        return False
    elif response.status_code == 429:
        print(f'Received 429 response for post ID {post_id}. Retrying in 60 seconds...')
        await asyncio.sleep(60)  # Wait for 60 seconds before retrying
        return await check_for_updates(post_id)  # Retry the request
    elif response.status_code != 404:
        print(f'Post ID {post_id} has status code {response.status_code}')
        return False
    else:
        return False

async def run_update_check(post_id):
    while True:
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Checking post ID {post_id}')
        result = await check_for_updates(post_id)
        print(f'retrying to get api response')
        if result == True:
            return
        await asyncio.sleep(2)

@client.event
async def on_ready():
    print('Bot is ready.')
    await run_update_check(post_id)
# replace INSERT_BOT_TOKEN with your own
client.run('INSERT_BOT_TOKEN')
