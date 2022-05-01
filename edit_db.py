from __future__ import annotations

from database import db
from aiohttp.web import Request, Response, FileResponse, json_response
from utils import params_verif_factory, admin_auth, error_page


@admin_auth
@params_verif_factory(["user", "passwd"])
async def create_user(result: bool, request: Request) -> Response | FileResponse:
    query = request.query

    if result:
        return error_page("Missing parameters")

    await db.set(query["user"], {
        "passwd": query["passwd"]
    })

    return Response(text=f"Created user {query['user']} successfully!")


@admin_auth
async def erase_db(request: Request) -> Response | FileResponse:
    for key in await db.keys():
        await db.delete(key)

    return Response(text="Done :>")


@admin_auth
@params_verif_factory(["info_hash"])
async def register_hash(result: bool, request: Request) -> Response | FileResponse:
    if result:
        return error_page("Missing parameters")

    await db.set(f"hash_{request.query['info_hash']}", {
        "complete": [],
        "incomplete": [],
        "peers": []
    })

    return Response(text="Done :3")


@admin_auth
async def dump_db(request: Request) -> Response | FileResponse:
    return json_response(await db.to_dict())
