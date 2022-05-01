import logging
import asyncio
from aiohttp import web
from aiohttp.web import Request

from announce import announce
from edit_db import create_user, erase_db, register_hash, dump_db
from utils import error_page


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


async def run_web_server():
    app = web.Application(middlewares=[create_error_middleware()])
    app.add_routes([web.post("/create_user", create_user),
                    web.post("/delete_all", erase_db),
                    web.post("/register_hash", register_hash),
                    web.get("/dump_db", dump_db),
                    web.get("/announce/{username}/{passwd}/{ip_addr}", announce),
                    web.get("/", (lambda req: web.FileResponse("./content/index.html")))])
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

