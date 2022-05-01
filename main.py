import logging
import asyncio
from aiohttp import web

from announce import announce
from edit_db import create_user, erase_db, register_hash, dump_db


HOST = "0.0.0.0"
PORT = 80
CONTENT_PATH = "./content"


async def run_web_server():
    app = web.Application()
    app.add_routes([web.get("/create_user", create_user),
                    web.get("/delete_all", erase_db),
                    web.get("/register_hash", register_hash),
                    web.get("/dump_db", dump_db),
                    web.get("/announce/{username}/{passwd}/{ip_addr}", announce)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()


async def run_other_task():
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.create_task(run_web_server())
    loop.run_until_complete(run_other_task())
    loop.run_forever()

