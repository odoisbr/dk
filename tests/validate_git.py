#!/usr/bin/env python3
"""Git: descoberta, classificação e — sobretudo — as guardas.

As guardas são a parte que importa: git é o único lugar do DK onde um erro sai
da máquina e chega no repositório de todo mundo."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import git, io  # noqa: E402

errors = []


def repo(raiz: Path, branch='feature/teste', remoto=None):
    subprocess.run(['git', 'init', '-q', str(raiz)], check=True)
    for k, v in (('user.email', 'dk@teste.local'), ('user.name', 'DK Teste')):
        subprocess.run(['git', '-C', str(raiz), 'config', k, v], check=True)
    io.atomic_write(raiz / 'README.md', '# teste\n')
    subprocess.run(['git', '-C', str(raiz), 'add', 'README.md'], check=True)
    subprocess.run(['git', '-C', str(raiz), 'commit', '-qm', 'inicial'], check=True)
    atual = subprocess.run(['git', '-C', str(raiz), 'branch', '--show-current'],
                           capture_output=True, text=True).stdout.strip()
    if atual != branch:
        subprocess.run(['git', '-C', str(raiz), 'checkout', '-qb', branch], check=True)
    if remoto:
        subprocess.run(['git', '-C', str(raiz), 'remote', 'add', 'origin', remoto],
                       check=True)


# ── descoberta do projeto no GitLab, sem API ──
SSH = 'git@gitlab.seatecnologia.com.br:design/sesc-df/design-credenciamento.git'
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d) / 'p'
    repo(raiz, remoto=SSH)
    p = git.projeto_remoto(raiz)
    if p.get('host') != 'gitlab.seatecnologia.com.br':
        errors.append(f"host: {p.get('host')}")
    if p.get('grupo') != 'design/sesc-df':
        errors.append(f"grupo aninhado não resolvido: {p.get('grupo')}")
    if p.get('projeto') != 'design-credenciamento':
        errors.append(f"projeto: {p.get('projeto')}")
    if not p.get('novo_mr', '').endswith('/-/merge_requests/new'):
        errors.append('a URL de novo MR não foi montada')

    st = git.estado(raiz)
    if not st['repositorio'] or st['branch'] != 'feature/teste':
        errors.append(f'estado errado: {st}')
    if st['protegida']:
        errors.append('feature/teste não é protegida')

HTTPS = 'https://gitlab.seatecnologia.com.br/design/sesc-df/x.git'
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d) / 'p'
    repo(raiz, remoto=HTTPS)
    if git.projeto_remoto(raiz).get('caminho') != 'design/sesc-df/x':
        errors.append('URL https não foi resolvida')

# ── branch protegida bloqueia commit e push ──
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d) / 'p'
    repo(raiz, branch='main')
    io.atomic_write(raiz / 'novo.md', 'x\n')
    for operacao in ('commit', 'push'):
        ids = {a['id'] for a in git.guardar(raiz, operacao, ['novo.md'])}
        if 'GIT-BRANCH-PROTEGIDA' not in ids:
            errors.append(f'{operacao} em main deveria ser bloqueado')

for protegida in ('main', 'master', 'develop', 'production', 'release/1.0'):
    if not git.protegida(protegida):
        errors.append(f'{protegida} deveria ser protegida')
if git.protegida('feature/x'):
    errors.append('feature/x não é protegida')

# ── arquivo sensível nunca entra ──
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d) / 'p'
    repo(raiz)
    for nome in ('.env', 'chave.pem', 'credentials.json'):
        io.atomic_write(raiz / nome, 'segredo\n')
        ach = [a for a in git.guardar(raiz, 'commit', [nome])
               if a['id'] == 'GIT-SENSIVEL']
        if not ach:
            errors.append(f'VAZAMENTO: {nome} passou na guarda de commit')

# ── documento de projeto real não é segredo, por mais que o nome pareça ──
# Regressão do defeito que o padrão `*credential*` causou na varredura: engoliu
# sete especificações de um projeto de credenciamento. Nome não faz segredo;
# nome exato e extensão fazem.
REAIS = (
    '1-levantamento/requisitos/compartilhado/credential-categories.md',
    '1-levantamento/requisitos/macromodulos/mm02_renewal-and-type-change/'
    '01_specs/f01_renew-credential.md',
    '1-levantamento/requisitos/macromodulos/mm04_my-credential/'
    '01_specs/f02_facial-validation.md',
    '2-prototipo/design-system/tokens.json',
    'docs/secrets-management.md',
    'src/keyboard.js',
)
for caminho in REAIS:
    if git._SENSIVEL.search(caminho):
        errors.append(f'falso positivo de sensível: {caminho}')
for segredo in ('.env', 'config/.env.production', 'certs/servidor.pem',
                'deploy/id_rsa', 'credentials.json', 'app/secrets.yml'):
    if not git._SENSIVEL.search(segredo):
        errors.append(f'VAZAMENTO: {segredo} não foi reconhecido como sensível')

# ── mensagem de commit: marca bloqueia, formato avisa ──
if 'GIT-MENSAGEM-MARCA' not in {a['id'] for a in git.validar_mensagem(
        'fix: ajuste feito com claude')}:
    errors.append('mensagem com marca de LLM deveria ser recusada')
if git.validar_mensagem('fix: corrige o botão de ação'):
    errors.append('mensagem válida não deveria ter achado')
formato = git.validar_mensagem('mexi numas coisas')
if [a for a in formato if a['impacto'] == 'alto']:
    errors.append('formato de mensagem deveria avisar, não bloquear')
if not formato:
    errors.append('mensagem fora da convenção deveria ser apontada')

# ── `git add .` sem classificação é proibido ──
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d) / 'p'
    repo(raiz)
    io.atomic_write(raiz / 'novo.md', 'x\n')
    if 'GIT-SEM-CLASSIFICACAO' not in {a['id'] for a in git.guardar(raiz, 'commit')}:
        errors.append('commit sem lista de arquivos deveria ser bloqueado')
    if git.guardar(raiz, 'commit', ['novo.md']):
        errors.append('commit com arquivo classificado não deveria bloquear')

# ── nome de branch com marca de ferramenta ──
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d) / 'p'
    repo(raiz, branch='claude/ajuste')
    if 'GIT-NOME-BRANCH' not in {a['id'] for a in git.guardar(raiz, 'commit', [])}:
        errors.append('branch com marca de LLM deveria ser recusada')

# ── classificação do pedido em tipo de branch ──
for texto, esperado in (('corrigir o bug da tela', 'fix'),
                        ('urgente, quebrou em produção', 'hotfix'),
                        ('ajustar o espaçamento do card', 'adjustment'),
                        ('documentar o handoff', 'documentation'),
                        ('criar a tela de renovação', 'feature'),
                        ('trocar o texto do rótulo', 'content')):
    obtido = git.tipo_de_branch(texto)
    if obtido != esperado:
        errors.append(f'{texto!r} → {obtido}, esperado {esperado}')

if git.nome_de_branch('fix', 'Corrigir o Botão de Ação') != 'fix/corrigir-o-botao-de-acao':
    errors.append(f"nome de branch: {git.nome_de_branch('fix', 'Corrigir o Botão de Ação')}")

# ── o MR sai por push option, sem dependência ──
cmd = git.comando_push_mr('fix/x', 'Corrige o botão', alvo='main')
if 'merge_request.create' not in ' '.join(cmd):
    errors.append('o push não cria merge request')
if '--force' in cmd or '-f' in cmd:
    errors.append('FORCE PUSH: proibido pela política')
if 'merge_request.target=main' not in ' '.join(cmd):
    errors.append('o MR não declara o alvo')

# ── plano de commit não escreve nada ──
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d) / 'p'
    repo(raiz)
    io.atomic_write(raiz / 'novo.md', 'x\n')
    antes = git.estado(raiz)['sujo']
    plano = git.plano_commit(raiz, ['novo.md'], 'feat: novo')
    if git.estado(raiz)['sujo'] != antes:
        errors.append('plano_commit alterou o repositório')
    if plano['bloqueios']:
        errors.append(f"plano válido com bloqueio: {plano['bloqueios']}")
    fora = git.plano_commit(raiz, ['inexistente.md'], 'x')
    if 'inexistente.md' not in fora['fora_do_diff']:
        errors.append('arquivo fora do diff não foi apontado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
