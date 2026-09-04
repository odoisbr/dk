#!/usr/bin/env python3
"""Descobre o que o projeto é, por evidência.

Nome de diretório mente: uma pasta `backend/` pode estar vazia, e um monorepo
pode não ter `packages/`. O que não mente é manifesto, lockfile e arquivo de
configuração — e cada conclusão aqui cita o arquivo que a sustenta."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, List

from core import classify

_LOCKS = {
    'pnpm-lock.yaml': 'pnpm', 'yarn.lock': 'yarn',
    'package-lock.json': 'npm', 'bun.lockb': 'bun',
    'poetry.lock': 'poetry', 'Pipfile.lock': 'pipenv', 'uv.lock': 'uv',
}

# nome da dependência → rótulo usado na stack
_FRAMEWORKS_JS = {
    'react': 'react', 'next': 'next', 'vue': 'vue', 'nuxt': 'nuxt',
    '@angular/core': 'angular', 'svelte': 'svelte', 'express': 'express',
    '@nestjs/core': 'nestjs', 'astro': 'astro', 'vite': 'vite',
    'tailwindcss': 'tailwind',
}

_FRAMEWORKS_PY = ('django', 'flask', 'fastapi', 'pydantic', 'sqlalchemy',
                  'celery')

_UI = ('react', 'next', 'vue', 'nuxt', 'angular', 'svelte', 'astro')
_API = ('express', 'nestjs', 'django', 'flask', 'fastapi', 'java', 'go')


def _ler(raiz: Path, rel: str) -> str:
    p = raiz / rel
    if not p.exists():
        return ''
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def detectar(raiz: Path, entradas: List[dict]) -> Dict:
    raiz = Path(raiz).resolve()
    caminhos = {e['caminho'] for e in entradas}
    stack: List[str] = []
    evidencias: List[str] = []
    gerenciador = ''
    tipo = 'indefinido'

    for lock, nome in _LOCKS.items():
        if lock in caminhos:
            gerenciador = nome
            evidencias.append(f'{lock}: gerenciador {nome}')
            break

    if 'package.json' in caminhos:
        stack.append('node')
        evidencias.append('package.json: projeto Node')
        try:
            dados = json.loads(_ler(raiz, 'package.json') or '{}')
        except json.JSONDecodeError:
            dados = {}
        deps = {}
        deps.update(dados.get('dependencies') or {})
        deps.update(dados.get('devDependencies') or {})
        for dep, rotulo in _FRAMEWORKS_JS.items():
            if dep in deps and rotulo not in stack:
                stack.append(rotulo)
                evidencias.append(f'package.json: dependência {dep}')
        if not gerenciador:
            gerenciador = 'npm'
        if dados.get('workspaces'):
            tipo = 'monorepo'
            evidencias.append('package.json: workspaces declarados')

    origem_py = next((f for f in ('pyproject.toml', 'requirements.txt', 'setup.py')
                      if f in caminhos), '')
    if origem_py:
        stack.append('python')
        evidencias.append(f'{origem_py}: projeto Python')
        texto = _ler(raiz, origem_py).lower()
        for fw in _FRAMEWORKS_PY:
            if re.search(rf'\b{re.escape(fw)}\b', texto):
                stack.append(fw)
                evidencias.append(f'{origem_py}: dependência {fw}')

    for manifesto, linguagem in (('pom.xml', 'java'), ('build.gradle', 'java'),
                                 ('build.gradle.kts', 'kotlin'),
                                 ('go.mod', 'go'), ('Gemfile', 'ruby'),
                                 ('composer.json', 'php'),
                                 ('Cargo.toml', 'rust')):
        if manifesto in caminhos:
            stack.append(linguagem)
            evidencias.append(f'{manifesto}: projeto {linguagem}')

    # Projeto sem manifesto ainda é projeto. Quando a linguagem não foi declarada
    # por manifesto, ela é inferida pela massa de arquivos — e a evidência cita um
    # arquivo real mais a contagem, para a conclusão continuar conferível.
    _MIN_ARQUIVOS = 3
    porta_linguagem = {}
    for e in entradas:
        # `entradas` pode vir crua da varredura ou já classificada; a detecção não
        # depende dessa ordem — se o rótulo não veio, ela o deriva da extensão.
        lang = e.get('linguagem') or classify.LINGUAGEM_POR_EXT.get(
            e.get('ext', ''), '')
        if lang:
            porta_linguagem.setdefault(lang, []).append(e['caminho'])
    for lang, arquivos in sorted(porta_linguagem.items()):
        if lang in stack or len(arquivos) < _MIN_ARQUIVOS:
            continue
        stack.append(lang)
        evidencias.append(
            f'{sorted(arquivos)[0]}: {len(arquivos)} arquivos {lang} '
            'no repositório, sem manifesto declarado')

    if '.claude-plugin/plugin.json' in caminhos:
        tipo = 'plugin'
        evidencias.append('.claude-plugin/plugin.json: plugin de Claude Code')
    elif tipo == 'indefinido':
        tem_ui = any(s in stack for s in _UI)
        tem_api = any(s in stack for s in _API)
        if tem_ui and tem_api:
            tipo = 'fullstack'
        elif tem_ui:
            tipo = 'frontend'
        elif tem_api:
            tipo = 'backend'
        elif any(e.get('tipo') == 'doc' for e in entradas) and \
                not any(e.get('tipo') == 'source' for e in entradas):
            tipo = 'documentacao'

    return {'tipo': tipo, 'stack': stack, 'gerenciador': gerenciador,
            'evidencias': evidencias}
