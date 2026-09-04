#!/usr/bin/env python3
"""Rotula cada arquivo e estima o que ele custaria em contexto.

A estimativa é declarada, não escondida: `REGRA_TOKENS` diz a conversão usada, e
todo relatório que mostra número de token repete que é estimativa."""
from __future__ import annotations
from pathlib import Path

REGRA_TOKENS = '~4 bytes por token para texto; binário não é lido, custa 0'

LINGUAGEM_POR_EXT = {
    '.py': 'python', '.js': 'javascript', '.mjs': 'javascript',
    '.ts': 'typescript', '.tsx': 'typescript', '.jsx': 'javascript',
    '.java': 'java', '.go': 'go', '.rb': 'ruby', '.php': 'php',
    '.rs': 'rust', '.kt': 'kotlin', '.swift': 'swift', '.cs': 'csharp',
    '.css': 'css', '.scss': 'scss', '.html': 'html', '.ftl': 'freemarker',
    '.sh': 'shell', '.bash': 'shell', '.sql': 'sql',
}

_CONFIG_EXT = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.properties',
               '.xml', '.env'}
_DOC_EXT = {'.md', '.rst', '.txt', '.adoc'}
_BINARIA = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.pdf', '.zip',
            '.gz', '.tar', '.jar', '.war', '.class', '.so', '.dylib', '.dll',
            '.exe', '.woff', '.woff2', '.ttf', '.otf', '.mp4', '.mov', '.mp3',
            '.sqlite'}

_MANIFESTOS = {
    'package.json', 'pyproject.toml', 'requirements.txt', 'setup.py',
    'pom.xml', 'build.gradle', 'build.gradle.kts', 'go.mod', 'Gemfile',
    'composer.json', 'Cargo.toml', 'pubspec.yaml',
}

_DOC_RAIZ = {'README.md', 'CLAUDE.md', 'AGENTS.md', 'AGENT.md',
             'CONTRIBUTING.md', 'CHANGELOG.md', 'llms.txt', 'llms-full.txt'}


def classificar(entrada: dict) -> dict:
    caminho = entrada['caminho']
    partes = Path(caminho).parts
    nome = Path(caminho).name
    ext = entrada.get('ext', '')

    binario = ext in _BINARIA
    entrada['binario'] = binario
    entrada['linguagem'] = LINGUAGEM_POR_EXT.get(ext, '')

    if binario:
        tipo, categoria = 'asset', 'binario'
    elif nome in _MANIFESTOS:
        tipo, categoria = 'config', 'manifesto'
    elif nome in _DOC_RAIZ and len(partes) == 1:
        tipo, categoria = 'doc', 'documentacao-raiz'
    elif any(p in ('test', 'tests', 'spec', '__tests__') for p in partes) \
            or nome.startswith('test_') or nome.endswith('_test.py'):
        tipo, categoria = 'test', 'teste'
    elif ext in _CONFIG_EXT:
        tipo, categoria = 'config', 'configuracao'
    elif ext in _DOC_EXT:
        tipo, categoria = 'doc', 'documentacao'
    elif entrada['linguagem']:
        tipo, categoria = 'source', 'codigo'
    else:
        tipo, categoria = 'outro', 'nao-classificado'

    entrada['tipo'] = tipo
    entrada['categoria'] = categoria
    entrada['tokens_estimados'] = 0 if binario else entrada['bytes'] // 4
    return entrada
