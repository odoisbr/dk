#!/usr/bin/env python3
"""Varredura do repositório: lista, não lê.

O invariante MAP ANTES DE LER começa aqui. A varredura usa só metadado do sistema
de arquivos — nome, tamanho, extensão. Conteúdo é decisão de etapa posterior, e
custa contexto.

A lista de sensíveis não é negociável nem configurável para menos: arquivo de
credencial não entra no mapa nem que esteja versionado, porque o mapa vai para
a LLM."""
from __future__ import annotations
import fnmatch
from pathlib import Path
from typing import List

IGNORADOS_PADRAO = (
    '.git', 'node_modules', 'dist', 'build', 'coverage', '.cache',
    '__pycache__', '.venv', 'venv', '.tox', '.mypy_cache', '.pytest_cache',
    'target', 'vendor', '.next', '.nuxt', '.gradle', '.idea', '.DS_Store',
)

SENSIVEIS = (
    '.env', '.env.*', '*.pem', '*.key', '*.p12', '*.pfx', '*.keystore',
    'id_rsa', 'id_rsa.*', 'id_ed25519', 'id_ed25519.*',
    '*credential*', '*secret*', '.netrc', '.npmrc', '.pypirc',
)

_LIMITE_BYTES = 2_000_000


def _casa(nome: str, padroes) -> bool:
    return any(fnmatch.fnmatch(nome, p) or fnmatch.fnmatch(nome.lower(), p)
               for p in padroes)


def ignorado(rel: str, extras=()) -> str:
    """Devolve o motivo do descarte, ou string vazia se o arquivo entra.

    O motivo nomeia o padrão que casou: um relatório que diz apenas 'ignorado'
    não permite conferir se a política está certa."""
    partes = Path(rel).parts
    nome = Path(rel).name
    for p in partes:
        if p in IGNORADOS_PADRAO:
            return f'diretório ignorado por padrão: {p}'
    if _casa(nome, SENSIVEIS):
        return 'arquivo sensível'
    for padrao in extras:
        alvo = padrao.rstrip('/')
        if padrao.endswith('/') and alvo in partes:
            return f'.gitignore: {padrao}'
        if fnmatch.fnmatch(rel, alvo) or fnmatch.fnmatch(nome, alvo):
            return f'.gitignore: {padrao}'
    return ''


def _gitignore(raiz: Path) -> List[str]:
    """Padrões simples do .gitignore. Negação e glob duplo ficam de fora:
    o que esta função não entende, ela não finge entender."""
    f = raiz / '.gitignore'
    if not f.exists():
        return []
    padroes = []
    with open(f, encoding='utf-8', errors='replace') as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha or linha.startswith('#') or linha.startswith('!'):
                continue
            padroes.append(linha.lstrip('/'))
    return padroes


def varrer(raiz: Path) -> List[dict]:
    raiz = Path(raiz).resolve()
    extras = _gitignore(raiz)
    entradas = []
    for p in sorted(raiz.rglob('*')):
        if p.is_symlink() or not p.is_file():
            continue
        rel = str(p.relative_to(raiz))
        if ignorado(rel, extras):
            continue
        try:
            tamanho = p.stat().st_size
        except OSError:
            continue
        if tamanho > _LIMITE_BYTES:
            continue
        entradas.append({'caminho': rel, 'bytes': tamanho,
                         'ext': p.suffix.lower()})
    return entradas


def descartados(raiz: Path) -> dict:
    """Contagem do que ficou de fora, por motivo. O mapa declara o que não viu."""
    raiz = Path(raiz).resolve()
    extras = _gitignore(raiz)
    contagem = {}
    for p in raiz.rglob('*'):
        if not p.is_file():
            continue
        motivo = ignorado(str(p.relative_to(raiz)), extras)
        if motivo:
            contagem[motivo] = contagem.get(motivo, 0) + 1
    return contagem
