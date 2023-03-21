import requests
import discord
import asyncio
import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv()

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

post_id = 41291
channel_id = os.getenv('CHANNEL_ID')
num_ids_to_check = 100

async def find_hidden_posts(starting_post_id, num_ids_to_check):
    while True:
        post_statuses = load_post_statuses()
        for i in range(starting_post_id + 3, starting_post_id + num_ids_to_check + 1):
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Checking post {i} for hidden data!')
            status_code = await check_for_updates(i)
            if status_code != 404 and i not in post_statuses and status_code != 429:
                post_statuses[i] = status_code
                print(f'found something: {post_statuses}')
                save_post_statuses(post_statuses)
                if status_code == 401:
                    await notify_hidden_post(i)
            await asyncio.sleep(15)
        await asyncio.sleep(60)


async def notify_hidden_post(post_id, status_code):
    server = client.get_guild(int(os.getenv('SERVER_ID')))
    if server is None:
        print(f'Error: Could not find server with ID {os.getenv("SERVER_ID")}')
        return
    role = discord.utils.get(server.roles, id=int(os.getenv('ROLE_ID')))
    if role is None:
        print(f'Error: Could not find role with ID {os.getenv("ROLE_ID")}')
        return
    message = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Found a hidden blog post with ID {post_id}! {role.mention} URL: https://blog.counter-strike.net/index.php/2023/02/{post_id}/'
    channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
    if channel:
        await asyncio.create_task(channel.send(message))
    else:
        print(f'Error: Could not find channel with ID {channel_id}')

def save_post_statuses(post_statuses):
    with open('post_statuses.json', 'w') as f:
        json.dump(post_statuses, f)


def load_post_statuses():
    try:
        with open('post_statuses.json', 'r') as f:
            data = f.read()
            if not data:
                return {}
            return json.loads(data)
    except FileNotFoundError:
        with open('post_statuses.json', 'w') as f:
            f.write("{}")
        return {}

async def check_for_updates(post_id):
    try:
        url = f'https://blog.counter-strike.net/wp-json/wp/v2/posts/{post_id}'
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Connection error: {e}. Retrying in 5 minutes...')
        await asyncio.sleep(300)
        return await check_for_updates(post_id)

async def notify_new_post(post_id, status_code):
    server = client.get_guild(int(os.getenv('SERVER_ID')))
    if server is None:
        print(f'Error: Could not find server with ID {os.getenv("SERVER_ID")}')
        return
    role = discord.utils.get(server.roles, id=int(os.getenv('ROLE_ID')))
    if role is None:
        print(f'Error: Could not find role with ID {os.getenv("ROLE_ID")}')
        return
    status_text = 'Found' if status_code == 200 else 'Hidden'
    message = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | A {status_text} blog post with ID {post_id}! {role.mention} URL: https://blog.counter-strike.net/index.php/2023/02/{post_id}/'
    channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
    if channel:
        await asyncio.create_task(channel.send(message))
    else:
        print(f'Error: Could not find channel with ID {channel_id}')

async def run_update_check(post_id):
    starting_post_id = post_id
    post_statuses = load_post_statuses()
    while True:
        hidden_posts = []
        post = starting_post_id
        while True:
            status_code = await check_for_updates(post)
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} checking {post} for updated data!')
            if status_code != post_statuses.get(str(post)):
                if status_code == 200 or status_code == 401:
                    await notify_new_post(post, status_code)
                    post_statuses[str(post)] = status_code
                    save_post_statuses(post_statuses)
                    if status_code == 401:
                        hidden_posts.append(post)
                elif status_code == 404:
                    if post > starting_post_id:
                        post = starting_post_id - 1
                    else:
                        break
                elif status_code == 429:
                    print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} status code: 429. sleeping for 60 seconds.')
                    await asyncio.sleep(60)
                    continue
                else:
                    print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Unexpected status code {status_code} for post ID {post}')
            post += 1
            await asyncio.sleep(10)

        for hidden_post_id in hidden_posts:
            status_code = await check_for_updates(hidden_post_id)
            while status_code == 401:
                await asyncio.sleep(10)
                status_code = await check_for_updates(hidden_post_id)

            if status_code != post_statuses.get(str(hidden_post_id)):
                if status_code == 200:
                    await notify_new_post(hidden_post_id, status_code)
                elif status_code != 404:
                    print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Unexpected status code {status_code} for post ID {hidden_post_id}')
                post_statuses[str(hidden_post_id)] = status_code
                save_post_statuses(post_statuses)

        await asyncio.sleep(10)
@client.event
async def on_ready():
    print('Bot is ready.')
    task1 = asyncio.create_task(run_update_check(post_id))
    task2 = asyncio.create_task(find_hidden_posts(post_id + 1, num_ids_to_check))
    await asyncio.gather(task1, task2)
client.run(os.getenv('DISCORD_TOKEN'))
