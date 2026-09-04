#!/usr/bin/env python3
"""Git e GitLab: o mínimo que o processo de design precisa, com as guardas.

Quatro capacidades, não cinquenta skills: configurar o git local, achar o projeto
no GitLab, subir commit e abrir merge request. O Kit tinha cinquenta skills de
git; a maior parte era passo de um fluxo, não capacidade.

A política de segurança é portada literal do Kit e vale como bloqueio, não como
recomendação:

    proibidos: commit ou push direto em main, master, develop, release/* e
    production · `git add .` sem classificação · force push · reset hard ·
    rebase destrutivo · exclusão de branch com commits exclusivos · commit de
    .env, chave privada, token e credencial · token GitLab no repositório

Nada aqui executa escrita sozinho. Toda função devolve **plano**; quem aplica é a
CLI, com `--apply`, e só depois de a guarda passar.

O merge request sai por push option do GitLab — `-o merge_request.create` — que é
git puro: sem token, sem API, sem dependência. Quando o `glab` existe, ele é
oferecido como atalho; quando não existe, o DK diz e entrega a URL."""
from __future__ import annotations
import re
import subprocess
import unicodedata
from pathlib import Path
from shutil import which
from typing import Dict, List, Optional

PROTEGIDAS = ('main', 'master', 'develop', 'production')
_PROTEGIDA_PADRAO = re.compile(r'^(release|hotfix-release)/')

TIPOS_BRANCH = {
    'hotfix': ('urgente', 'produção', 'producao', 'incidente', 'hotfix'),
    'fix': ('erro', 'bug', 'quebrado', 'corrigir', 'correção', 'correcao',
            'não funciona', 'nao funciona'),
    'adjustment': ('ajustar', 'ajuste', 'melhorar', 'refinar',
                   'alterar posição', 'responsividade'),
    'content': ('texto', 'copy', 'imagem', 'conteúdo', 'conteudo', 'rótulo'),
    'documentation': ('documentar', 'documentação', 'documentacao', 'handoff',
                      'readme', 'especificação'),
    'refactor': ('refatorar', 'reorganizar', 'limpar código',
                 'sem mudar comportamento', 'tokens'),
    'chore': ('configurar', 'dependência', 'dependencia', 'estrutura',
              'pipeline'),
    'spike': ('estudar', 'experimentar', 'prova de conceito', 'poc', 'spike'),
    'feature': ('criar', 'nova', 'novo', 'adicionar', 'implementar',
                'construir'),
}

# Nome de branch com marca de LLM é proibido pela política da casa.
_MARCA_LLM = re.compile(r'\b(claude|anthropic|gpt|copilot|codex)\b', re.I)

_SENSIVEL = re.compile(
    r'(^|/)(\.env(\..*)?|\.netrc|\.npmrc|\.pypirc|credentials(\.json|\.ya?ml)?|'
    r'secrets(\.json|\.ya?ml)?|id_rsa|id_ed25519)$|\.(pem|key|p12|pfx|keystore)$',
    re.I)


def _git(raiz: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(raiz), *args],
                          capture_output=True, text=True)


def e_repositorio(raiz: Path) -> bool:
    return _git(Path(raiz), 'rev-parse', '--git-dir').returncode == 0


def estado(raiz: Path) -> Dict:
    raiz = Path(raiz)
    if not e_repositorio(raiz):
        return {'repositorio': False}
    branch = _git(raiz, 'branch', '--show-current').stdout.strip()
    porcelain = _git(raiz, 'status', '--porcelain=v1').stdout.splitlines()
    remoto = _git(raiz, 'remote', 'get-url', 'origin').stdout.strip()
    hooks = _git(raiz, 'config', 'core.hooksPath').stdout.strip()
    upstream = _git(raiz, 'rev-parse', '--abbrev-ref',
                    '--symbolic-full-name', '@{u}')
    frente = atras = 0
    if upstream.returncode == 0:
        contagem = _git(raiz, 'rev-list', '--left-right', '--count',
                        f'{upstream.stdout.strip()}...HEAD').stdout.split()
        if len(contagem) == 2:
            atras, frente = int(contagem[0]), int(contagem[1])
    return {
        'repositorio': True,
        'branch': branch,
        'protegida': protegida(branch),
        'sujo': len(porcelain),
        'alterados': [l[3:] for l in porcelain],
        'remoto': remoto,
        'hooksPath': hooks,
        'upstream': upstream.stdout.strip() if upstream.returncode == 0 else '',
        'a_frente': frente,
        'atras': atras,
    }


def protegida(branch: str) -> bool:
    return branch in PROTEGIDAS or bool(_PROTEGIDA_PADRAO.match(branch or ''))


def projeto_remoto(raiz: Path) -> Dict:
    """Descobre o projeto no GitLab a partir do remoto, sem chamar a API.

    Aceita as duas formas: `git@host:grupo/sub/projeto.git` e
    `https://host/grupo/sub/projeto.git`."""
    url = estado(raiz).get('remoto', '')
    if not url:
        return {}
    m = re.match(r'^(?:git@|ssh://git@)([^:/]+)[:/](.+?)(?:\.git)?$', url)
    if not m:
        m = re.match(r'^https?://(?:[^@]+@)?([^/]+)/(.+?)(?:\.git)?$', url)
    if not m:
        return {'url': url}
    host, caminho = m.group(1), m.group(2).strip('/')
    partes = caminho.split('/')
    return {
        'url': url,
        'host': host,
        'caminho': caminho,
        'grupo': '/'.join(partes[:-1]),
        'projeto': partes[-1],
        'web': f'https://{host}/{caminho}',
        'novo_mr': f'https://{host}/{caminho}/-/merge_requests/new',
    }


def tipo_de_branch(texto: str) -> str:
    """Classifica o pedido em tipo de branch pelas palavras da casa.

    Ordem importa: `hotfix` antes de `fix`, e `feature` por último — "criar" é
    genérico e casaria com quase tudo se viesse antes."""
    baixo = (texto or '').lower()
    for tipo, palavras in TIPOS_BRANCH.items():
        if any(p in baixo for p in palavras):
            return tipo
    return 'feature'


def nome_de_branch(tipo: str, descricao: str) -> str:
    """`tipo/descricao-em-kebab`, com acento dobrado antes do corte.

    Sem a dobra, "Botão" vira `bot-o`: o acento não casa com `[a-z0-9]` e vira
    separador, partindo a palavra ao meio."""
    dobrado = unicodedata.normalize('NFKD', (descricao or '').lower())
    dobrado = ''.join(c for c in dobrado if not unicodedata.combining(c))
    slug = re.sub(r'[^a-z0-9]+', '-', dobrado.strip()).strip('-')[:48].strip('-')
    return f'{tipo}/{slug or "sem-descricao"}'


def _achado(ident, titulo, evidencia, impacto='alto') -> Dict:
    return {'id': ident, 'titulo': titulo, 'evidencia': evidencia,
            'impacto': impacto}


def guardar(raiz: Path, operacao: str, arquivos: Optional[List[str]] = None) -> List[Dict]:
    """As guardas da política, antes de qualquer escrita. Lista vazia libera."""
    raiz = Path(raiz)
    st = estado(raiz)
    achados = []

    if not st.get('repositorio'):
        return [_achado('GIT-SEM-REPO', 'não é um repositório git',
                        f'{raiz} não tem .git — `dk git --configurar` inicia')]

    if operacao in ('commit', 'push') and st['protegida']:
        achados.append(_achado(
            'GIT-BRANCH-PROTEGIDA', f'{operacao} direto em branch protegida',
            f"branch atual é {st['branch']!r} — protegidas: "
            + ', '.join(PROTEGIDAS) + ', release/*. Crie uma branch de trabalho'))

    if _MARCA_LLM.search(st.get('branch') or ''):
        achados.append(_achado(
            'GIT-NOME-BRANCH', 'nome de branch com marca de ferramenta',
            f"{st['branch']!r} — a política da casa não aceita nome de LLM em "
            'branch, commit, MR ou release'))

    alvo = arquivos if arquivos is not None else st.get('alterados', [])
    sensiveis = [a for a in alvo if _SENSIVEL.search(a)]
    if sensiveis:
        achados.append(_achado(
            'GIT-SENSIVEL', 'arquivo sensível no conjunto a commitar',
            'não vão para o repositório: ' + ', '.join(sensiveis)))

    if operacao == 'commit' and arquivos is None:
        achados.append(_achado(
            'GIT-SEM-CLASSIFICACAO', 'commit sem classificação de arquivo',
            '`git add .` é proibido pela política: liste o que entra no commit'))

    return achados


def plano_commit(raiz: Path, arquivos: List[str], mensagem: str) -> Dict:
    raiz = Path(raiz)
    st = estado(raiz)
    fora = [a for a in arquivos if a not in st.get('alterados', [])]
    return {
        'branch': st.get('branch'),
        'arquivos': list(arquivos),
        'fora_do_diff': fora,
        'mensagem': mensagem,
        'bloqueios': guardar(raiz, 'commit', arquivos) + validar_mensagem(mensagem),
    }


def comando_push_mr(branch: str, titulo: str, alvo: str = 'main',
                    descricao: str = '') -> List[str]:
    """O push que abre o merge request, em git puro.

    Push option do GitLab: sem token, sem API, sem dependência. É o caminho
    canônico; o `glab` fica como atalho opcional."""
    cmd = ['git', 'push', '-u', 'origin', branch,
           '-o', 'merge_request.create',
           '-o', f'merge_request.target={alvo}',
           '-o', f'merge_request.title={titulo}',
           '-o', 'merge_request.remove_source_branch']
    if descricao:
        cmd += ['-o', f'merge_request.description={descricao}']
    return cmd


def glab_disponivel() -> str:
    return which('glab') or ''


TIPOS_COMMIT = ('feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore',
                'content', 'adjustment', 'hotfix', 'spike')
_MENSAGEM = re.compile(r'^(' + '|'.join(TIPOS_COMMIT) + r')(\([^)]+\))?: .{3,}',
                       re.S)


def validar_mensagem(mensagem: str) -> List[Dict]:
    """Mensagem de commit: marca de LLM bloqueia, formato só avisa.

    Marca de ferramenta é política e vale bloqueio. Formato convencional é
    convenção da casa: aponta, não impede."""
    achados = []
    if _MARCA_LLM.search(mensagem or ''):
        achados.append(_achado(
            'GIT-MENSAGEM-MARCA', 'mensagem de commit com marca de ferramenta',
            'a política da casa não aceita nome de LLM em commit, branch, MR '
            'ou release'))
    if not _MENSAGEM.match((mensagem or '').strip()):
        achados.append(_achado(
            'GIT-MENSAGEM-FORMATO', 'mensagem fora da convenção',
            '`<tipo>: descrição` com tipo em ' + ', '.join(TIPOS_COMMIT),
            impacto='medio'))
    return achados


def configuracao(raiz: Path) -> Dict:
    """O que falta no git local para o projeto operar."""
    raiz = Path(raiz)
    if not e_repositorio(raiz):
        return {'repositorio': False, 'faltando': ['repositório git']}
    lido = {c: _git(raiz, 'config', c).stdout.strip()
            for c in ('user.name', 'user.email')}
    ignore = raiz / '.gitignore'
    texto = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    cobertos = {p for p in ('.env', '*.pem', '*.key') if p in texto}
    faltando = [c for c, v in lido.items() if not v]
    if not (raiz / '.gitignore').exists():
        faltando.append('.gitignore')
    elif len(cobertos) < 3:
        faltando.append('.gitignore sem padrão sensível')
    if not estado(raiz).get('remoto'):
        faltando.append('remote origin')
    return {'repositorio': True, 'config': lido,
            'gitignore_sensivel': sorted(cobertos), 'faltando': faltando}


LINHAS_GITIGNORE = ('# sensível — política do DK', '.env', '.env.*', '*.pem',
                    '*.key', '*.p12', '*.pfx', 'credentials.json',
                    'secrets.json', '.netrc', '.npmrc')


def plano_gitignore(raiz: Path) -> str:
    """Devolve o conteúdo do .gitignore com as linhas sensíveis, sem gravar.

    Acrescenta o que falta e preserva o que já está lá — .gitignore de projeto
    real tem regra que ninguém do DK deve apagar."""
    ignore = Path(raiz) / '.gitignore'
    atual = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    linhas = atual.splitlines()
    novas = [l for l in LINHAS_GITIGNORE if l not in linhas]
    if not novas:
        return atual
    corpo = ('\n'.join(linhas) + '\n\n') if linhas else ''
    return corpo + '\n'.join(novas) + '\n'
