import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode


@Bot.on_message(
    filters.private
    & filters.user(ADMINS)
    & ~filters.command(["start", "users", "broadcast", "batch", "genlink", "stats"])
)
async def channel_post(client: Client, message: Message):
    """Admin sends a file → bot copies to DB channel and returns a share link."""
    reply = await message.reply("Please wait…", quote=True)
    try:
        post = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        await reply.edit(f"Something went wrong: <code>{e}</code>")
        return

    converted_id = post.id * abs(client.db_channel.id)
    b64 = await encode(f"get-{converted_id}")
    link = f"https://t.me/{client.username}?start={b64}"
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )
    await reply.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=markup,
                     disable_web_page_preview=True)

    if not DISABLE_CHANNEL_BUTTON:
        try:
            await post.edit_reply_markup(markup)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await post.edit_reply_markup(markup)
        except Exception:
            pass


@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    """Auto-add share button to new channel posts."""
    if DISABLE_CHANNEL_BUTTON:
        return
    converted_id = message.id * abs(client.db_channel.id)
    b64 = await encode(f"get-{converted_id}")
    link = f"https://t.me/{client.username}?start={b64}"
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )
    try:
        await message.edit_reply_markup(markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_reply_markup(markup)
    except Exception:
        pass
