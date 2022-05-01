from __future__ import annotations

from aiohttp.web import Request, Response, FileResponse
from config import ADMIN_PASSWD, ADMIN_USERNAME
from base64 import b64decode


def admin_auth(function):
    async def wrapper(request: Request, *args, **kwargs) -> Response | FileResponse:
        response401 = error_page("401 Unauthorized", status=401, headers={"WWW-Authenticate": "Basic"})
        
        if "Authorization" not in request.headers.keys():
            return response401
        else:
            auth = b64decode(request.headers["Authorization"].split(" ")[1]).decode("utf-8").split(":")
            if auth[0] != ADMIN_USERNAME or auth[1] != ADMIN_PASSWD:
                return response401
        
        return await function(request, *args, **kwargs)
    return wrapper


def params_verif_factory(required: list[str]):
    def params_verif(function):
        async def wrapper(request: Request, *args, **kwargs) -> Response | FileResponse:
            result = len(set(required) & set(request.query.keys())) != len(required)

            return await function(result, request, *args, **kwargs)
        return wrapper
    return params_verif


def error_page(error: str, status=200, headers=None) -> Response:
    with open("./content/error_top.html", "rb") as error_top:
        error_top = error_top.read()

    with open("./content/error_bottom.html", "rb") as error_bottom:
        error_bottom = error_bottom.read()

    return Response(body=error_top+bytes(error, "utf8")+error_bottom,
                    status=status, headers=headers,
                    content_type="text/html")
