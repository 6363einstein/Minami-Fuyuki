from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from bot import Bot
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT
from helper_func import get_readable_time


@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    delta = datetime.now() - bot.uptime
    await message.reply(BOT_STATS_TEXT.format(uptime=get_readable_time(int(delta.total_seconds()))))


@Bot.on_message(filters.private & filters.incoming)
async def catch_all(_: Bot, message: Message):
    if USER_REPLY_TEXT:
        await message.reply(USER_REPLY_TEXT)
