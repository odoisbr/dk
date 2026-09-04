#!/usr/bin/env python3
"""O changeset declara o alvo antes de tocar em arquivo.

É a peça que fecha a dor nº 2: pediram um ajuste numa tela, e a ferramenta
alterou outras três. Com o changeset, o que não foi declarado não é escrito —
e a operação falha em vez de passar batido."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import changeset, io, ops  # noqa: E402

errors = []

cs = changeset.abrir('CS-001', 'ajustar espaçamento do card',
                     'pedido da Cecília em 04/09',
                     ['2-design/prototipo/components/card'])

for campo in ('id', 'title', 'status', 'source', 'affected', 'validation',
              'result'):
    if campo not in cs:
        errors.append(f'changeset sem o campo {campo} do schema do DLS')
if cs['status'] != 'aberto':
    errors.append(f"changeset nasce {cs['status']!r}, deveria nascer 'aberto'")

if changeset.validar(cs):
    errors.append(f'changeset completo não deveria ter achado: '
                  f'{changeset.validar(cs)}')

vazio = changeset.abrir('CS-002', 'sem alvo', 'x', [])
if 'CS-SEM-ALVO' not in {a['id'] for a in changeset.validar(vazio)}:
    errors.append('changeset sem affected deveria reprovar')

sem_origem = changeset.abrir('CS-003', 'sem origem', '', ['a'])
if 'CS-SEM-ORIGEM' not in {a['id'] for a in changeset.validar(sem_origem)}:
    errors.append('changeset sem origem deveria reprovar')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    alvo = raiz / '2-design' / 'prototipo' / 'components' / 'card' / 'card.css'
    fora = raiz / '2-design' / 'prototipo' / 'components' / 'botao' / 'botao.css'
    io.atomic_write(alvo, '.card{padding:8px}')
    io.atomic_write(fora, '.botao{padding:8px}')

    op = changeset.operacao(raiz, cs)
    plano = op.planejar(alvo, '.card{padding:12px}')
    if plano['acao'] != 'modifica':
        errors.append(f"plano inesperado: {plano['acao']}")

    try:
        op.planejar(fora, '.botao{padding:12px}')
    except ops.ForaDoEscopo:
        pass
    else:
        errors.append('o changeset não impediu escrita fora do affected')

    escritos = op.aplicar()
    if fora.read_text(encoding='utf-8') != '.botao{padding:8px}':
        errors.append('arquivo fora do changeset foi alterado')
    if alvo.read_text(encoding='utf-8') != '.card{padding:12px}':
        errors.append('o alvo declarado não foi escrito')

    fechado = changeset.fechar(cs, 'espaçamento ajustado', escritos)
    if fechado['status'] != 'fechado':
        errors.append('fechar() não mudou o status')
    if not fechado['result']:
        errors.append('changeset fechado sem resultado')
    if str(alvo) not in ' '.join(fechado['escritos']):
        errors.append('o changeset fechado não registra o que foi escrito')
    if cs['status'] != 'aberto':
        errors.append('fechar() mutou o changeset original')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
