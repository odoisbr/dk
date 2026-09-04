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


# Manual e e-mail: portados do Design Community, com as regras que a skill de lá
# enunciava em prosa.
for tipo in ('manual', 'email'):
    if tipo not in entregaveis.CONTRATOS:
        errors.append(f'contrato de {tipo} ausente')

EMAIL_OK = """## Assunto: (Entrega) Credenciamento SESC-DF

## Abertura

Prezados,

## Resumo

O projeto contemplou os principais pontos.

## Status do ambiente

Homologação.

## Itens da entrega

1.1 Renovação de credencial.

## Encerramento

Em caso de dúvidas, estou à disposição.
"""
if entregaveis.validar('email', EMAIL_OK):
    errors.append(f'e-mail completo não deveria reprovar: '
                  f'{entregaveis.validar("email", EMAIL_OK)}')

fora = EMAIL_OK.replace('(Entrega) Credenciamento SESC-DF', 'Entrega do projeto')
if 'EMA-ASSUNTO' not in {a['id'] for a in entregaveis.validar('email', fora)}:
    errors.append('assunto fora do padrão deveria reprovar')

vazando = EMAIL_OK + '\nDADOS DE ACESSO\nUsuário: admin\nSenha: sesc2026\n'
ach = [a for a in entregaveis.validar('email', vazando) if a['id'] == 'EMA-CREDENCIAL']
if not ach:
    errors.append('VAZAMENTO: credencial preenchida no e-mail não foi barrada')
elif ach[0]['impacto'] != 'alto':
    errors.append('credencial em e-mail tem que bloquear, não avisar')

marcador = EMAIL_OK + '\nDADOS DE ACESSO\nUsuário: <informar>\nSenha: <informar>\n'
if 'EMA-CREDENCIAL' in {a['id'] for a in entregaveis.validar('email', marcador)}:
    errors.append('bloco com marcador é válido e não deveria reprovar')

if 'TIPO-DESCONHECIDO' not in {a['id'] for a in entregaveis.validar('bolo', 'x')}:
    errors.append('tipo sem contrato deveria ser recusado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
