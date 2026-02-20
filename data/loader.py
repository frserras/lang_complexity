from pathlib import Path
import pandas as pd


class ExcelLoader:
    def __init__(self, *path):
        _path = []
        _srcs = []
        _data = []
        for p in path:
            p = Path(p)
            s, d = self._load(p)
            _path.append(p)
            _srcs.append(s)
            _data.append(d)

        self.path = tuple(_path)
        self.srcs = tuple(_srcs)
        self.data = tuple(_data)

    def __repr__(self):
        return f"ExcelLoader({self.path!r})"

    def _load(self, path):
        dirfiles = (
            [path] if path.is_file() else [e for e in path.iterdir() if e.is_file()]
        )
        excels = [
            {k: v.to_dict() for k, v in pd.read_excel(e, None).items()}
            for e in dirfiles
        ]
        return dirfiles, excels

    def load(self):
        if hasattr(self, "data"):
            return self.srcs, self.data
