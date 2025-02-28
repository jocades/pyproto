import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable
from proto import User, with_marker


@dataclass
class Addr:
    host: str
    port: int

    def __str__(self):
        return f"{self.host}:{self.port}"


class Connection:
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        self.reader = reader
        self.writer = writer
        self._peer_addr: Addr | None = None

    def peer_addr(self) -> Addr:
        if not self._peer_addr:
            host, port = self.writer.get_extra_info("peername")
            self._peer_addr = Addr(host, port)
        return self._peer_addr

    async def send(self, message: str | bytes):
        self.writer.write(with_marker(message))
        await self.writer.drain()

    async def __aiter__(self):
        try:
            while True:
                marker = int.from_bytes(await self.reader.readexactly(4))
                message = await self.reader.readexactly(marker)
                yield message

        except asyncio.IncompleteReadError:
            pass
            # print(f"{addr} disconnected")

        # print(f"{addr} closing connection")
        self.writer.close()
        await self.writer.wait_closed()


class Server:
    def __init__(
        self,
        callback: Callable[[Connection], Awaitable[None]],
        *,
        addr="0.0.0.0",
        port=8000,
    ):
        self.callback = callback
        self.addr = addr
        self.port = port

    async def process(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        conn = Connection(reader, writer)
        await self.callback(conn)

    async def run(self):
        async with await asyncio.start_server(self.process, self.addr, self.port) as server:
            print(f"Listening on port {self.port}...")
            await server.serve_forever()


async def process(conn: Connection):
    async for message in conn:
        await conn.send(f"echo -> {message.decode()}")


async def main():
    server = Server(process)
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
