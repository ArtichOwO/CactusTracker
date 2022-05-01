from __future__ import annotations

from database import db
from bencode3 import bencode
from aiohttp.web import Request, Response
from utils import params_verif_factory


@params_verif_factory(["info_hash", "peer_id", "port", "left", "compact"])
async def announce(result: bool, request: Request) -> Response:
    username = request.match_info["username"]
    passwd = request.match_info["passwd"]

    if result:
        return_content = {
            "failure code": "900",
            "failure reason": "Missing parameters"
        }
    else:
        try:
            user: dict = await db.get(username)

            if user["passwd"] != passwd:
                return_content = {
                    "failure code": "900",
                    "failure reason": "Wrong password"
                }
            else:
                try:
                    torrent: dict = await db.get(f"hash_{request.query['info_hash']}")

                    old_peers: list[dict] = []

                    for peer in torrent["peers"]:
                        if peer["ip"] != request.match_info["ip_addr"]:
                            old_peers.append(peer)

                    complete = [ip for ip in torrent["complete"] if ip != request.match_info["ip_addr"]]
                    incomplete = [ip for ip in torrent["incomplete"] if ip != request.match_info["ip_addr"]]

                    if request.query["left"] == "0":
                        complete.append(request.match_info["ip_addr"])
                    else:
                        incomplete.append(request.match_info["ip_addr"])

                    new_peers = old_peers + [{
                        "peer_id": request.query["peer_id"],
                        "ip": request.match_info["ip_addr"],
                        "port": request.query["port"]
                    }]

                    await db.set(f"hash_{request.query['info_hash']}", {
                        "complete": complete,
                        "incomplete": incomplete,
                        "peers": new_peers
                    })

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
