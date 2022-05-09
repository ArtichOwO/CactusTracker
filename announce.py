from __future__ import annotations

from bencode3 import bencode
from aiohttp.web import Request, Response
from utils import params_verif_factory, decode_hash
from edit_db import set_torrent, get_torrent, get_user


@params_verif_factory(["info_hash", "peer_id", "port", "left", "compact"])
async def announce(result: bool, request: Request) -> Response:
    username = request.match_info["username"]
    passwd = request.match_info["passwd"]
    ip_addr = request.match_info["ip_addr"]

    if result:
        return_content = {
            "failure code": "900",
            "failure reason": "Missing parameters"
        }
    else:
        try:
            user: dict = await get_user(username)

            if user["passwd"] != passwd:
                return_content = {
                    "failure code": "900",
                    "failure reason": "Wrong password"
                }
            else:
                try:
                    info_hash = dict([(param.split("=")[0], param.split("=")[1])
                                      for param in request.query_string.split("&")])["info_hash"]
                    info_hash = decode_hash(info_hash)

                    torrent: dict = await get_torrent(info_hash)

                    old_peers: list = []

                    for peer in torrent["peers"]:
                        if peer["ip"] != ip_addr:
                            old_peers.append(peer)

                    complete = [ip for ip in torrent["complete"] if ip != ip_addr]
                    incomplete = [ip for ip in torrent["incomplete"] if ip != ip_addr]

                    if request.query["left"] == "0":
                        complete.append(ip_addr)
                    else:
                        incomplete.append(ip_addr)

                    new_peers = old_peers + [{
                        "peer_id": request.query["peer_id"],
                        "ip": ip_addr,
                        "port": request.query["port"]
                    }]

                    await set_torrent(info_hash, complete, incomplete, new_peers)

                    peers: list[dict] | bytes = new_peers

                    if request.query["compact"] == "1":
                        compact_peers = b""

                        for peer in peers:
                            for digit in peer["ip"].split("."):
                                compact_peers += int(digit).to_bytes(1, "big")
                            compact_peers += int(peer["port"]).to_bytes(2, "big")

                        peers = compact_peers

                    return_content = {
                        "complete": len(complete),
                        "incomplete": len(incomplete),
                        "interval": 15,
                        "peers": peers
                    }
                except KeyError:
                    return_content = {
                        "failure code": "900",
                        "failure reason": "Hash not registered"
                    }
        except KeyError:
            return_content = {
                "failure code": "900",
                "failure reason": "User does not exist"
            }

    return Response(body=bencode(return_content))
