import json
from typing import Dict
from pathlib import Path

fst = int("0x13000", 0)
lst = int("0x1342e", 0) + 1
hmp = [chr(i) for i in range(fst, lst)]


class Transliterator:
    def __init__(self, encode_table, decode_table):
        for k, v in encode_table.items():
            assert (
                decode_table[v] == k
            ), f"decode_table[{v}] == {decode_table[v]} != {k}"
        self.encode_table = encode_table
        self.decode_table = decode_table

    @classmethod
    def from_list(cls, content):
        encode_table, decode_table = cls._build_encode_decode_table(set(content))
        return cls(encode_table, decode_table)

    @staticmethod
    def _build_encode_decode_table(elements):
        encode_table = {c: i for i, c in enumerate(elements)}
        decode_table = {i: c for i, c in enumerate(elements)}
        return encode_table, decode_table

    @property
    def encoder(self):
        return lambda c: self.encode_table[c]

    @property
    def decoder(self):
        return lambda i: self.decode_table[i]

    def encode(self, s):
        ret = list(map(self.encoder, s))
        return ret

    def decode(self, t):
        ret = list(map(self.decoder, t))
        return ret

    def __repr__(self):
        return "%r(encode_table=%r, decode_table=%r)" % (
            type(self).__name__,
            self.encode_table,
            self.decode_table,
        )

    def __len__(self):
        return len(self.encode_table)

    def write_json(self, filename):
        p = Path(filename)
        d = dict(encode_table=self.encode_table, decode_table=self.decode_table)
        with p.open("w") as f:
            f.write(json.dumps(d))

    @classmethod
    def read_json(cls, filename):
        p = Path(filename)
        with p.open("r") as f:
            d = json.loads(f.read())
        return cls(
            encode_table=d["encode_table"],
            decode_table={int(k): v for k, v in d["decode_table"].items()},
        )
