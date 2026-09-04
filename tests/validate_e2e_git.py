#!/usr/bin/env python3
"""E2E do git: configurar, achar o projeto, commitar e preparar o MR.

Nada de rede. O push é verificado no plano — é onde a política atua; o envio em
si é `git push`, e testar a rede aqui só tornaria o teste frágil."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DK = [sys.executable, str(RAIZ / 'bin' / 'dk')]
REMOTO = 'git@gitlab.seatecnologia.com.br:design/sesc-df/design-credenciamento.git'

errors = []


def dk(*args, esperado=0):
    r = subprocess.run(DK + list(args), capture_output=True, text=True)
    if r.returncode != esperado:
        errors.append(f'dk {" ".join(args[:3])} → saiu {r.returncode}, '
                      f'esperado {esperado}: {(r.stdout + r.stderr).strip()[:300]}')
    return r.stdout + r.stderr


with tempfile.TemporaryDirectory() as d:
    proj = Path(d) / 'projeto'
    proj.mkdir()

    # 1. configurar o git local, do zero
    saida = dk('git', '--projeto', str(proj), '--configurar', '--apply',
               '--nome', 'Design SEA', '--email', 'design@sea.local',
               '--remoto', REMOTO)
    if not (proj / '.git').is_dir():
        errors.append('--configurar --apply não iniciou o repositório')
    ignore = (proj / '.gitignore').read_text(encoding='utf-8')
    for padrao in ('.env', '*.pem', 'credentials.json'):
        if padrao not in ignore:
            errors.append(f'.gitignore sem {padrao}')

    # 2. achar o projeto no GitLab, sem API
    if 'design/sesc-df/design-credenciamento' not in saida:
        errors.append(f'o projeto no GitLab não foi identificado: {saida[:200]}')
    if 'falta configurar' in saida:
        errors.append(f'configuração ficou incompleta: {saida[:200]}')

    subprocess.run(['git', '-C', str(proj), 'add', '.gitignore'], check=True)
    subprocess.run(['git', '-C', str(proj), 'commit', '-qm', 'chore: inicial'],
                   check=True)
    atual = subprocess.run(['git', '-C', str(proj), 'branch', '--show-current'],
                           capture_output=True, text=True).stdout.strip()
    if atual not in ('main', 'master'):
        subprocess.run(['git', '-C', str(proj), 'branch', '-M', 'main'], check=True)

    # 3. branch protegida bloqueia o commit antes de qualquer escrita
    (proj / 'nota.md').write_text('conteúdo\n', encoding='utf-8')
    saida = dk('git', '--projeto', str(proj), '--commit', 'feat: nota',
               '--arquivo', 'nota.md', '--apply', esperado=1)
    if 'GIT-BRANCH-PROTEGIDA' not in saida:
        errors.append('commit em main deveria ser recusado pelo CLI')
    if subprocess.run(['git', '-C', str(proj), 'log', '--oneline'],
                      capture_output=True, text=True).stdout.count('\n') != 1:
        errors.append('VAZAMENTO: o commit bloqueado foi feito assim mesmo')

    # 4. branch de trabalho, classificada pelo pedido
    saida = dk('git', '--projeto', str(proj), '--branch',
               'Corrigir o botão de ação da tela', '--apply')
    if 'fix/corrigir-o-botao-de-acao-da-tela' not in saida:
        errors.append(f'branch não foi classificada nem nomeada: {saida[:200]}')

    # 5. simulação não commita
    saida = dk('git', '--projeto', str(proj), '--commit', 'fix: ajusta a nota',
               '--arquivo', 'nota.md')
    if 'simulação' not in saida:
        errors.append('o commit sem --apply deveria simular')
    if subprocess.run(['git', '-C', str(proj), 'status', '--porcelain'],
                      capture_output=True, text=True).stdout.strip() == '':
        errors.append('a simulação commitou')

    # 6. arquivo sensível não entra, nem com --apply
    (proj / '.env').write_text('TOKEN=abc\n', encoding='utf-8')
    saida = dk('git', '--projeto', str(proj), '--commit', 'chore: env',
               '--arquivo', '.env', '--apply', esperado=1)
    if 'GIT-SENSIVEL' not in saida:
        errors.append('VAZAMENTO: .env passou pelo CLI')

    # 7. commit sem lista de arquivo é recusado
    saida = dk('git', '--projeto', str(proj), '--commit', 'fix: tudo',
               '--apply', esperado=1)
    if 'proibido' not in saida:
        errors.append('commit sem --arquivo deveria ser recusado')

    # 8. o commit de verdade
    saida = dk('git', '--projeto', str(proj), '--commit', 'fix: ajusta a nota',
               '--arquivo', 'nota.md', '--apply')
    log = subprocess.run(['git', '-C', str(proj), 'log', '--oneline'],
                         capture_output=True, text=True).stdout
    if 'fix: ajusta a nota' not in log:
        errors.append(f'o commit não entrou: {saida[:200]}')
    if '.env' in subprocess.run(['git', '-C', str(proj), 'show', '--name-only',
                                 '--format='], capture_output=True,
                                text=True).stdout:
        errors.append('VAZAMENTO: .env entrou no commit')

    # 9. o push que abre o MR, em plano
    saida = dk('git', '--projeto', str(proj), '--push', '--titulo',
               'Corrige o botão de ação')
    for esperado in ('merge_request.create', 'merge_request.target=main',
                     'design-credenciamento'):
        if esperado not in saida:
            errors.append(f'o plano de push não traz {esperado}')
    if '--force' in saida:
        errors.append('FORCE PUSH no plano: proibido pela política')
    if 'simulação' not in saida:
        errors.append('o push sem --apply deveria simular')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
