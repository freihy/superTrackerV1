import discord
import asyncio
import json
import datetime
import threading
from discord.ext import tasks, commands
from MultiTrack import MultiTracker
from PrintTime import print_time

# Load from json
SETUP_CONFIGS = json.load(open('config.json'))
TOKEN = SETUP_CONFIGS["TOKEN"]   						# Your discord bot token from the Discord Developers Portal
APP_ID = SETUP_CONFIGS["APP_ID"]
GUILD_ID = SETUP_CONFIGS["GUILD_ID"]
PREFIX = SETUP_CONFIGS["PREFIX"]                        # Prefix for commands (Not needed)
MINS = int(SETUP_CONFIGS["MINS"])-1                            # How often to check for new listings
CHANNEL_TO_SEND = SETUP_CONFIGS["CHANNEL_TO_SEND"]      # Paste your channel ID here
TO_PING = SETUP_CONFIGS["TO_PING"]                      # Your Discord ID (Found by clicking on your message > Copy ID)

class MyClient(commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix = PREFIX,
		 	intents=discord.Intents.all(),
		 	application_id = APP_ID)
		self.countdown = 0
		self.listing_result = None
		self.new_listing_results = []
		self.tracker_instance = None

	async def setup_hook(self) -> None:
		self.loop.create_task(self.scraper())
		await client.tree.sync(guild = discord.Object(id=GUILD_ID))

	async def on_ready(self):
		print(f'{client.user} is online!')
		channel = self.get_channel(int(CHANNEL_TO_SEND))
		await channel.send(f"I am alive!")

	async def scraper(self):
		await self.wait_until_ready()						# Wait till bot is initialised
		channel = self.get_channel(int(CHANNEL_TO_SEND))	# Get channel to send messages to 

		while not self.is_closed():
			do = False
			if self.countdown <= 0:
				self.countdown = MINS
				do = True
			else:
				self.countdown -= 1
				await channel.purge(limit=1)
				if self.countdown+1 > 1:
					await channel.send(f'Scraping again in {self.countdown+1} minutes.')
				else:
					await channel.send(f'Scraping again in a minute.')
			if do:
				def start_scraping():
					self.tracker_instance = MultiTracker()
					self.listing_result = self.tracker_instance .do_jobs()

				def update_db_and_local():
					self.new_listing_results = self.tracker_instance .find_new_listings(self.listing_result)
					self.tracker_instance .update_stalking_list(self.listing_result)

				await channel.purge(limit=1)
				await channel.send("Scraping...")
				start_scraping()
				await channel.purge(limit=1)
				await channel.send("Finished scraping, updating database...")
				update_db_and_local()
				await channel.purge(limit=1)

				if len(self.new_listing_results) != 0:
				    await channel.send(f'**------------------------------------------------------**\n**NEW LISTINGS FOUND:**\n')
				    await channel.send(self.tracker_instance.print_results(self.new_listing_results))
				    await channel.send(f'**------------------------------------------------------**\n')
				    await channel.purge(limit=1)
				    await channel.send("Scraping Completed :D")
				    if TO_PING != None:
				        await channel.send(TO_PING)
				else:
					await channel.send("Nothing new found D:")

			await asyncio.sleep(60)


client = MyClient()

@client.tree.command(name="ping", description="wow much test")
async def ping(interaction: discord.Interaction):
	await interaction.response.send_message("ponggers")

client.run(TOKEN)