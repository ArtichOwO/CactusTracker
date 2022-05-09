from __future__ import annotations
from typing import Callable

from aiohttp.web import Request, Response, FileResponse
from config import ADMIN_PASSWD, ADMIN_USERNAME
from base64 import b64decode
from random import choice
import os


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


def params_verif_factory(required: list):
    def params_verif(function: Callable):
        async def wrapper(request: Request) -> Response | FileResponse:
            result = len(set(required) & set(request.query.keys())) != len(required)

            return await function(result, request)
        return wrapper
    return params_verif


def error_page(error: str, status=200, headers=None) -> Response:
    with open("content/error.html") as error_file:
        return Response(body=replace_banner_filename(error_file.read().replace("%%ERROR_STRING", error)),
                        status=status, headers=headers,
                        content_type="text/html")


def replace_banner_filename(content: str) -> bytes:
    banners: list[str] = os.listdir("./content/banners")
    return bytes(content.replace("%%BANNER_FILENAME", choice(banners)), "utf8")


def decode_hash(info_hash: str) -> str:
    info_hash = [char for char in info_hash]
    result = ""

    while info_hash:
        if (char := info_hash.pop(0)) == "%":
            result += hex(int(info_hash.pop(0) + info_hash.pop(0), 16))[2:].rjust(2, "0")
        else:
            result += hex(ord(char))[2:].rjust(2, "0")

    return result
