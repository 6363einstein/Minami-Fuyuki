from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch(client: Client, message: Message):
    """Generate a link for a range of DB-channel messages."""
    # First message
    while True:
        try:
            first_msg = await client.ask(
                chat_id=message.from_user.id,
                text="Forward the <b>first</b> message from DB Channel (with quotes), "
                     "or send its t.me link.",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        f_id = await get_message_id(client, first_msg)
        if f_id:
            break
        await first_msg.reply("❌ That post is not from my DB Channel. Try again.")

    # Last message
    while True:
        try:
            last_msg = await client.ask(
                chat_id=message.from_user.id,
                text="Now forward the <b>last</b> message from DB Channel (with quotes), "
                     "or send its t.me link.",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        l_id = await get_message_id(client, last_msg)
        if l_id:
            break
        await last_msg.reply("❌ That post is not from my DB Channel. Try again.")

    b64 = await encode(
        f"get-{f_id * abs(client.db_channel.id)}-{l_id * abs(client.db_channel.id)}"
    )
    link = f"https://t.me/{client.username}?start={b64}"
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )
    await last_msg.reply(f"<b>Here is your batch link</b>\n\n{link}",
                         reply_markup=markup, quote=True)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def link_generator(client: Client, message: Message):
    """Generate a link for a single DB-channel message."""
    while True:
        try:
            channel_msg = await client.ask(
                chat_id=message.from_user.id,
                text="Forward a message from DB Channel (with quotes), or send its t.me link.",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        msg_id = await get_message_id(client, channel_msg)
        if msg_id:
            break
        await channel_msg.reply("❌ That post is not from my DB Channel. Try again.")

    b64 = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={b64}"
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )
    await channel_msg.reply(f"<b>Here is your link</b>\n\n{link}",
                             reply_markup=markup, quote=True)
