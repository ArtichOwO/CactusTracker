from database import db


async def set_torrent(info_hash: str,
                      complete: list = None,
                      incomplete: list = None,
                      peers: list = None):
    if complete is None:
        complete = []
    if incomplete is None:
        incomplete = []
    if peers is None:
        peers = []

    await db.set(f"torrent_{info_hash}", {
        "info_hash": info_hash,
        "complete": complete,
        "incomplete": incomplete,
        "peers": peers
    })


async def get_torrent(info_hash: str) -> dict:
    return await db.get(f"torrent_{info_hash}")


async def delete_torrent(info_hash: str):
    await db.delete(f"torrent_{info_hash}")


async def set_user(username: str, passwd: str):
    await db.set(f"user_{username}", {
        "name": username,
        "passwd": passwd
    })


async def get_user(username: str) -> dict:
    return await db.get(f"user_{username}")


async def delete_user(name: str):
    await db.delete(f"user_{name}")
