# Ayra - UserBot
# Copyright (C) 2021-2022 Teamayra
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/senpai80/Ayra/blob/main/LICENSE>.

import inspect
import re
from traceback import format_exc

from telethon import Button
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery, NewMessage
from telethon.tl.types import InputWebDocument

from .. import LOGS, asst, udB, ayra_bot
from ..fns.admins import admin_check
from . import append_or_update, owner_and_sudos

OWNER = ayra_bot.full_name

MSG = f"""
**ᴀʏʀᴀ ꭙ ᴜꜱᴇʀʙᴏᴛ​**
➖➖➖➖➖➖➖➖➖➖
**Owner**: [{OWNER}](tg://user?id={ayra_bot.uid})
**Support**: @stufsupport
➖➖➖➖➖➖➖➖➖➖
"""

IN_BTTS = [
    [
        Button.url(
            "Repository",
            url="https://github.com/senpai80/ayra",
        ),
        Button.url("Support", url="https://t.me/stufsupport"),
    ]
]


# decorator for assistant


def asst_cmd(pattern=None, load=None, owner=False, **kwargs):
    """Decorator for assistant's command"""
    name = inspect.stack()[1].filename.split("/")[-1].replace(".py", "")
    kwargs["forwards"] = False

    def ayra(func):
        if pattern:
            kwargs["pattern"] = re.compile(f"^/{pattern}")
        if owner:
            kwargs["from_users"] = owner_and_sudos
        asst.add_event_handler(func, NewMessage(**kwargs))
        if load is not None:
            append_or_update(load, func, name, kwargs)

    return ayra


def callback(data=None, from_users=[], admins=False, owner=False, **kwargs):
    """Assistant's callback decorator"""
    if "me" in from_users:
        from_users.remove("me")
        from_users.append(ayra_bot.uid)

    def ayra(func):
        async def wrapper(event):
            if admins and not await admin_check(event):
                return
            if from_users and event.sender_id not in from_users:
                return await event.answer("Not for You!", alert=True)
            if owner and event.sender_id not in owner_and_sudos():
                return await event.answer(f"This is {OWNER}'s bot!!")
            try:
                await func(event)
            except Exception as er:
                LOGS.exception(er)

        asst.add_event_handler(wrapper, CallbackQuery(data=data, **kwargs))

    return ayra


def in_pattern(pattern=None, owner=False, **kwargs):
    """Assistant's inline decorator."""

    def don(func):
        async def wrapper(event):
            if owner and event.sender_id not in owner_and_sudos():
                res = [
                    await event.builder.article(
                        title="ᴀʏʀᴀ ꭙ ᴜꜱᴇʀʙᴏᴛ​",
                        url="https://t.me/stufsupport​",
                        description="©↻ꝛɪᴢ",
                        text=MSG,
                        thumb=InputWebDocument(
                            "https://graph.org/file/02f9ca4617cec58377b9d.jpg",
                            0,
                            "image/jpeg",
                            [],
                        ),
                        buttons=IN_BTTS,
                    )
                ]
                return await event.answer(
                    res,
                    switch_pm=f"🤖: Assistant of {OWNER}",
                    switch_pm_param="start",
                )
            try:
                await func(event)
            except QueryIdInvalidError:
                pass
            except Exception as er:
                err = format_exc()

                def error_text():
                    return f"**#ERROR #INLINE**\n\nQuery: `{asst.me.username} {pattern}`\n\n**Traceback:**\n`{format_exc()}`"

                LOGS.exception(er)
                try:
                    await event.answer(
                        [
                            await event.builder.article(
                                title="Unhandled Exception has Occured!",
                                text=error_text(),
                                buttons=Button.url(
                                    "Report", "https://t.me/stufsupport"
                                ),
                            )
                        ]
                    )
                except QueryIdInvalidError:
                    LOGS.exception(err)
                except Exception as er:
                    LOGS.exception(er)
                    await asst.send_message(udB.get_key("LOG_CHANNEL"), error_text())

        asst.add_event_handler(wrapper, InlineQuery(pattern=pattern, **kwargs))

    return don
