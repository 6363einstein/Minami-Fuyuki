import base64
import re
import asyncio
import logging

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from config import FORCE_SUB_CHANNEL, ADMINS, AUTO_DELETE_TIME, AUTO_DEL_SUCCESS_MSG


# ── Force-subscribe filter ────────────────────────────────────────────────────

async def is_subscribed(filter, client, update):
    if not FORCE_SUB_CHANNEL:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
    except UserNotParticipant:
        return False
    return member.status in (
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.MEMBER,
    )


subscribed = filters.create(is_subscribed)


# ── Base64 helpers ────────────────────────────────────────────────────────────

async def encode(string: str) -> str:
    b64 = base64.urlsafe_b64encode(string.encode("ascii"))
    return b64.decode("ascii").strip("=")


async def decode(b64_string: str) -> str:
    b64_string = b64_string.strip("=")
    padded = b64_string + "=" * (-len(b64_string) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")


# ── Message fetching ──────────────────────────────────────────────────────────

async def get_messages(client, message_ids):
    messages = []
    total = 0
    while total < len(message_ids):
        batch = message_ids[total: total + 200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=batch,
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=batch,
            )
        total += len(batch)
        messages.extend(msgs)
    return messages


async def get_message_id(client, message):
    """Return the DB-channel message id from a forwarded post or t.me link."""
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0
    if message.forward_sender_name:
        return 0
    if message.text:
        pattern = r"https://t\.me/(?:c/)?(.+?)/(\d+)"
        m = re.match(pattern, message.text)
        if not m:
            return 0
        channel_id, msg_id = m.group(1), int(m.group(2))
        if channel_id.isdigit():
            return msg_id if f"-100{channel_id}" == str(client.db_channel.id) else 0
        return msg_id if channel_id == client.db_channel.username else 0
    return 0


# ── Readable uptime ───────────────────────────────────────────────────────────

def get_readable_time(seconds: int) -> str:
    parts = []
    for unit, mod in [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]:
        val, seconds = divmod(seconds, mod)
        if val:
            parts.append(f"{val}{unit}")
    return " ".join(parts) or "0s"


# ── Auto-delete ───────────────────────────────────────────────────────────────

async def delete_file(messages, client, process):
    await asyncio.sleep(AUTO_DELETE_TIME)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            logging.warning(f"Could not delete message {msg.id}: {e}")
    await process.edit_text(AUTO_DEL_SUCCESS_MSG)
