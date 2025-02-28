import asyncio
from dataclasses import dataclass
from proto import User


class Server:
    def __init__(self, *, addr="0.0.0.0", port=8000):
        self.addr = addr
        self.port = port

    async def process(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        conn = Connection(reader, writer)
        addr = conn.peer_addr()
        print(f"{addr} connected")

        try:
            while True:
                message = await reader.readline()
                if not message:
                    break
                print("->", message)
                writer.write(message)
                await writer.drain()

        except asyncio.IncompleteReadError:
            print(f"{addr} disconnected")

        print(f"{addr} closing connection")
        writer.close()
        await writer.wait_closed()

    async def run(self):
        async with await asyncio.start_server(self.process, self.addr, self.port) as server:
            print(f"Listening on port {self.port}...")
            await server.serve_forever()


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


async def serve(*, addr="0.0.0.0", port=8000):
    server = Server(addr=addr, port=port)
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("Shutting down...")
