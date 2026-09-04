#!/usr/bin/env python3
"""As políticas de governança estão presentes e têm dono declarado.

O critério é o campo `owner` do front-matter, não a ausência da string TBD em
qualquer lugar: uma célula "TBD" numa coluna de canal de anúncio é informação
faltando, não política órfã. Política sem dono é que é contrato sem fonte."""
from __future__ import annotations
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
OBRIGATORIAS = [
    'naming-conventions.md', 'versioning-policy.md', 'review-process.md',
    'content-lifecycle.md', 'delivery-checklist.md', 'input-contract.md',
    'OWNERS.md', 'README.md',
]

errors = []
gov = RAIZ / 'governance'

for nome in OBRIGATORIAS:
    f = gov / nome
    if not f.exists():
        errors.append(f'governance/{nome} ausente')
        continue
    if nome == 'README.md':
        continue
    texto = f.read_text(encoding='utf-8')
    m = re.search(r'^owner:\s*(.+)$', texto, re.M)
    if not m:
        errors.append(f'governance/{nome}: sem campo owner no front-matter')
    elif m.group(1).strip() in ('', 'TBD', '[]', '[TBD]'):
        errors.append(f'governance/{nome}: owner é {m.group(1).strip()!r} — '
                      'política sem dono real')
    r = re.search(r'^reviewers:\s*(.+)$', texto, re.M)
    if r and 'TBD' in r.group(1):
        errors.append(f'governance/{nome}: reviewers ainda em TBD')

for caminho in ('.gitlab/CODEOWNERS', '.gitlab/merge_request_templates/default.md'):
    if not (RAIZ / caminho).exists():
        errors.append(f'{caminho} ausente')

codeowners = RAIZ / '.gitlab' / 'CODEOWNERS'
if codeowners.exists():
    for linha in codeowners.read_text(encoding='utf-8').splitlines():
        alvo = linha.strip()
        if not alvo.startswith('/') or alvo == '/':
            continue
        caminho = alvo.lstrip('/').rstrip('/')
        if not (RAIZ / caminho).exists():
            errors.append(f'CODEOWNERS aponta para {alvo}, que não existe no dk')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
