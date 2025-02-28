import sys
from struct import pack


def send(message: str) -> bytes:
    encoded = message.encode()
    data = pack("!I", len(encoded)) + encoded
    print("->", data)
    return data


def recv(data: bytes):
    length = data[:4]
    n = int.from_bytes(length)
    message = data[4 : 4 + n]
    print(f"<- {length=} {n=} {message=}")


if __name__ == "__main__":
    message = "hello"
    if len(sys.argv) > 1:
        message = sys.argv[1]
    recv(send(message))
