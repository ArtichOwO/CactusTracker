from __future__ import annotations

from database import db
from aiohttp.web import Request, Response, FileResponse, json_response
from utils import params_verif_factory, admin_auth, error_page


@admin_auth
async def create_user(request: Request) -> Response | FileResponse:
    query = await request.post()

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
async def register_hash(request: Request) -> Response | FileResponse:
    query = request.post()

    await db.set(f"hash_{request.query['info_hash']}", {
        "complete": [],
        "incomplete": [],
        "peers": []
    })

    return Response(text="Done :3")


@admin_auth
async def dump_db(request: Request) -> Response | FileResponse:
    return json_response(await db.to_dict())
