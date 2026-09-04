#!/usr/bin/env python3
"""Registro do que foi lido na sessão.

Existe para uma coisa só: permitir que a camada de escrita recuse gravar um
artefato cuja fonte ninguém abriu. Escrever sem ler é como o furo aparece —
o requisito que já estava no projeto é substituído em vez de atualizado."""
from __future__ import annotations
from pathlib import Path
from typing import Dict


class Registro:
    def __init__(self) -> None:
        self._lidos = {}  # type: Dict[str, str]

    def ler(self, path: Path) -> str:
        path = Path(path)
        conteudo = path.read_text(encoding='utf-8')
        self._lidos[str(path.resolve())] = conteudo
        return conteudo

    def foi_lido(self, path: Path) -> bool:
        return str(Path(path).resolve()) in self._lidos

    def conteudo(self, path: Path) -> str:
        return self._lidos[str(Path(path).resolve())]
