import asyncio


class Connection:
    async def __aiter__(self):
        for i in range(5):
            yield i


conn = Connection()


async def recv():
    async for message in conn:
        print(message)


asyncio.run(recv())
