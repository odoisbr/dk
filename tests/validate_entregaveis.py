#!/usr/bin/env python3
"""As regras editoriais do entregável são cobradas por código."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import entregaveis  # noqa: E402

errors = []

if 'ata' not in entregaveis.CONTRATOS:
    errors.append('contrato da ata ausente')
if len(entregaveis.CONTRATOS['ata']['secoes']) != 7:
    errors.append('a ata tem 7 seções obrigatórias')

COMPLETA = '\n'.join(f'## {i}. {nome}\n\nconteúdo\n'
                     for i, nome in enumerate(
                         entregaveis.CONTRATOS['ata']['secoes'], start=1))

achados = entregaveis.validar('ata', COMPLETA)
if achados:
    errors.append(f'ata completa não deveria ter achado: {achados}')

parcial = COMPLETA.replace('## 7. Pontos em Aberto / Pendências',
                           '## 7. Outra coisa')
resultado = entregaveis.validar('ata', parcial)
if 'ATA-SECAO' not in {a['id'] for a in resultado}:
    errors.append('seção faltando não foi detectada')
for a in resultado:
    if not a.get('evidencia'):
        errors.append(f'achado sem evidência: {a}')

com_status = COMPLETA + '\n| Ação | Responsável | Prazo | Status |\n|---|---|---|---|\n'
if 'ATA-STATUS' not in {a['id'] for a in entregaveis.validar('ata', com_status)}:
    errors.append('coluna de status nos encaminhamentos não foi detectada')

com_marcador = COMPLETA + '\nFulana [verificar] disse que sim.\n'
if 'ATA-MARCADOR' not in {a['id'] for a in entregaveis.validar('ata', com_marcador)}:
    errors.append('marcador pendente não foi detectado')

com_proibida = COMPLETA + '\n## Próximos Passos\n\nx\n'
if 'ATA-PROIBIDA' not in {a['id'] for a in entregaveis.validar('ata', com_proibida)}:
    errors.append('seção proibida não foi detectada')

if 'REQ-EPICO' not in {a['id'] for a in
                       entregaveis.validar('requisitos',
                                           '## 1. Contexto e objetivo\n')}:
    errors.append('documento de requisitos sem épico deveria reprovar')

if 'TIPO-DESCONHECIDO' not in {a['id'] for a in entregaveis.validar('bolo', 'x')}:
    errors.append('tipo sem contrato deveria ser recusado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
