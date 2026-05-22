import asyncio

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import (
    ADMINS, AUTO_DELETE_MSG, AUTO_DELETE_TIME, CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON, FORCE_MSG, JOIN_REQUEST_ENABLE,
    FORCE_SUB_CHANNEL, PROTECT_CONTENT, START_MSG, START_PIC,
)
from database.database import add_user, del_user, full_userbase, present_user
from helper_func import decode, delete_file, get_messages, subscribed

WAIT_MSG   = "<b>Processing …</b>"
REPLY_ERROR = "<code>Use this command as a reply to any Telegram message.</code>"


# ── /start (subscribed users) ─────────────────────────────────────────────────

@Bot.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    uid = message.from_user.id
    if not await present_user(uid):
        try:
            await add_user(uid)
        except Exception:
            pass

    text = message.text
    if len(text) > 7:
        # Deep-link: decode and fetch files
        try:
            b64 = text.split(" ", 1)[1]
        except IndexError:
            return

        string = await decode(b64)
        parts = string.split("-")

        if len(parts) == 3:
            try:
                start = int(int(parts[1]) / abs(client.db_channel.id))
                end   = int(int(parts[2]) / abs(client.db_channel.id))
            except Exception:
                return
            ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
        elif len(parts) == 2:
            try:
                ids = [int(int(parts[1]) / abs(client.db_channel.id))]
            except Exception:
                return
        else:
            return

        temp = await message.reply("Please wait…")
        try:
            messages = await get_messages(client, ids)
        except Exception:
            await message.reply("Something went wrong!")
            return
        await temp.delete()

        track_msgs = []
        for msg in messages:
            caption = (
                CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name if msg.document else "",
                )
                if CUSTOM_CAPTION and msg.document
                else ("" if not msg.caption else msg.caption.html)
            )
            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                try:
                    copied = await msg.copy(
                        chat_id=uid, caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT,
                    )
                    track_msgs.append(copied)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    copied = await msg.copy(
                        chat_id=uid, caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT,
                    )
                    track_msgs.append(copied)
                except Exception:
                    pass
            else:
                try:
                    await msg.copy(
                        chat_id=uid, caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT,
                    )
                    await asyncio.sleep(0.5)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await msg.copy(
                        chat_id=uid, caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT,
                    )
                except Exception:
                    pass

        if track_msgs:
            notice = await client.send_message(
                chat_id=uid,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME),
            )
            asyncio.create_task(delete_file(track_msgs, client, notice))
        return

    # Normal /start (no payload)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("😊 About Me", callback_data="about"),
            InlineKeyboardButton("🔒 Close",    callback_data="close"),
        ]
    ])
    fmt = dict(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else "@" + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id,
    )
    if START_PIC:
        await message.reply_photo(photo=START_PIC, caption=START_MSG.format(**fmt),
                                  reply_markup=buttons, quote=True)
    else:
        await message.reply_text(text=START_MSG.format(**fmt), reply_markup=buttons,
                                 disable_web_page_preview=True, quote=True)


# ── /start (not subscribed) ───────────────────────────────────────────────────

@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Client, message: Message):
    if JOIN_REQUEST_ENABLE:
        inv = await client.create_chat_invite_link(
            chat_id=FORCE_SUB_CHANNEL, creates_join_request=True
        )
        url = inv.invite_link
    else:
        url = client.invitelink

    buttons = [[InlineKeyboardButton("Join Channel", url=url)]]
    try:
        buttons.append([
            InlineKeyboardButton(
                "Try Again",
                url=f"https://t.me/{client.username}?start={message.command[1]}",
            )
        ])
    except IndexError:
        pass

    fmt = dict(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else "@" + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id,
    )
    await message.reply(
        text=FORCE_MSG.format(**fmt),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True,
    )


# ── /users (admin) ────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("users") & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await message.reply(WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"<b>{len(users)}</b> users are using this bot.")


# ── /broadcast (admin) ────────────────────────────────────────────────────────

@Bot.on_message(filters.command("broadcast") & filters.private & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if not message.reply_to_message:
        err = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await err.delete()
        return

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total = successful = blocked = deleted = unsuccessful = 0

    notice = await message.reply("<i>Broadcasting… this may take a while.</i>")
    for chat_id in query:
        try:
            await broadcast_msg.copy(chat_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await broadcast_msg.copy(chat_id)
            successful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except Exception:
            unsuccessful += 1
        total += 1

    await notice.edit(
        f"<b><u>Broadcast Complete</u>\n\n"
        f"Total: <code>{total}</code>\n"
        f"Successful: <code>{successful}</code>\n"
        f"Blocked: <code>{blocked}</code>\n"
        f"Deleted: <code>{deleted}</code>\n"
        f"Failed: <code>{unsuccessful}</code></b>"
    )
