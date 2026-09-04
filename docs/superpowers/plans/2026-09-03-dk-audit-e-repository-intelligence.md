# DK — `dk audit` e Repository Intelligence · Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar ao `dk` a capacidade de entender um repositório que ele acabou de conhecer, sem ler tudo: varredura com política de ignore, classificação, detecção de stack por evidência, mapa progressivo com ranking, e conformidade com o modelo DK — tudo determinístico, antes de qualquer LLM.

**Architecture:** `core/scan` lista sem ler conteúdo. `core/classify` rotula e estima custo. `core/deteccao` identifica stack por evidência real, nunca por nome de diretório. `core/mapa` compõe o mapa progressivo e ranqueia relevância. `core/conformidade` classifica o projeto contra o modelo DK. `bin/dk audit` junta tudo e emite o mapa mais o `llms.txt` do projeto auditado.

**Tech Stack:** Python 3.9+ (stdlib apenas). Sem tree-sitter, sem dependência externa: o nível de símbolo entra num plano futuro, com integração opcional anunciada.

**Spec:** `docs/superpowers/specs/2026-09-03-dk-consolidacao-design.md`
**Plano anterior:** `docs/superpowers/plans/2026-09-03-dk-fundacao-e-espinha.md`

## Global Constraints

Valem todas as do plano anterior, e mais estas:

- **`MAP ANTES DE LER` é verificado por código.** `core/scan.py` não pode conter `read_text`, `read_bytes` nem `open(` sobre arquivo varrido. Varredura usa apenas metadado do sistema de arquivos.
- **Segurança de contexto.** `.env`, `.env.*`, chave privada, certificado e credencial nunca entram no mapa, nem que estejam versionados.
- Detecção de stack por **evidência de arquivo**, nunca por nome de diretório.
- Estimativa de tokens é declarada como estimativa, com a regra de conversão explícita.

## Ajuste de escopo em relação ao plano 1

O plano 1 previa o porte das 27 regras de validação junto com o `dk audit`. Executando, ficou
claro que elas checam estrutura de **projeto de design** — pastas obrigatórias, nome canônico
de entregável, bloco de validação em Visão e Requisitos. Isso depende do padrão de projeto,
que chega com a camada de entregáveis. **As 27 regras passam para o plano 3.** O `dk audit`
deste plano reporta conformidade estrutural sem elas, e ganha as regras quando o padrão existir.

---

## File Structure

| Arquivo | Responsabilidade |
|---|---|
| `core/scan.py` | lista arquivos; ignore e segurança; nunca lê conteúdo |
| `core/classify.py` | tipo, linguagem, categoria, tokens estimados |
| `core/deteccao.py` | stack e tipo de projeto por evidência |
| `core/mapa.py` | mapa progressivo e ranking de relevância |
| `core/conformidade.py` | o projeto usa DK? em que estado? |
| `bin/dk` | subcomando `audit` |
| `skills/dk-audit/SKILL.md` | porta da etapa |
| `agents/dk-audit.md` | orquestrador que enumera a etapa |
| `tests/validate_scan.py` … | um validador por unidade |

---

### Task 1: Varredura com política de ignore e segurança

**Files:**
- Create: `dk/core/scan.py`
- Test: `dk/tests/validate_scan.py`

**Interfaces:**
- Produces: `core.scan.varrer(raiz) -> list[dict]` com `caminho` (relativo), `bytes`, `ext`; `core.scan.IGNORADOS_PADRAO`, `core.scan.SENSIVEIS`, `core.scan.ignorado(rel) -> str` devolvendo o motivo ou `''`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""A varredura lista sem ler, respeita ignore e nunca expõe segredo."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import scan  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'src').mkdir()
    (raiz / 'node_modules' / 'pkg').mkdir(parents=True)
    (raiz / '.git').mkdir()
    (raiz / 'src' / 'app.py').write_text('print(1)\n', encoding='utf-8')
    (raiz / 'README.md').write_text('# projeto\n', encoding='utf-8')
    (raiz / '.env').write_text('SENHA=123\n', encoding='utf-8')
    (raiz / 'chave.pem').write_text('-----BEGIN\n', encoding='utf-8')
    (raiz / 'node_modules' / 'pkg' / 'index.js').write_text('x\n', encoding='utf-8')
    (raiz / '.git' / 'HEAD').write_text('ref\n', encoding='utf-8')
    (raiz / '.gitignore').write_text('build/\n*.log\n', encoding='utf-8')
    (raiz / 'build').mkdir()
    (raiz / 'build' / 'out.js').write_text('y\n', encoding='utf-8')
    (raiz / 'debug.log').write_text('z\n', encoding='utf-8')

    entradas = scan.varrer(raiz)
    caminhos = {e['caminho'] for e in entradas}

    for esperado in ('src/app.py', 'README.md', '.gitignore'):
        if esperado not in caminhos:
            errors.append(f'{esperado} deveria estar na varredura')

    for proibido in ('.env', 'chave.pem'):
        if proibido in caminhos:
            errors.append(f'SEGREDO VAZADO: {proibido} entrou na varredura')

    for proibido in ('node_modules/pkg/index.js', '.git/HEAD',
                     'build/out.js', 'debug.log'):
        if proibido in caminhos:
            errors.append(f'{proibido} deveria ter sido ignorado')

    app = [e for e in entradas if e['caminho'] == 'src/app.py']
    if app and app[0]['bytes'] != 9:
        errors.append(f"bytes errado: {app[0]['bytes']}")
    if app and app[0]['ext'] != '.py':
        errors.append(f"ext errado: {app[0]['ext']}")
    if app and 'conteudo' in app[0]:
        errors.append('a varredura leu o conteúdo do arquivo')

    if not scan.ignorado('node_modules/x'):
        errors.append('ignorado() não reconhece node_modules')
    if scan.ignorado('src/app.py'):
        errors.append('ignorado() marcou arquivo válido')

fonte = (RAIZ / 'core' / 'scan.py').read_text(encoding='utf-8')
for proibida in ('read_text', 'read_bytes'):
    if proibida in fonte:
        errors.append(f'core/scan.py usa {proibida} — MAP ANTES DE LER violado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_scan.py`
Expected: FAIL com `ImportError: cannot import name 'scan'`

- [ ] **Step 3: Implementar `core/scan.py`**

```python
#!/usr/bin/env python3
"""Varredura do repositório: lista, não lê.

O invariante MAP ANTES DE LER começa aqui. A varredura usa só metadado do sistema
de arquivos — nome, tamanho, extensão. Conteúdo é decisão de etapa posterior, e
custa contexto.

A lista de sensíveis não é negociável nem configurável para menos: arquivo de
credencial não entra no mapa nem que esteja versionado, porque o mapa vai para
a LLM."""
from __future__ import annotations
import fnmatch
from pathlib import Path
from typing import List

IGNORADOS_PADRAO = (
    '.git', 'node_modules', 'dist', 'build', 'coverage', '.cache',
    '__pycache__', '.venv', 'venv', '.tox', '.mypy_cache', '.pytest_cache',
    'target', 'vendor', '.next', '.nuxt', '.gradle', '.idea', '.DS_Store',
)

SENSIVEIS = (
    '.env', '.env.*', '*.pem', '*.key', '*.p12', '*.pfx', '*.keystore',
    'id_rsa', 'id_rsa.*', 'id_ed25519', 'id_ed25519.*',
    '*credential*', '*secret*', '.netrc', '.npmrc', '.pypirc',
)

BINARIAS = (
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.pdf', '.zip', '.gz',
    '.tar', '.jar', '.war', '.class', '.so', '.dylib', '.dll', '.exe',
    '.woff', '.woff2', '.ttf', '.otf', '.mp4', '.mov', '.mp3', '.sqlite',
)

_LIMITE_BYTES = 2_000_000


def _casa(nome: str, padroes) -> bool:
    return any(fnmatch.fnmatch(nome, p) or fnmatch.fnmatch(nome.lower(), p)
               for p in padroes)


def ignorado(rel: str, extras=()) -> str:
    """Devolve o motivo do descarte, ou string vazia se o arquivo entra."""
    partes = Path(rel).parts
    nome = Path(rel).name
    if any(p in IGNORADOS_PADRAO for p in partes):
        return 'diretório ignorado por padrão'
    if _casa(nome, SENSIVEIS):
        return 'arquivo sensível'
    for padrao in extras:
        alvo = padrao.rstrip('/')
        if padrao.endswith('/') and alvo in partes:
            return f'.gitignore: {padrao}'
        if fnmatch.fnmatch(rel, alvo) or fnmatch.fnmatch(nome, alvo):
            return f'.gitignore: {padrao}'
    return ''


def _gitignore(raiz: Path) -> List[str]:
    """Padrões simples do .gitignore. Negação e glob duplo ficam de fora:
    o que esta função não entende, ela não finge entender."""
    f = raiz / '.gitignore'
    if not f.exists():
        return []
    padroes = []
    with open(f, encoding='utf-8', errors='replace') as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha or linha.startswith('#') or linha.startswith('!'):
                continue
            padroes.append(linha.lstrip('/'))
    return padroes


def varrer(raiz: Path) -> List[dict]:
    raiz = Path(raiz).resolve()
    extras = _gitignore(raiz)
    entradas = []
    for p in sorted(raiz.rglob('*')):
        if not p.is_file() or p.is_symlink():
            continue
        rel = str(p.relative_to(raiz))
        if ignorado(rel, extras):
            continue
        try:
            tamanho = p.stat().st_size
        except OSError:
            continue
        if tamanho > _LIMITE_BYTES:
            continue
        entradas.append({'caminho': rel, 'bytes': tamanho,
                         'ext': p.suffix.lower()})
    return entradas


def descartados(raiz: Path) -> dict:
    """Contagem do que ficou de fora, por motivo. O mapa declara o que não viu."""
    raiz = Path(raiz).resolve()
    extras = _gitignore(raiz)
    contagem = {}
    for p in raiz.rglob('*'):
        if not p.is_file():
            continue
        motivo = ignorado(str(p.relative_to(raiz)), extras)
        if motivo:
            contagem[motivo] = contagem.get(motivo, 0) + 1
    return contagem
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_scan.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/scan.py tests/validate_scan.py
git commit -m "feat: varredura que lista sem ler, com ignore e guarda de segredo"
```

---

### Task 2: Classificação e estimativa de custo

**Files:**
- Create: `dk/core/classify.py`
- Test: `dk/tests/validate_classify.py`

**Interfaces:**
- Produces: `core.classify.classificar(entrada) -> dict` acrescentando `tipo`, `linguagem`, `categoria`, `tokens_estimados`, `binario`; `core.classify.REGRA_TOKENS`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""Cada arquivo recebe tipo, linguagem, categoria e custo estimado."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import classify  # noqa: E402

errors = []

casos = [
    ({'caminho': 'src/app.py', 'bytes': 400, 'ext': '.py'},
     {'tipo': 'source', 'linguagem': 'python'}),
    ({'caminho': 'package.json', 'bytes': 800, 'ext': '.json'},
     {'tipo': 'config', 'categoria': 'manifesto'}),
    ({'caminho': 'README.md', 'bytes': 1200, 'ext': '.md'},
     {'tipo': 'doc', 'categoria': 'documentacao-raiz'}),
    ({'caminho': 'tests/test_app.py', 'bytes': 300, 'ext': '.py'},
     {'tipo': 'test'}),
    ({'caminho': 'logo.png', 'bytes': 50000, 'ext': '.png'},
     {'tipo': 'asset', 'binario': True}),
]

for entrada, esperado in casos:
    r = classify.classificar(dict(entrada))
    for chave, valor in esperado.items():
        if r.get(chave) != valor:
            errors.append(
                f"{entrada['caminho']}: {chave} esperado {valor!r}, veio {r.get(chave)!r}")

py = classify.classificar({'caminho': 'src/app.py', 'bytes': 400, 'ext': '.py'})
if py['tokens_estimados'] != 100:
    errors.append(f"tokens de 400 B deveriam ser 100, vieram {py['tokens_estimados']}")

png = classify.classificar({'caminho': 'logo.png', 'bytes': 50000, 'ext': '.png'})
if png['tokens_estimados'] != 0:
    errors.append('binário não custa token de leitura; deveria ser 0')

if not classify.REGRA_TOKENS:
    errors.append('a regra de conversão precisa ser declarada, não implícita')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_classify.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/classify.py`**

```python
#!/usr/bin/env python3
"""Rotula cada arquivo e estima o que ele custaria em contexto.

A estimativa é declarada, não escondida: `REGRA_TOKENS` diz a conversão usada, e
todo relatório que mostra número de token repete que é estimativa."""
from __future__ import annotations
from pathlib import Path

REGRA_TOKENS = '~4 bytes por token para texto; binário não é lido, custa 0'

_LINGUAGEM = {
    '.py': 'python', '.js': 'javascript', '.mjs': 'javascript',
    '.ts': 'typescript', '.tsx': 'typescript', '.jsx': 'javascript',
    '.java': 'java', '.go': 'go', '.rb': 'ruby', '.php': 'php',
    '.rs': 'rust', '.kt': 'kotlin', '.swift': 'swift', '.cs': 'csharp',
    '.css': 'css', '.scss': 'scss', '.html': 'html', '.ftl': 'freemarker',
    '.sh': 'shell', '.bash': 'shell', '.sql': 'sql',
}

_CONFIG_EXT = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.properties',
               '.xml', '.env'}
_DOC_EXT = {'.md', '.rst', '.txt', '.adoc'}
_BINARIA = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.pdf', '.zip',
            '.gz', '.tar', '.jar', '.war', '.class', '.so', '.dylib', '.dll',
            '.exe', '.woff', '.woff2', '.ttf', '.otf', '.mp4', '.mov', '.mp3',
            '.sqlite'}

_MANIFESTOS = {
    'package.json', 'pyproject.toml', 'requirements.txt', 'setup.py',
    'pom.xml', 'build.gradle', 'build.gradle.kts', 'go.mod', 'Gemfile',
    'composer.json', 'Cargo.toml', 'pubspec.yaml',
}

_DOC_RAIZ = {'README.md', 'CLAUDE.md', 'AGENTS.md', 'AGENT.md',
             'CONTRIBUTING.md', 'CHANGELOG.md', 'llms.txt', 'llms-full.txt'}


def classificar(entrada: dict) -> dict:
    caminho = entrada['caminho']
    partes = Path(caminho).parts
    nome = Path(caminho).name
    ext = entrada.get('ext', '')

    binario = ext in _BINARIA
    entrada['binario'] = binario
    entrada['linguagem'] = _LINGUAGEM.get(ext, '')

    if binario:
        tipo, categoria = 'asset', 'binario'
    elif nome in _MANIFESTOS:
        tipo, categoria = 'config', 'manifesto'
    elif nome in _DOC_RAIZ and len(partes) == 1:
        tipo, categoria = 'doc', 'documentacao-raiz'
    elif any(p in ('test', 'tests', 'spec', '__tests__') for p in partes) \
            or nome.startswith('test_') or nome.endswith('_test.py'):
        tipo, categoria = 'test', 'teste'
    elif ext in _CONFIG_EXT:
        tipo, categoria = 'config', 'configuracao'
    elif ext in _DOC_EXT:
        tipo, categoria = 'doc', 'documentacao'
    elif entrada['linguagem']:
        tipo, categoria = 'source', 'codigo'
    else:
        tipo, categoria = 'outro', 'nao-classificado'

    entrada['tipo'] = tipo
    entrada['categoria'] = categoria
    entrada['tokens_estimados'] = 0 if binario else entrada['bytes'] // 4
    return entrada
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_classify.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/classify.py tests/validate_classify.py
git commit -m "feat: classificacao de arquivo e estimativa declarada de tokens"
```

---

### Task 3: Detecção de stack por evidência

**Files:**
- Create: `dk/core/deteccao.py`
- Test: `dk/tests/validate_deteccao.py`

**Interfaces:**
- Produces: `core.deteccao.detectar(raiz, entradas) -> dict` com `tipo`, `stack`, `gerenciador`, `evidencias`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""Stack sai de evidência de arquivo, nunca de nome de diretório."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import deteccao, scan  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'package.json').write_text(json.dumps({
        'name': 'app', 'dependencies': {'react': '^18', 'next': '^14'},
    }), encoding='utf-8')
    (raiz / 'pnpm-lock.yaml').write_text('lockfileVersion: 6\n', encoding='utf-8')
    (raiz / 'backend').mkdir()

    r = deteccao.detectar(raiz, scan.varrer(raiz))
    if 'react' not in r['stack']:
        errors.append(f"react não detectado: {r['stack']}")
    if 'next' not in r['stack']:
        errors.append(f"next não detectado: {r['stack']}")
    if r['gerenciador'] != 'pnpm':
        errors.append(f"gerenciador errado: {r['gerenciador']}")
    if 'backend' in r['stack']:
        errors.append('detectou backend por nome de diretório, não por evidência')
    if not r['evidencias']:
        errors.append('nenhuma evidência citada')
    for ev in r['evidencias']:
        if not (raiz / ev.split(':')[0]).exists():
            errors.append(f'evidência aponta para arquivo inexistente: {ev}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'pyproject.toml').write_text(
        '[project]\nname = "x"\ndependencies = ["fastapi"]\n', encoding='utf-8')
    r = deteccao.detectar(raiz, scan.varrer(raiz))
    if 'python' not in r['stack']:
        errors.append(f"python não detectado: {r['stack']}")
    if 'fastapi' not in r['stack']:
        errors.append(f"fastapi não detectado: {r['stack']}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / '.claude-plugin').mkdir()
    (raiz / '.claude-plugin' / 'plugin.json').write_text('{"name":"x"}',
                                                        encoding='utf-8')
    r = deteccao.detectar(raiz, scan.varrer(raiz))
    if r['tipo'] != 'plugin':
        errors.append(f"tipo esperado plugin, veio {r['tipo']}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_deteccao.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/deteccao.py`**

```python
#!/usr/bin/env python3
"""Descobre o que o projeto é, por evidência.

Nome de diretório mente: uma pasta `backend/` pode estar vazia, e um monorepo
pode não ter `packages/`. O que não mente é manifesto, lockfile e arquivo de
configuração — e cada conclusão aqui cita o arquivo que a sustenta."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, List

_LOCKS = {
    'pnpm-lock.yaml': 'pnpm', 'yarn.lock': 'yarn',
    'package-lock.json': 'npm', 'bun.lockb': 'bun',
    'poetry.lock': 'poetry', 'Pipfile.lock': 'pipenv', 'uv.lock': 'uv',
}

_FRAMEWORKS_JS = ('react', 'next', 'vue', 'nuxt', 'angular', '@angular/core',
                  'svelte', 'express', 'nestjs', '@nestjs/core', 'astro',
                  'vite', 'tailwindcss')

_FRAMEWORKS_PY = ('django', 'flask', 'fastapi', 'pydantic', 'sqlalchemy',
                  'pytest', 'celery')


def _ler(raiz: Path, rel: str) -> str:
    p = raiz / rel
    if not p.exists():
        return ''
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def detectar(raiz: Path, entradas: List[dict]) -> Dict:
    raiz = Path(raiz).resolve()
    caminhos = {e['caminho'] for e in entradas}
    stack = []
    evidencias = []
    gerenciador = ''
    tipo = 'indefinido'

    for lock, nome in _LOCKS.items():
        if lock in caminhos:
            gerenciador = nome
            evidencias.append(f'{lock}: gerenciador {nome}')
            break

    if 'package.json' in caminhos:
        stack.append('node')
        evidencias.append('package.json: projeto Node')
        try:
            dados = json.loads(_ler(raiz, 'package.json') or '{}')
        except json.JSONDecodeError:
            dados = {}
        deps = {}
        deps.update(dados.get('dependencies') or {})
        deps.update(dados.get('devDependencies') or {})
        for fw in _FRAMEWORKS_JS:
            if fw in deps:
                curto = fw.split('/')[-1].replace('core', 'angular')
                if curto not in stack:
                    stack.append(curto)
                evidencias.append(f'package.json: dependência {fw}')
        if not gerenciador:
            gerenciador = 'npm'
        if dados.get('workspaces'):
            tipo = 'monorepo'
            evidencias.append('package.json: workspaces declarados')

    if 'pyproject.toml' in caminhos or 'requirements.txt' in caminhos \
            or 'setup.py' in caminhos:
        stack.append('python')
        origem = ('pyproject.toml' if 'pyproject.toml' in caminhos
                  else 'requirements.txt' if 'requirements.txt' in caminhos
                  else 'setup.py')
        evidencias.append(f'{origem}: projeto Python')
        texto = _ler(raiz, origem).lower()
        for fw in _FRAMEWORKS_PY:
            if re.search(rf'\b{re.escape(fw)}\b', texto):
                stack.append(fw)
                evidencias.append(f'{origem}: dependência {fw}')

    for manifesto, linguagem in (('pom.xml', 'java'), ('build.gradle', 'java'),
                                 ('build.gradle.kts', 'kotlin'),
                                 ('go.mod', 'go'), ('Gemfile', 'ruby'),
                                 ('composer.json', 'php'),
                                 ('Cargo.toml', 'rust')):
        if manifesto in caminhos:
            stack.append(linguagem)
            evidencias.append(f'{manifesto}: projeto {linguagem}')

    if '.claude-plugin/plugin.json' in caminhos:
        tipo = 'plugin'
        evidencias.append('.claude-plugin/plugin.json: plugin de Claude Code')
    elif tipo == 'indefinido':
        tem_ui = any(s in stack for s in ('react', 'next', 'vue', 'nuxt',
                                          'angular', 'svelte', 'astro'))
        tem_api = any(s in stack for s in ('express', 'nestjs', 'django',
                                           'flask', 'fastapi', 'java', 'go'))
        if tem_ui and tem_api:
            tipo = 'fullstack'
        elif tem_ui:
            tipo = 'frontend'
        elif tem_api:
            tipo = 'backend'
        elif any(e['tipo'] == 'doc' for e in entradas) and \
                not any(e['tipo'] == 'source' for e in entradas):
            tipo = 'documentacao'

    return {'tipo': tipo, 'stack': stack, 'gerenciador': gerenciador,
            'evidencias': evidencias}
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_deteccao.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/deteccao.py tests/validate_deteccao.py
git commit -m "feat: deteccao de stack por evidencia de arquivo"
```

---

### Task 4: Mapa progressivo com ranking

**Files:**
- Create: `dk/core/mapa.py`
- Test: `dk/tests/validate_mapa.py`

**Interfaces:**
- Produces: `core.mapa.montar(raiz, nivel=2) -> dict` com `projeto`, `estrutura`, `entrypoints`, `configs`, `documentos`, `importantes`, `ignorados`, `metricas`; `core.mapa.NIVEIS`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O mapa é progressivo, ranqueado, e declara o que não olhou."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import mapa  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'src').mkdir()
    (raiz / 'node_modules').mkdir()
    (raiz / 'node_modules' / 'a.js').write_text('x\n', encoding='utf-8')
    (raiz / 'package.json').write_text(json.dumps({'name': 'x'}), encoding='utf-8')
    (raiz / 'README.md').write_text('# x\n' * 50, encoding='utf-8')
    (raiz / 'src' / 'index.js').write_text('export default 1\n', encoding='utf-8')
    (raiz / 'src' / 'util.js').write_text('const a = 1\n', encoding='utf-8')

    m0 = mapa.montar(raiz, nivel=0)
    if 'importantes' in m0 and m0['importantes']:
        errors.append('nível 0 não deveria ranquear')
    if not m0['metricas'].get('arquivos'):
        errors.append('nível 0 deveria contar arquivos')

    m = mapa.montar(raiz, nivel=2)
    if 'package.json' not in m['configs']:
        errors.append(f"package.json fora dos configs: {m['configs']}")
    if 'README.md' not in m['documentos']:
        errors.append(f"README fora dos documentos: {m['documentos']}")

    nomes = [i['caminho'] for i in m['importantes']]
    if 'package.json' not in nomes:
        errors.append('manifesto deveria ser importante')
    altas = [i for i in m['importantes'] if i['importancia'] == 'ALTA']
    if not altas:
        errors.append('nenhum arquivo classificado como ALTA')
    for i in m['importantes']:
        if not i.get('motivo'):
            errors.append(f"{i['caminho']}: importância sem motivo")

    if not m['ignorados']:
        errors.append('o mapa não declara o que ignorou')
    if m['metricas']['tokens_estimados_total'] <= 0:
        errors.append('métrica de token vazia')
    if 'estimativa' not in json.dumps(m['metricas'], ensure_ascii=False).lower():
        errors.append('a métrica de token não se declara estimativa')

    if m['metricas']['arquivos'] != len(
            [1 for _ in (raiz / 'src').iterdir()]) + 2:
        errors.append(f"contagem de arquivos inesperada: {m['metricas']}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_mapa.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/mapa.py`**

```python
#!/usr/bin/env python3
"""Mapa progressivo do repositório.

Níveis, do mais barato ao mais caro. O `dk` sobe de nível só quando a tarefa
exige — é o que impede a leitura do repositório inteiro por reflexo.

    0  sistema de arquivos: quantos arquivos, quanto pesam
    1  tipos: quanto de código, de config, de doc, de teste
    2  arquivos importantes, ranqueados, com motivo

Níveis 3 (símbolos) e 4 (relações) exigem parser e ficam para um plano futuro,
com integração opcional anunciada."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Dict

from core import classify, deteccao, scan

NIVEIS = {0: 'filesystem', 1: 'tipos', 2: 'importantes'}

_ENTRYPOINT = {
    'index.js', 'index.ts', 'main.py', '__main__.py', 'app.py', 'main.go',
    'main.java', 'index.html', 'app.js', 'server.js', 'cli.py',
}


def _importancia(entrada: dict) -> tuple:
    """Devolve (nível, motivo). Regra explícita, não heurística escondida."""
    caminho = entrada['caminho']
    nome = Path(caminho).name
    profundidade = len(Path(caminho).parts)

    if entrada['categoria'] == 'manifesto':
        return 'ALTA', 'manifesto do projeto'
    if entrada['categoria'] == 'documentacao-raiz':
        return 'ALTA', 'documentação de entrada do repositório'
    if nome in _ENTRYPOINT:
        return 'ALTA', 'entrypoint por convenção de nome'
    if entrada['tipo'] == 'config' and profundidade == 1:
        return 'MEDIA', 'configuração na raiz'
    if entrada['tipo'] == 'source' and profundidade <= 2:
        return 'MEDIA', 'código próximo da raiz'
    if entrada['tipo'] == 'test':
        return 'BAIXA', 'teste'
    if entrada['tipo'] == 'asset':
        return 'BAIXA', 'binário, não é lido'
    return 'BAIXA', 'sem sinal de relevância'


def montar(raiz: Path, nivel: int = 2) -> Dict:
    raiz = Path(raiz).resolve()
    entradas = [classify.classificar(e) for e in scan.varrer(raiz)]

    total_bytes = sum(e['bytes'] for e in entradas)
    total_tokens = sum(e['tokens_estimados'] for e in entradas)
    metricas = {
        'arquivos': len(entradas),
        'bytes': total_bytes,
        'tokens_estimados_total': total_tokens,
        'nota': f'estimativa — {classify.REGRA_TOKENS}',
    }

    m = {
        'nivel': nivel,
        'projeto': {},
        'estrutura': {},
        'entrypoints': [],
        'configs': [],
        'documentos': [],
        'importantes': [],
        'ignorados': scan.descartados(raiz),
        'metricas': metricas,
    }

    if nivel <= 0:
        return m

    m['projeto'] = deteccao.detectar(raiz, entradas)
    m['estrutura'] = dict(Counter(e['tipo'] for e in entradas))
    m['metricas']['linguagens'] = dict(
        Counter(e['linguagem'] for e in entradas if e['linguagem']))

    if nivel <= 1:
        return m

    for e in entradas:
        nivel_imp, motivo = _importancia(e)
        if e['categoria'] == 'manifesto' or (
                e['tipo'] == 'config' and len(Path(e['caminho']).parts) == 1):
            m['configs'].append(e['caminho'])
        if e['tipo'] == 'doc':
            m['documentos'].append(e['caminho'])
        if Path(e['caminho']).name in _ENTRYPOINT:
            m['entrypoints'].append(e['caminho'])
        if nivel_imp in ('ALTA', 'MEDIA'):
            m['importantes'].append({
                'caminho': e['caminho'],
                'importancia': nivel_imp,
                'motivo': motivo,
                'tokens_estimados': e['tokens_estimados'],
            })

    ordem = {'ALTA': 0, 'MEDIA': 1, 'BAIXA': 2}
    m['importantes'].sort(key=lambda i: (ordem[i['importancia']], i['caminho']))
    m['metricas']['tokens_dos_importantes'] = sum(
        i['tokens_estimados'] for i in m['importantes'])
    return m
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_mapa.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/mapa.py tests/validate_mapa.py
git commit -m "feat: mapa progressivo com ranking e motivo explicito"
```

---

### Task 5: Conformidade com o modelo DK

**Files:**
- Create: `dk/core/conformidade.py`
- Test: `dk/tests/validate_conformidade.py`

**Interfaces:**
- Produces: `core.conformidade.avaliar(raiz, entradas) -> dict` com `usa_dk`, `classificacao`, `artefatos`, `achados`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O auditor responde: este projeto usa DK? em que estado?"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import conformidade, scan  # noqa: E402

errors = []
VALIDAS = {'COMPATIVEL', 'PARCIALMENTE COMPATIVEL', 'DESATUALIZADO',
           'INCONSISTENTE', 'NAO COMPATIVEL'}

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'src').mkdir()
    (raiz / 'src' / 'a.js').write_text('x\n', encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if r['usa_dk']:
        errors.append('projeto sem artefato DK marcado como usuário de DK')
    if r['classificacao'] != 'NAO COMPATIVEL':
        errors.append(f"esperado NAO COMPATIVEL, veio {r['classificacao']}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'registry').mkdir()
    (raiz / 'registry' / 'requisitos.json').write_text('[]', encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if not r['usa_dk']:
        errors.append('registry/ presente e não reconheceu uso de DK')
    if r['classificacao'] not in VALIDAS:
        errors.append(f"classificação inválida: {r['classificacao']}")
    if r['classificacao'] == 'COMPATIVEL':
        errors.append('projeto só com registry não deveria ser COMPATIVEL')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for sub in ('registry', '0-apoio', 'docs'):
        (raiz / sub).mkdir()
    (raiz / 'registry' / 'requisitos.json').write_text('[]', encoding='utf-8')
    (raiz / 'registry' / 'regras.json').write_text('[]', encoding='utf-8')
    (raiz / 'projeto.yml').write_text('nome: x\n', encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if r['classificacao'] not in ('COMPATIVEL', 'PARCIALMENTE COMPATIVEL'):
        errors.append(f"projeto completo classificado como {r['classificacao']}")
    if not r['artefatos']:
        errors.append('nenhum artefato listado')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'registry').mkdir()
    (raiz / 'registry' / 'requisitos.json').write_text('nao e json',
                                                       encoding='utf-8')
    r = conformidade.avaliar(raiz, scan.varrer(raiz))
    if r['classificacao'] != 'INCONSISTENTE':
        errors.append(f"registry quebrado deveria dar INCONSISTENTE, "
                      f"veio {r['classificacao']}")
    if not r['achados']:
        errors.append('inconsistência sem achado descrito')
    for a in r['achados']:
        if not a.get('evidencia'):
            errors.append(f'achado sem evidência: {a}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_conformidade.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/conformidade.py`**

```python
#!/usr/bin/env python3
"""O projeto segue o modelo DK? E em que estado?

Classificação com cinco estados. `INCONSISTENTE` ganha de todos os outros: um
registro que não abre é pior que um registro que falta, porque quem lê acha que
tem informação e não tem."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

ARTEFATOS = {
    'registry/requisitos.json': 'registro de requisitos',
    'registry/regras.json': 'registro de regras de negócio',
    'registry/decisions.json': 'registro de decisões',
    'projeto.yml': 'manifesto do projeto',
    'llms.txt': 'roteador para agentes',
    '.claude-plugin/plugin.json': 'manifesto de plugin',
}

_NUCLEO = ('registry/requisitos.json', 'registry/regras.json', 'projeto.yml')


def avaliar(raiz: Path, entradas: List[dict]) -> Dict:
    raiz = Path(raiz).resolve()
    caminhos = {e['caminho'] for e in entradas}
    achados = []

    presentes = {c: d for c, d in ARTEFATOS.items() if c in caminhos}
    usa_dk = bool(presentes)

    for caminho in presentes:
        if not caminho.endswith('.json'):
            continue
        try:
            json.loads((raiz / caminho).read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError) as exc:
            achados.append({
                'id': 'CONF-JSON',
                'titulo': f'{caminho} não é JSON válido',
                'evidencia': f'{caminho}: {exc.__class__.__name__}',
                'impacto': 'alto',
            })

    if not usa_dk:
        classificacao = 'NAO COMPATIVEL'
    elif achados:
        classificacao = 'INCONSISTENTE'
    else:
        nucleo = [c for c in _NUCLEO if c in presentes]
        if len(nucleo) == len(_NUCLEO):
            classificacao = 'COMPATIVEL'
        elif nucleo:
            classificacao = 'PARCIALMENTE COMPATIVEL'
            faltando = [c for c in _NUCLEO if c not in presentes]
            achados.append({
                'id': 'CONF-NUCLEO',
                'titulo': 'artefato de núcleo ausente',
                'evidencia': 'ausentes: ' + ', '.join(faltando),
                'impacto': 'medio',
            })
        else:
            classificacao = 'PARCIALMENTE COMPATIVEL'
            achados.append({
                'id': 'CONF-PERIFERIA',
                'titulo': 'só artefatos periféricos do DK presentes',
                'evidencia': 'presentes: ' + ', '.join(sorted(presentes)),
                'impacto': 'medio',
            })

    return {
        'usa_dk': usa_dk,
        'classificacao': classificacao,
        'artefatos': [{'caminho': c, 'papel': d} for c, d in sorted(presentes.items())],
        'achados': achados,
    }
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_conformidade.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/conformidade.py tests/validate_conformidade.py
git commit -m "feat: classificacao de conformidade do projeto com o modelo DK"
```

---

### Task 6: `dk audit` na CLI, com `llms.txt` do projeto

**Files:**
- Modify: `dk/bin/dk` (novo subcomando `audit`)
- Test: `dk/tests/validate_audit_cli.py`

**Interfaces:**
- Consumes: `core.mapa.montar`, `core.conformidade.avaliar`, `core.ops`, `core.leitura`
- Produces: `dk audit --projeto <raiz> [--nivel N] [--json] [--apply]`; grava `.dk/mapa.json` e propõe `llms.txt` do projeto

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O audit roda, simula por padrão, e o llms.txt que ele propõe é derivado do mapa."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'src').mkdir()
    (raiz / 'package.json').write_text(
        json.dumps({'name': 'demo', 'dependencies': {'react': '^18'}}),
        encoding='utf-8')
    (raiz / 'README.md').write_text('# demo\n', encoding='utf-8')
    (raiz / 'src' / 'index.js').write_text('export default 1\n', encoding='utf-8')

    seco = dk('audit', '--projeto', str(raiz))
    if seco.returncode != 0:
        errors.append(f'audit falhou: {seco.stdout}{seco.stderr}')
    if (raiz / '.dk' / 'mapa.json').exists():
        errors.append('a simulação gravou o mapa')
    if (raiz / 'llms.txt').exists():
        errors.append('a simulação gravou o llms.txt')
    for esperado in ('react', 'NAO COMPATIVEL', 'estimativa'):
        if esperado not in seco.stdout:
            errors.append(f'{esperado!r} ausente da saída do audit')

    j = dk('audit', '--projeto', str(raiz), '--json')
    if j.returncode != 0:
        errors.append('audit --json falhou')
    else:
        try:
            dados = json.loads(j.stdout)
        except json.JSONDecodeError as exc:
            dados = {}
            errors.append(f'--json não emitiu JSON: {exc}')
        for chave in ('projeto', 'metricas', 'conformidade', 'importantes'):
            if chave not in dados:
                errors.append(f'--json sem a chave {chave}')

    ap = dk('audit', '--projeto', str(raiz), '--apply')
    if ap.returncode != 0:
        errors.append(f'audit --apply falhou: {ap.stdout}{ap.stderr}')
    if not (raiz / '.dk' / 'mapa.json').exists():
        errors.append('--apply não gravou .dk/mapa.json')
    if not (raiz / 'llms.txt').exists():
        errors.append('--apply não gravou llms.txt')
    else:
        texto = (raiz / 'llms.txt').read_text(encoding='utf-8')
        if 'react' not in texto:
            errors.append('o llms.txt não reflete a stack detectada')
        if 'README.md' not in texto:
            errors.append('o llms.txt não aponta os documentos do projeto')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_audit_cli.py`
Expected: FAIL — `invalid choice: 'audit'`

- [ ] **Step 3: Acrescentar o subcomando ao `bin/dk`**

Acrescente o import de `mapa` e `conformidade`, a função abaixo, e o parser.

```python
def _llms_do_projeto(m: dict, conf: dict) -> str:
    proj = m['projeto']
    linhas = ['# ' + Path(m['raiz']).name, '']
    if proj.get('stack'):
        linhas.append(f"Projeto {proj.get('tipo', 'indefinido')} — "
                      f"{', '.join(proj['stack'])}.")
    else:
        linhas.append(f"Projeto {proj.get('tipo', 'indefinido')}.")
    if proj.get('gerenciador'):
        linhas.append(f"Gerenciador: {proj['gerenciador']}.")
    linhas += ['', '## Conformidade com o DK', '',
               f"- Estado: {conf['classificacao']}"]
    for a in conf['artefatos']:
        linhas.append(f"- {a['caminho']} — {a['papel']}")
    if m['entrypoints']:
        linhas += ['', '## Entrypoints', '']
        linhas += [f'- {c}' for c in m['entrypoints']]
    if m['configs']:
        linhas += ['', '## Configuração', '']
        linhas += [f'- {c}' for c in m['configs']]
    if m['documentos']:
        linhas += ['', '## Documentos', '']
        linhas += [f'- {c}' for c in m['documentos'][:20]]
    linhas += ['', '## Custo de contexto', '',
               f"- {m['metricas']['arquivos']} arquivos mapeados",
               f"- {m['metricas']['tokens_estimados_total']} tokens no total "
               f"({m['metricas']['nota']})",
               f"- {m['metricas'].get('tokens_dos_importantes', 0)} tokens "
               'nos arquivos importantes', '']
    return '\n'.join(linhas)


def cmd_audit(args) -> int:
    projeto = Path(args.projeto).resolve()
    m = mapa.montar(projeto, nivel=args.nivel)
    m['raiz'] = str(projeto)
    entradas = [{'caminho': i['caminho']} for i in m['importantes']]
    from core import scan as _scan
    conf = conformidade.avaliar(projeto, _scan.varrer(projeto))

    if args.json:
        print(json.dumps({
            'projeto': m['projeto'], 'estrutura': m['estrutura'],
            'metricas': m['metricas'], 'conformidade': conf,
            'importantes': m['importantes'], 'ignorados': m['ignorados'],
        }, ensure_ascii=False, indent=2))
        return 0

    texto_llms = _llms_do_projeto(m, conf)
    op = ops.Operacao(projeto, escopo=['.dk', 'llms.txt'])
    planos = [
        op.planejar(projeto / '.dk' / 'mapa.json',
                    json.dumps(m, ensure_ascii=False, indent=2) + '\n'),
        op.planejar(projeto / 'llms.txt', texto_llms),
    ]

    proj = m['projeto']
    print(f"tipo: {proj.get('tipo')} · stack: {', '.join(proj.get('stack')) or '—'}"
          f" · gerenciador: {proj.get('gerenciador') or '—'}")
    for ev in proj.get('evidencias', []):
        print(f'  evidência: {ev}')
    print(f"conformidade com o DK: {conf['classificacao']}")
    for a in conf['achados']:
        print(f"  {a['id']}: {a['titulo']} — {a['evidencia']}")
    print(f"{m['metricas']['arquivos']} arquivos · "
          f"{m['metricas']['tokens_estimados_total']} tokens "
          f"({m['metricas']['nota']})")
    for motivo, n in sorted(m['ignorados'].items()):
        print(f'  ignorados {n}: {motivo}')

    if not args.apply:
        for p in planos:
            print(f"{p['acao']}: {p['caminho']}")
        print('simulação — nada foi gravado. Use --apply para aplicar.')
        return 0

    op.aplicar()
    print(f"gravado: .dk/mapa.json e llms.txt")
    return 0
```

E no `main()`:

```python
    aud = sub.add_parser('audit', help='mapeia o projeto e avalia conformidade')
    aud.add_argument('--projeto', required=True)
    aud.add_argument('--nivel', type=int, default=2, choices=(0, 1, 2))
    aud.add_argument('--json', action='store_true')
    aud.add_argument('--apply', action='store_true',
                     help='grava .dk/mapa.json e llms.txt; sem a flag, simula')
    aud.set_defaults(func=cmd_audit)
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_audit_cli.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add bin/dk tests/validate_audit_cli.py
git commit -m "feat: dk audit com mapa, conformidade e llms.txt do projeto"
```

---

### Task 7: Porta e agente da etapa `audit`

**Files:**
- Create: `dk/skills/dk-audit/SKILL.md`
- Create: `dk/skills/dk-audit-conformidade/SKILL.md`
- Create: `dk/agents/dk-audit.md`

- [ ] **Step 1: Criar a porta**

```markdown
---
name: dk-audit
description: Porta da etapa de auditoria do DK. Use quando o trabalho for entender um projeto que você acabou de abrir - qual a stack, qual a estrutura, o que já existe, se ele segue o modelo do Kit e onde estão as inconsistências. É a primeira etapa: ela produz o estado que as demais são obrigadas a consultar.
argument-hint: "[caminho do projeto, ou vazio para o diretório atual]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: tabela
---

# dk-audit — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Rode `bin/dk audit --projeto <raiz>` em simulação. **Não leia arquivo antes disso**:
   o mapa é que diz o que vale abrir.
2. Leia o mapa. Só então abra os arquivos que ele marcou como ALTA, e apenas os que
   a pergunta do usuário exige.
3. Se o usuário quiser persistir o mapa e o `llms.txt` do projeto, rode com `--apply`.

## Regras

- Nunca leia o repositório inteiro. MAP → SELECT → READ.
- Toda conclusão aponta para arquivo. Stack sem evidência de arquivo não é afirmada.
- O que foi ignorado é declarado, não escondido.

## Resposta

Tabela com tipo, stack, conformidade e custo estimado, mais uma frase com o achado
de maior impacto.
```

- [ ] **Step 2: Criar a skill de conformidade**

```markdown
---
name: dk-audit-conformidade
description: Classifica o projeto contra o modelo DK - compatível, parcialmente compatível, desatualizado, inconsistente ou não compatível - e lista os artefatos encontrados com o papel de cada um. Use quando a etapa audit do DK estiver ativa e a pergunta for sobre aderência ao Kit, não sobre a stack.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-audit-conformidade

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Rode `bin/dk audit --projeto <raiz> --json` e leia o bloco `conformidade`.
2. Para cada achado, confirme a evidência abrindo só o arquivo citado.
3. Classifique e proponha o próximo passo: qual artefato falta, qual está quebrado.

## Regras

- `INCONSISTENTE` ganha de qualquer outra classificação: registro que não abre é pior
  que registro ausente, porque quem lê acha que tem informação.
- Achado sem evidência de arquivo não é reportado.

## Resposta

Tabela com artefato, papel e estado, e uma frase com a classificação final e o motivo.
```

- [ ] **Step 3: Criar o agente**

```markdown
---
name: dk-audit
description: Orquestrador da etapa de auditoria do DK — entender o projeto antes de tocar nele.
---

# Etapa: audit

Primeira etapa. Produz o mapa e o estado que as demais consultam.

## Invariantes da etapa

- MAP → SELECT → READ. O mapa vem antes de qualquer leitura de arquivo.
- Nenhuma conclusão sem evidência de arquivo.
- O que foi ignorado é declarado.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-audit-conformidade` | a pergunta é sobre aderência ao modelo DK |

Para mapa, stack e custo de contexto, a própria porta `dk-audit` resolve pela CLI.

## Procedimento

1. Rode a auditoria em simulação.
2. Escolha a skill pela natureza da pergunta.
3. Informe o achado de maior impacto em uma frase.
```

- [ ] **Step 4: Rodar a bateria**

Run: `python3 verificar.py`
Expected: tudo verde, incluindo `validate_enumeracao` e `validate_portao_e_orcamento`

- [ ] **Step 5: Commit**

```bash
git add skills/dk-audit skills/dk-audit-conformidade agents/dk-audit.md
git commit -m "feat: porta e agente da etapa audit"
```

---

### Task 8: Dogfooding — o `dk` auditando o próprio `dk`

**Files:**
- Test: `dk/tests/validate_dogfooding.py`

**Interfaces:**
- Consumes: `bin/dk audit`

- [ ] **Step 1: Escrever o teste**

```python
#!/usr/bin/env python3
"""O dk consegue mapear a si mesmo, e se reconhece como projeto DK.

É o teste que a spec chama de dogfooding: se o auditor não entende o próprio
repositório, ele não entende repositório nenhum."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []

r = subprocess.run(
    [sys.executable, str(RAIZ / 'bin' / 'dk'), 'audit',
     '--projeto', str(RAIZ), '--json'],
    capture_output=True, text=True)

if r.returncode != 0:
    errors.append(f'audit sobre o próprio dk falhou: {r.stdout}{r.stderr}')
else:
    m = json.loads(r.stdout)

    if m['projeto']['tipo'] != 'plugin':
        errors.append(f"o dk deveria se detectar como plugin, "
                      f"veio {m['projeto']['tipo']}")
    if 'python' not in m['projeto']['stack']:
        errors.append(f"stack sem python: {m['projeto']['stack']}")

    if not m['conformidade']['usa_dk']:
        errors.append('o dk não se reconhece como projeto DK')
    if m['conformidade']['achados']:
        for a in m['conformidade']['achados']:
            if a['impacto'] == 'alto':
                errors.append(f"achado alto no próprio dk: {a['titulo']} — "
                              f"{a['evidencia']}")

    nomes = {i['caminho'] for i in m['importantes']}
    for esperado in ('llms.txt', 'CLAUDE.md', '.claude-plugin/plugin.json'):
        if esperado not in nomes:
            errors.append(f'{esperado} deveria ser importante no próprio dk')

    if m['metricas']['arquivos'] < 20:
        errors.append(f"mapeou só {m['metricas']['arquivos']} arquivos do dk")

    for caminho in nomes:
        if not (RAIZ / caminho).exists():
            errors.append(f'o mapa aponta {caminho}, que não existe')

    ignorados = json.dumps(m['ignorados'], ensure_ascii=False)
    if '.git' not in ignorados:
        errors.append('o mapa não declara ter ignorado o .git')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar**

Run: `python3 tests/validate_dogfooding.py`
Expected: PASS

- [ ] **Step 3: Acrescentar ao portão de release**

Em `tests/validate_release_gate.py`, acrescente à lista `ITENS`:

```python
    ('dogfooding: o dk audita o próprio dk', 'tests/validate_dogfooding.py'),
    ('varredura sem leitura e sem segredo', 'tests/validate_scan.py'),
```

- [ ] **Step 4: Conferir o portão**

Run: `python3 verificar.py --release`
Expected: `portão de release aberto`, agora com 13 itens

- [ ] **Step 5: Commit**

```bash
git add tests/validate_dogfooding.py tests/validate_release_gate.py
git commit -m "test: dogfooding do audit sobre o proprio repositorio"
```

---

## Cobertura da spec

Este plano entrega a camada Repository Intelligence (seção 4.2 da spec, etapa `audit`),
o invariante `MAP ANTES DE LER` (4.4) e o `llms.txt` do projeto auditado.

Fica para os planos seguintes: níveis 3 e 4 do mapa — símbolos e relações — que exigem
parser e entram como integração opcional anunciada; e as 27 regras de validação, movidas
para o plano 3 pelo motivo declarado no topo deste documento.

## Depois deste plano

1. Camada de entregável — as 9 skills do community, com o pipeline HTML canônico, e as
   27 regras de validação junto com o padrão de projeto
2. Etapa `entender` — cobertura, lacuna e léxico, portadas do Kit
3. `modules/design-system/` — cruzamento DLS × Kit
4. Os demais módulos: git-workflow, liferay-migration, similar-analysis, lean-inception
5. Congelamento das duas bases antigas, com inspeção prévia dos sete clones
