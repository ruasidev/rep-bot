import logging
import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from reputation import get_reputation, get_reputation_change

load_dotenv()
TOKEN = os.getenv("TOKEN")
TESTING = bool(os.getenv("TESTING"))

MAX_STARS = 5
REP_CHANGE_MONTHS = 3
EMOJI_DIR = Path(__file__).parent / "assets" / "emojis"

log = logging.getLogger("rep-bot")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

star_emojis: dict[str, str] = {}


async def load_star_emojis():
    existing = {emoji.name: emoji for emoji in await bot.fetch_application_emojis()}
    for name in ("star_full", "star_half", "star_empty"):
        emoji = existing.get(name)
        if emoji is None:
            image = (EMOJI_DIR / f"{name}.png").read_bytes()
            emoji = await bot.create_application_emoji(name=name, image=image)
            log.info("Uploaded emoji %s", name)
        star_emojis[name] = str(emoji)


def star_row(rating: float) -> str:
    full = int(rating)
    half = int(rating - full >= 0.5)
    empty = MAX_STARS - full - half
    return (
        star_emojis["star_full"] * full
        + star_emojis["star_half"] * half
        + star_emojis["star_empty"] * empty
    )


@bot.event
async def setup_hook():
    await load_star_emojis()
    synced = await bot.tree.sync()
    log.info("Synced %d slash command(s)", len(synced))


@bot.event
async def on_ready():
    log.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    log.info(f"Testing mode is {"on" if TESTING else "off"}")


@bot.tree.command(name="ping", description="Check that the bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")


@bot.tree.command(name="rep", description="Check the reputation of a user")
@app_commands.describe(target="The user you want to check the reputation of")
async def rep(interaction: discord.Interaction, target: discord.Member):
    rating = get_reputation(target.id)
    change = get_reputation_change(target.id, REP_CHANGE_MONTHS)

    embed = discord.Embed(
        title=f"@{target.name}'s reputation",
        description="## " + star_row(rating),
    )
    arrow = "🔺" if change >= 0 else "🔻"
    embed.set_footer(text=f"{change:+d} {arrow} in {REP_CHANGE_MONTHS} months")

    # if TESTING=1 set in `.env`, `/rep` will not be ephemeral
    await interaction.response.send_message(embed=embed, ephemeral=(not TESTING))    # may set ephemeral=True 


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("TOKEN is not set, pls add it to .env")
    bot.run(TOKEN, root_logger=True)
