import logging
from datetime import timedelta

import discord

import config
from reputation import get_reputation

log =logging.getLogger("rep-bot")


async def react(message: discord.Message, emoji: str):
    try:
        await message.add_reaction(emoji)
    except discord.HTTPException as e:
        log.warning("Couldn't react to message %s: %s", message.id, e.text)


async def reply(message: discord.Message, text: str):
    try:
        await message.reply(text)
    except discord.HTTPException as e:
        log.warning("Couldn't reply to message %s: %s", message.id, e.text)


async def timeout(member: discord.Member, duration: timedelta, reason: str | None = None):
    """`reason` shows up in the server's audit log. discord caps timeouts at 28 days"""
    try:
        await member.timeout(min(duration, timedelta(days=28)), reason=reason)
    except discord.HTTPException as e:  # e.g. the bot is missing Moderate Members or the member outranks it
        log.warning("Couldn't time out %s: %s", member, e.text)


async def kick(member: discord.Member, reason: str | None = None):
    """`reason` shows up in the server's audit log"""
    try:
        await member.kick(reason=reason)
    except discord.HTTPException as e:  # e.g. the bot is missing Kick Members or the member outranks it
        log.warning("Couldn't kick %s: %s", member, e.text)


async def respond(message: discord.Message, score: float):
    """react to messages that score low enough to get flagged"""
    if score <= config.FLAG_THRESHOLD:
        await react(message, "🤨")
        await react(message, "🚩")


