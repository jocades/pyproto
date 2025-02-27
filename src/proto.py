from struct import pack
from typing import dataclass_transform, Self
from dataclasses import dataclass, fields


def packint(n: int) -> bytes:
    return pack("!I", n)


def readint(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4])


@dataclass_transform()
class Proto:
    def __init_subclass__(cls) -> None:
        dataclass(cls)

    def __bytes__(self) -> bytes:
        return self.encode()

    def encode(self) -> bytes:
        data = b""

        for k, v in self.__dict__.items():
            if isinstance(v, str):
                encoded = v.encode()
                data += packint(len(encoded)) + encoded
            elif isinstance(v, int):
                data += packint(v)
            elif isinstance(v, bytes):
                data += packint(len(v)) + v
            else:
                raise TypeError(f"Unsupported type: {type(v)} in {self.__class__.__name__}.{k}")

        return packint(len(data)) + data

    @classmethod
    def decode(cls, data: bytes) -> Self:
        offset = 4
        length = readint(data, 0)
        values = []

        for field in fields(cls):  # type:ignore
            if field.type is str:
                n = readint(data, offset)
                offset += 4
                v = data[offset : offset + n].decode()
                offset += n
                values.append(v)
            elif field.type is int:
                v = readint(data, offset)
                offset += 4
                values.append(v)
            elif field.type is bytes:
                n = readint(data, offset)
                offset += 4
                v = data[offset : offset + n]
                values.append(v)

        return cls(*values)


class User(Proto):
    name: str
    age: int
    rand: bytes


def test():
    user = User("Jordi", 10, b"\x01\x02\x03")
    data = user.encode()
    other = User.decode(data)
    assert user == other
