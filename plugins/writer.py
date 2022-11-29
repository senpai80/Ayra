# Ayra - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/Ayra/blob/main/LICENSE/>.
"""
◈ Perintah Tersedia

• `{i}write <text or reply to text>`
   Itu akan menulis di atas kertas.

• `{i}image <text or reply to html or any doc file>`
   Tulis gambar dari html atau teks apa pun.
"""

import os

from htmlwebshot import WebShot
from PIL import Image, ImageDraw, ImageFont

from . import async_searcher, eod, get_string, text_set, ayra_cmd


@ayra_cmd(pattern="gethtml( (.*)|$)")
async def ghtml(e):
    if txt := e.pattern_match.group(1).strip():
        link = e.text.split(maxsplit=1)[1]
    else:
        return await eod(e, "`Balas file apa pun atau memberikan teks apa pun`")
    k = await async_searcher(link)
    with open("file.html", "w+") as f:
        f.write(k)
    await e.reply(file="file.html")


@ayra_cmd(pattern="image( (.*)|$)")
async def f2i(e):
    txt = e.pattern_match.group(1).strip()
    html = None
    if txt:
        html = e.text.split(maxsplit=1)[1]
    elif e.reply_to:
        r = await e.get_reply_message()
        if r.media:
            html = await e.client.download_media(r.media)
        elif r.text:
            html = r.text
    if not html:
        return await eod(e, "`Balas file apa pun atau memberikan teks apa pun`")
    html = html.replace("\n", "<br>")
    shot = WebShot(quality=85)
    css = "body {background: white;} p {color: red;}"
    pic = await shot.create_pic_async(html=html, css=css)
    await e.reply(file=pic, force_document=True)
    os.remove(pic)
    if os.path.exists(html):
        os.remove(html)


@ayra_cmd(pattern="write( (.*)|$)")
async def writer(e):
    if e.reply_to:
        reply = await e.get_reply_message()
        text = reply.message
    elif e.pattern_match.group(1).strip():
        text = e.text.split(maxsplit=1)[1]
    else:
        return await eod(e, get_string("writer_1"))
    k = await e.eor(get_string("com_1"))
    img = Image.open("resources/extras/template.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("resources/fonts/assfont.ttf", 30)
    x, y = 150, 140
    lines = text_set(text)
    line_height = font.getsize("hg")[1]
    for line in lines:
        draw.text((x, y), line, fill=(1, 22, 55), font=font)
        y = y + line_height - 5
    file = "ayra.jpg"
    img.save(file)
    await e.reply(file=file)
    os.remove(file)
    await k.delete()