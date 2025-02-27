import asyncio
from proto import User


async def client():
    _, w = await asyncio.open_connection("127.0.0.1", 8000)

    user = User(name="Jordi", age=25, rand=b"\x01\x02\x03")
    data = user.encode()

    w.write(data)
    await w.drain()

    w.close()
    await w.wait_closed()


if __name__ == "__main__":
    asyncio.run(client())
