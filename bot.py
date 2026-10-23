import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

log = logging.getLogger("rep-bot")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def setup_hook():
    synced = await bot.tree.sync()
    log.info("Synced %d slash command(s)", len(synced))


@bot.event
async def on_ready():
    log.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)


@bot.tree.command(name="ping", description="Check that the bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("TOKEN is not set, pls add it to .env")
    bot.run(TOKEN, root_logger=True)
