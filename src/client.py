import asyncio
from proto import User, with_marker


async def test_client():
    _, w = await asyncio.open_connection("127.0.0.1", 8000)

    user = User(name="Jordi", age=25, rand=b"\x01\x02\x03")
    data = user.encode()

    w.write(data)
    await w.drain()

    w.close()
    await w.wait_closed()


async def client():
    r, w = await asyncio.open_connection("127.0.0.1", 8000)

    while True:
        message = input("> ")
        if message == "exit":
            break
        data = with_marker(message)
        print("sending", data)
        w.write(with_marker(message))
        await w.drain()

        marker = int.from_bytes(await r.readexactly(4))
        data = await r.readexactly(marker)
        print(data)

    w.close()
    await w.wait_closed()

    pass


if __name__ == "__main__":
    asyncio.run(client())
