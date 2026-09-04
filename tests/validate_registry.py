#!/usr/bin/env python3
"""O registro atualiza item existente em vez de duplicar.

É a mecânica que impede o furo: o mesmo requisito, levantado de novo, atualiza
o que já estava lá e preserva o que não mudou."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import registry  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)

    if registry.carregar(raiz, 'requisitos') != []:
        errors.append('registro inexistente deveria carregar como lista vazia')

    itens, acao = registry.upsert([], {'id': 'REQ-001', 'titulo': 'primeiro',
                                       'origem': 'ata-14-08'})
    if acao != 'criado':
        errors.append(f'primeira inserção devolveu {acao!r}')

    itens, acao = registry.upsert(itens, {'id': 'REQ-001', 'titulo': 'primeiro revisado'})
    if acao != 'atualizado':
        errors.append(f'segunda inserção do mesmo id devolveu {acao!r}')
    if len(itens) != 1:
        errors.append(f'duplicou: {len(itens)} itens para o mesmo id')
    if itens[0]['titulo'] != 'primeiro revisado':
        errors.append('o campo alterado não foi atualizado')
    if itens[0].get('origem') != 'ata-14-08':
        errors.append('campo não informado no update foi perdido')

    registry.gravar(raiz, 'requisitos', itens)
    if registry.carregar(raiz, 'requisitos') != itens:
        errors.append('gravar/carregar não fizeram ida e volta')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
