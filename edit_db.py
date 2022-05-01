from __future__ import annotations

from database import db
from aiohttp.web import Request, Response, FileResponse, json_response
from utils import params_verif_factory


@params_verif_factory(["user", "passwd"], True)
async def create_user(result: bool, request: Request) -> Response | FileResponse:
    query = request.query

    if result:
        return FileResponse("./content/403.html", status=403)

    await db.set(query["user"], {
        "passwd": query["passwd"]
    })

    return Response(text=f"Created user {query['user']} successfully!")


@params_verif_factory([], True)
async def erase_db(result: bool, request: Request) -> Response | FileResponse:
    if result:
        return FileResponse("./content/403.html", status=403)

    for key in await db.keys():
        await db.delete(key)

    return Response(text="Done :>")


@params_verif_factory(["info_hash"], True)
async def register_hash(result: bool, request: Request) -> Response | FileResponse:
    if result:
        return FileResponse("./content/403.html", status=403)

    await db.set(f"hash_{request.query['info_hash']}", {
        "complete": [],
        "incomplete": [],
        "peers": []
    })

    return Response(text="Done :3")


@params_verif_factory([], True)
async def dump_db(result: bool, request: Request) -> Response | FileResponse:
    if result:
        return FileResponse("./content/403.html", status=403)

    return json_response(await db.to_dict())
