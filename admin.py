from __future__ import annotations

from aiohttp.web import Request, Response, FileResponse, json_response, HTTPSeeOther
from utils import admin_auth, replace_banner_filename
from database import db
from edit_db import set_torrent, set_user, delete_torrent, delete_user


@admin_auth
async def admin_homepage(request: Request) -> Response:
    with open("./content/admin.html") as admin_page:
        user_list = await db.list("user_")
        torrent_list = await db.list("torrent_")

        async def create_list(action: str, params: list[str], param_name: str):
            return "".join([f"<li>"
                            f"    <form action=\"{action}\" method=\"post\" class=\"field-row\">"
                            f"        <label for=\"{param_name}\">"
                            f"            {(value := (await db.get(param))[param_name])}"
                            f"        </label>"
                            f"        <input type=\"hidden\" "
                            f"               value=\"{value}\" "
                            f"               id=\"{param_name}\" "
                            f"               name=\"{param_name}\"/>"
                            f"        <button>Delete</button>"
                            f"    </form>"
                            f"</li>" for param in params])

        torrent_list = await create_list("/admin/delete_torrent", torrent_list, "info_hash")
        user_list = await create_list("/admin/delete_user", user_list, "name")

        admin_page = admin_page.read()\
            .replace("%%USER_LIST", user_list)\
            .replace("%%TORRENT_LIST", torrent_list)

        return Response(body=replace_banner_filename(admin_page),
                        content_type="text/html")


@admin_auth
async def admin_post(request: Request) -> Response | FileResponse:
    instruction = request.match_info["instruction"]
    query = await request.post()

    if instruction == "create_user":
        await set_user(query["username"], query["passwd"])
    elif instruction == "delete_all":
        for key in await db.keys():
            await db.delete(key)
    elif instruction == "register_hash":
        await set_torrent(query["info_hash"])
    elif instruction == "delete_torrent":
        await delete_torrent(query["info_hash"])
    elif instruction == "delete_user":
        await delete_user(query["name"])
    elif instruction == "dump_db":
        return json_response(await db.to_dict())

    return HTTPSeeOther("/admin")
