#!/usr/bin/env python3
"""Escrita atômica: arquivo temporário no mesmo diretório, depois `os.replace`.

`os.replace` é atômico dentro do mesmo sistema de arquivos — por isso o temporário
nasce ao lado do alvo, e não em /tmp. Escrita em lugar trunca; esta não."""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write(path: Path, texto: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(texto.encode('utf-8'))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_json(path: Path, dados: Any) -> None:
    atomic_write(Path(path),
                 json.dumps(dados, ensure_ascii=False, indent=2) + '\n')
