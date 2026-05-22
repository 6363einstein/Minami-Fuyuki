import sys
from datetime import datetime

from aiohttp import web
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import (
    API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS,
    FORCE_SUB_CHANNEL, CHANNEL_ID, PORT,
)
from plugins import web_server

ASCII_ART = """
╔═╗╦╦  ╔═╗  ╔═╗╦ ╦╔═╗╦═╗╦╔╗╔╔═╗  ╔╗ ╔═╗╔╦╗
╠╣ ║║  ║╣   ╚═╗╠═╣╠═╣╠╦╝║║║║║ ╦  ╠╩╗║ ║ ║ 
╚  ╩╩═╝╚═╝  ╚═╝╩ ╩╩ ╩╩╚═╩╝╚╝╚═╝  ╚═╝╚═╝ ╩ 
"""


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = datetime.now()
        self.username = me.username

        # ── Force-subscribe setup ─────────────────────────────────────────────
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as e:
                self.LOGGER(__name__).warning(e)
                self.LOGGER(__name__).warning(
                    "Cannot export invite link from FORCE_SUB_CHANNEL. "
                    "Make sure the bot is admin with 'Invite Users' permission."
                )
                sys.exit(1)

        # ── DB channel test ───────────────────────────────────────────────────
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="✅ Bot started successfully!")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(
                f"Make sure the bot is Admin in DB Channel. Current CHANNEL_ID: {CHANNEL_ID}"
            )
            sys.exit(1)

        self.set_parse_mode(ParseMode.HTML)
        print(ASCII_ART)
        self.LOGGER(__name__).info(f"Bot @{self.username} is running!")

        # ── Start aiohttp web server (keeps Render alive) ─────────────────────
        runner = web.AppRunner(await web_server())
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", PORT).start()
        self.LOGGER(__name__).info(f"Web server started on port {PORT}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
