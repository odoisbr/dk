#!/usr/bin/env python3
"""A dor nº 2, provada: o ajuste fora do escopo é recusado.

O time relatou que um pedido de ajuste numa tela acabava alterando outras coisas
e quebrando o que já estava pronto. Este teste monta dois componentes, declara um
como alvo, e exige que o outro permaneça byte a byte igual."""
from __future__ import annotations
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import changeset, io, ops, prototipo  # noqa: E402

errors = []


def sha(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()


with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    base = projeto / '2-design' / 'prototipo'
    io.atomic_write(base / 'index.html', '<a href="/vitrine">vitrine</a>')
    io.atomic_write(base / 'components' / 'card' / 'card.css',
                    '.card{padding:var(--token-space-2)}')
    io.atomic_write(base / 'components' / 'botao' / 'botao.css',
                    '.botao{padding:var(--token-space-2)}')
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:var(--token-blue)}')

    if prototipo.verificar(projeto):
        errors.append('o protótipo de partida deveria estar limpo')

    antes_botao = sha(base / 'components' / 'botao' / 'botao.css')

    cs = changeset.abrir(
        'CS-010', 'aumentar o espaçamento do card',
        'pedido do time em 04/09',
        ['2-design/prototipo/components/card'])
    if changeset.validar(cs):
        errors.append('o changeset montado deveria ser válido')

    op = changeset.operacao(projeto, cs)
    op.planejar(base / 'components' / 'card' / 'card.css',
                '.card{padding:var(--token-space-3)}')

    # o agente "se perde" e tenta ajustar o botão também
    recusado = False
    try:
        op.planejar(base / 'components' / 'botao' / 'botao.css',
                    '.botao{padding:var(--token-space-3)}')
    except ops.ForaDoEscopo:
        recusado = True
    if not recusado:
        errors.append('a escrita fora do alvo declarado NÃO foi recusada — '
                      'é exatamente a dor que o changeset existe para impedir')

    escritos = op.aplicar()

    if sha(base / 'components' / 'botao' / 'botao.css') != antes_botao:
        errors.append('o botão mudou: o que já estava pronto foi quebrado')
    if (base / 'components' / 'card' / 'card.css').read_text(encoding='utf-8') \
            != '.card{padding:var(--token-space-3)}':
        errors.append('o alvo declarado não foi ajustado')
    if len(escritos) != 1:
        errors.append(f'{len(escritos)} arquivos escritos para um alvo declarado')

    depois = prototipo.verificar(projeto)
    if depois:
        errors.append(f'o ajuste introduziu violação de padrão: {depois}')

    fechado = changeset.fechar(cs, 'espaçamento do card ajustado', escritos)
    if fechado['status'] != 'fechado' or not fechado['escritos']:
        errors.append('o changeset não fechou com o registro do que foi escrito')

    # e o caminho errado — ajustar valor cru no tema — é pego pelo padrão
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:#009CC5}')
    if 14 not in {a['regra'] for a in prototipo.verificar(projeto)}:
        errors.append('trocar token por valor cru deveria reprovar a regra 14')

    r = subprocess.run(
        [sys.executable, str(RAIZ / 'bin' / 'dk'), 'prototipar',
         '--projeto', str(projeto), '--verificar'],
        capture_output=True, text=True)
    if r.returncode == 0:
        errors.append('a CLI deveria reprovar o protótipo com valor cru')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
