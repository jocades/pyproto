import asyncio

from proto import User


async def process(r: asyncio.StreamReader, w: asyncio.StreamWriter):
    addr = w.get_extra_info("peername")
    print(f"{addr} connected")

    try:
        while True:
            length = await r.readexactly(4)
            data = await r.readexactly(int.from_bytes(length))
            user = User.decode(length + data)
            print("->", user)

    except asyncio.IncompleteReadError:
        print(f"{addr} disconnected")

    print(f"{addr} closing connection")
    w.close()
    await w.wait_closed()


async def main():
    server = await asyncio.start_server(process, "0.0.0.0", 8000)
    addr = server.sockets[0].getsockname()
    print(f"Listening on {addr}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
