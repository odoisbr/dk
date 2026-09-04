#!/usr/bin/env python3
"""As regras do protótipo, portadas do validador do Kit.

São as que dizem, objetivamente, o que é "fugir do padrão". A regra 14 —
variável de tema apontando para valor cru em vez de token — é a que mais escapa
numa revisão humana: o resultado visual fica idêntico, e a ligação com o design
system se perde em silêncio."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

BASE = '2-design/prototipo'

_FRAMEWORKS = ('bootstrap', 'tailwind', 'bulma', 'foundation', 'materialize')

_VALOR_CRU = re.compile(
    r'--([a-z0-9-]*(?:cor|color|espaco|space|fonte|font|raio|radius|sombra|'
    r'shadow)[a-z0-9-]*)\s*:\s*'
    r'(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\)|\d+(?:\.\d+)?(?:px|rem|em))',
    re.I)


def _arquivos(base: Path, *sufixos) -> List[Path]:
    if not base.is_dir():
        return []
    return [p for p in sorted(base.rglob('*'))
            if p.is_file() and p.suffix.lower() in sufixos]


def verificar(raiz: Path) -> List[Dict]:
    """As regras do protótipo mais as do design system.

    Componente e token entram aqui, e não num módulo próprio: a etapa
    `prototipar` já é o lugar onde se mexe em componente e em tema. Um diretório
    `modules/design-system/` acrescentaria estrutura sem acrescentar capacidade —
    a spec o propunha, e a execução mostrou que a etapa basta."""
    from core import componente, tokens
    raiz = Path(raiz)
    base = raiz / BASE
    achados = []

    # o design system tem vida própria: é verificado exista ou não protótipo
    for a in componente.verificar(raiz):
        achados.append({'regra': 'CMP', 'titulo': a['titulo'],
                        'evidencia': f"{a['componente']}: {a['evidencia']}",
                        'impacto': a['impacto']})
    for a in tokens.verificar(raiz):
        achados.append({'regra': 'TOK', 'titulo': a['titulo'],
                        'evidencia': a['evidencia'], 'impacto': a['impacto']})

    if not base.is_dir():
        return achados

    def achado(regra, titulo, evidencia, impacto='medio'):
        achados.append({'regra': regra, 'titulo': titulo,
                        'evidencia': evidencia, 'impacto': impacto})

    # 7 — cópia vendorizada de design system
    for p in sorted(base.rglob('*')):
        if not p.is_file():
            continue
        partes = [x.lower() for x in p.relative_to(base).parts]
        if 'vendor' in partes and any('design-system' in x or 'design_system' in x
                                      for x in partes):
            achado(7, 'Protótipo sem cópia vendorizada de design system',
                   f'{p.relative_to(raiz)}: cópia local do design system — '
                   'a fonte é o pacote, não a cópia', 'alto')
            break

    # 8 — rota de vitrine
    html = _arquivos(base, '.html', '.htm')
    if html:
        texto = '\n'.join(p.read_text(encoding='utf-8', errors='replace')
                          for p in html).lower()
        if 'vitrine' not in texto and 'showcase' not in texto:
            achado(8, 'Protótipo com rota de vitrine',
                   f'{len(html)} arquivo(s) HTML e nenhuma referência a '
                   'vitrine ou showcase')

    # 12 e 13 — framework concorrente e API exclusiva do Bootstrap 5
    for p in html + _arquivos(base, '.css', '.scss', '.js'):
        baixo = p.read_text(encoding='utf-8', errors='replace').lower()
        for fw in _FRAMEWORKS:
            if fw in baixo:
                achado(12, 'Sem framework CSS concorrente',
                       f'{p.relative_to(raiz)}: menciona {fw}', 'alto')
                break
        if 'data-bs-' in baixo:
            achado(13, 'Sem API exclusiva do Bootstrap 5 (`data-bs-*`)',
                   f'{p.relative_to(raiz)}: usa data-bs-*', 'alto')

    # 14 — variável de tema derivada de token, não de valor cru
    for p in _arquivos(base, '.css', '.scss'):
        conteudo = p.read_text(encoding='utf-8', errors='replace')
        for nome, valor in _VALOR_CRU.findall(conteudo):
            achado(14, 'Variáveis de tema derivadas de token, não de valor cru',
                   f'{p.relative_to(raiz)}: --{nome} recebe {valor} direto, '
                   'em vez de var(--token-…)', 'alto')

    # 15 — saída compilada mais nova que a fonte
    for fonte in _arquivos(base, '.scss'):
        saida = fonte.with_suffix('.css')
        if saida.exists() and saida.stat().st_mtime < fonte.stat().st_mtime:
            achado(15, 'Saída compilada mais nova que a fonte SCSS',
                   f'{saida.relative_to(raiz)} é mais velho que '
                   f'{fonte.relative_to(raiz)} — o build não rodou')

    return achados
