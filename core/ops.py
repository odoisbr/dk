#!/usr/bin/env python3
"""Envelope de escrita: declara o escopo, simula, e só então aplica.

Duas garantias. A simulação é inerte — `planejar` nunca toca o disco. E o escopo
é fechado — caminho fora do que foi declarado levanta `ForaDoEscopo` em vez de
ser escrito 'só desta vez'."""
from __future__ import annotations
import difflib
from pathlib import Path
from typing import List

from core import io


class ForaDoEscopo(Exception):
    """Levantada quando a operação tenta escrever fora do alvo declarado."""


class FonteNaoLida(Exception):
    """Levantada quando se tenta escrever sem ler a fonte declarada."""


class Operacao:
    def __init__(self, alvo, escopo, registro=None, fontes=None) -> None:
        self.alvo = Path(alvo).resolve()
        self.escopo = list(escopo)
        self.registro = registro
        self.fontes = [Path(f) for f in (fontes or [])]
        self._pendentes = []  # type: List[tuple]

    def _dentro(self, path: Path) -> bool:
        try:
            rel = Path(path).resolve().relative_to(self.alvo)
        except ValueError:
            return False
        return any(rel == Path(p) or str(rel).startswith(str(Path(p)) + '/')
                   for p in self.escopo)

    def _exigir_leitura(self) -> None:
        if self.registro is None:
            return
        faltando = [str(f) for f in self.fontes if not self.registro.foi_lido(f)]
        if faltando:
            raise FonteNaoLida(
                'fonte declarada não foi lida nesta sessão: ' + ', '.join(faltando))

    def planejar(self, path: Path, texto: str) -> dict:
        path = Path(path)
        if not self._dentro(path):
            raise ForaDoEscopo(
                f'{path} está fora do escopo declarado {self.escopo}')
        self._exigir_leitura()
        anterior = path.read_text(encoding='utf-8') if path.exists() else ''
        diff = '\n'.join(difflib.unified_diff(
            anterior.splitlines(), texto.splitlines(),
            fromfile=f'{path.name} (atual)', tofile=f'{path.name} (proposto)',
            lineterm=''))
        self._pendentes.append((path, texto))
        return {
            'caminho': str(path),
            'acao': 'modifica' if path.exists() else 'cria',
            'diff': diff,
        }

    def aplicar(self) -> List[Path]:
        escritos = []
        for path, texto in self._pendentes:
            io.atomic_write(path, texto)
            escritos.append(path)
        self._pendentes = []
        return escritos
