from __future__ import annotations

import logging
import asyncio
import os
from aiohttp import web
from aiohttp.web import Request, Response, FileResponse

from announce import announce
from utils import error_page, replace_banner_filename
from admin import admin_homepage, admin_post
from database import db


HOST = "0.0.0.0"
PORT = 80
CONTENT_PATH = "./content"


def create_error_middleware():
    @web.middleware
    async def error_middleware(request: Request, handler):
        try:
            return await handler(request)
        except web.HTTPException as ex:
            return error_page(ex.text, ex.status_code)
    return error_middleware


async def res_handler(request: Request) -> Response | FileResponse:
    if os.path.exists(f"./content/{request.match_info['path']}"):
        return FileResponse(f"./content/{request.match_info['path']}")
    else:
        return error_page("404: Not found :(", 404)


async def index(request: Request) -> Response:
    with open("./content/index.html") as index_file:
        index_file = index_file.read()

        user_list = await db.list("user_")
        user_list = "".join([f"<li>{(await db.get(user))['name']}</li>" for user in user_list])
        torrent_list = await db.list("torrent_")
        torrent_list = "".join([f"<li>"
                                f"    <details>"
                                f"        <summary>{(value := await db.get(torrent))['meta']['name']}</summary>"
                                f"        <li>Description: {value['meta']['description']}</li>"
                                f"        <li>Created by: {value['meta']['username']}</li>"
                                f"        <li>Hash: {value['info_hash']}</li>"
                                f"        <li>Seed: {len(value['complete'])}</li>"
                                f"        <li>Leech: {len(value['incomplete'])}</li>"
                                f"    </details>"
                                f"</li>" for torrent in torrent_list])

        index_file = index_file.replace("%%USER_LIST", f"<ul>{user_list}</ul>")\
                               .replace("%%TORRENT_LIST", f"<ul>{torrent_list}</ul>")

        return Response(body=replace_banner_filename(index_file),
                        content_type="text/html")


async def run_web_server():
    app = web.Application(middlewares=[create_error_middleware()])
    app.add_routes([
        web.post("/admin/{instruction}", admin_post),
        web.get("/admin", admin_homepage),
        web.get("/announce/{username}/{passwd}/{ip_addr}", announce),
        web.get("/", index),
        web.get("/{path:.+}", res_handler)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Server starting")
    loop = asyncio.get_event_loop()
    loop.create_task(run_web_server())
    loop.run_forever()
