from __future__ import annotations

from aiohttp.web import BaseRequest, Response, FileResponse
from config import ADMIN_PASSWD


def params_verif_factory(required: list[str], admin_verif=False):
    def params_verif(function):
        async def wrapper(request: BaseRequest, *args, **kwargs) -> Response | FileResponse:
            query = request.query
            print(query)
            result = (len(set(required) & set(query.keys())) != len(required)
                      or (query.get("admin_passwd", "") != ADMIN_PASSWD and admin_verif))

            return await function(result, request, *args, **kwargs)
        return wrapper
    return params_verif
