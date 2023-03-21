# check-csgo-api-post-status
Sends a discord message when the csgo api returns a 200 code(request successful) on a specific post id (Source 2 blog post)
now also runs through the next 100 ids for hidden data.

https://www.python.org/downloads/

python3 -m pip install -U discord.py

python3 pip install beautifulsoup4

python3 pip install python.dotenv

Create a .env file with the following data:

SERVER_ID=0123456789

CHANNEL_ID=0123456789

ROLE_ID=0123456789

DISCORD_TOKEN=YOUR_BOT_TOKEN

python3 api.py
