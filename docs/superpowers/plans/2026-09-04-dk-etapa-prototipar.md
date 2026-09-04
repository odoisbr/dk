# DK — Etapa `prototipar` · Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fechar a dor nº 2 relatada pelo time — "pede um ajuste, ele faz mais coisa, foge do padrão e quebra o que já foi construído". Todo ajuste no protótipo passa a abrir um **changeset** que declara o alvo antes de tocar em qualquer arquivo, e o padrão passa a ser verificado por código.

**Architecture:** `core/changeset` porta o modelo do `sea-dls` — id, título, origem, **`affected`**, validação, resultado — e o campo `affected` alimenta direto o `escopo` do `ops.Operacao`, que já recusa escrita fora dele. `core/prototipo` implementa as regras 7 a 15 do validador do Kit, as que dizem o que é "fugir do padrão". `core/componente` valida o contrato de componente contra o schema do DLS.

**Tech Stack:** Python 3.9+ (stdlib apenas).

**Spec:** `docs/superpowers/specs/2026-09-03-dk-consolidacao-design.md`
**Planos anteriores:** fundação e espinha · audit · camada de entregável · etapa entender

## Global Constraints

Valem todas as dos planos anteriores, e mais estas:

- **Nada é editado fora do `affected` do changeset.** Não é convenção: `ops.Operacao`
  levanta `ForaDoEscopo` e a operação inteira falha.
- **O modelo canônico manda.** Tokens e contrato de componente são fonte; HTML, CSS e
  build são saída. Editar a saída direto é o que produz divergência silenciosa — o
  orquestrador do Kit já registrava isso, sem ter como impedir.
- **Regra do padrão que o código consegue verificar, o código verifica.** Valor cru onde
  devia haver token é a forma mais comum de "fugir do padrão", e é detectável.

## Por que esta etapa antes dos entregáveis de comunicação

Das três dores relatadas, duas estão fechadas: requisito ignorado (etapas `levantar` e
`entender`) e prolixidade (contrato de resposta). A terceira — o protótipo mexer no que
não devia — segue aberta. Os invariantes que a resolvem já existem no núcleo desde o plano
1; falta a etapa que os usa. Entregáveis de comunicação passam para o plano 6.

## O que é portado, e de onde

| Capacidade | Origem | Forma no `dk` |
|---|---|---|
| Modelo de changeset com `affected` | `sea-dls/schemas/changeset.schema.json` | `core/changeset.py` |
| Contrato de componente | `sea-dls/schemas/component.schema.json` | `core/componente.py` |
| Regras 7, 8, 12, 13, 14, 15 | validador do Kit | `core/prototipo.py` |
| Tokens como fonte canônica, saída como derivado | orquestrador de protótipo do Kit | invariante da etapa |

---

### Task 1: Changeset — o escopo declarado antes do primeiro byte

**Files:**
- Create: `dk/core/changeset.py`
- Test: `dk/tests/validate_changeset.py`

**Interfaces:**
- Produces: `core.changeset.abrir(id, titulo, origem, afetados) -> dict`,
  `core.changeset.validar(cs) -> list[dict]`,
  `core.changeset.operacao(raiz, cs, registro=None) -> ops.Operacao`,
  `core.changeset.fechar(cs, resultado, escritos) -> dict`

- [ ] **Step 1: Escrever o teste que falha**

```python
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
ids = {a['id'] for a in changeset.validar(vazio)}
if 'CS-SEM-ALVO' not in ids:
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

    fechado = changeset.fechar(cs, 'espaçamento ajustado', escritos)
    if fechado['status'] != 'fechado':
        errors.append('fechar() não mudou o status')
    if not fechado['result']:
        errors.append('changeset fechado sem resultado')
    if str(alvo) not in ' '.join(fechado['escritos']):
        errors.append('o changeset fechado não registra o que foi escrito')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_changeset.py`
Expected: FAIL com `ImportError: cannot import name 'changeset'`

- [ ] **Step 3: Implementar `core/changeset.py`**

```python
#!/usr/bin/env python3
"""Changeset: o que vai mudar, declarado antes de mudar.

Modelo portado do `sea-dls`. O campo que importa é `affected` — ele vira o escopo
do envelope de escrita, e o envelope recusa qualquer caminho fora dele.

É a resposta direta à dor relatada: pediram ajuste numa tela e a ferramenta
alterou outras três. Aqui isso não é uma questão de disciplina do agente; é uma
exceção em tempo de execução."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

from core import ops

CAMPOS = ('id', 'title', 'status', 'source', 'affected', 'validation', 'result')


def abrir(ident: str, titulo: str, origem: str,
          afetados: List[str]) -> Dict:
    return {
        'id': ident,
        'title': titulo,
        'status': 'aberto',
        'source': origem,
        'affected': list(afetados),
        'validation': [],
        'result': '',
        'escritos': [],
    }


def validar(cs: Dict) -> List[Dict]:
    achados = []
    if not cs.get('affected'):
        achados.append({
            'id': 'CS-SEM-ALVO',
            'titulo': 'changeset sem alvo declarado',
            'evidencia': f"{cs.get('id')}: `affected` vazio — sem alvo não há "
                         'escopo, e sem escopo a escrita não é contida',
            'impacto': 'alto',
        })
    if not str(cs.get('source') or '').strip():
        achados.append({
            'id': 'CS-SEM-ORIGEM',
            'titulo': 'changeset sem origem',
            'evidencia': f"{cs.get('id')}: `source` vazio — mudança sem pedido "
                         'rastreável é mudança que ninguém pediu',
            'impacto': 'alto',
        })
    if not str(cs.get('title') or '').strip():
        achados.append({
            'id': 'CS-SEM-TITULO',
            'titulo': 'changeset sem título',
            'evidencia': f"{cs.get('id')}: `title` vazio",
            'impacto': 'medio',
        })
    return achados


def operacao(raiz: Path, cs: Dict, registro=None) -> ops.Operacao:
    """O envelope de escrita da mudança. `affected` é o escopo, sem exceção."""
    return ops.Operacao(raiz, escopo=cs['affected'], registro=registro,
                        fontes=cs.get('fontes') or [])


def fechar(cs: Dict, resultado: str, escritos: List[Path]) -> Dict:
    fechado = dict(cs)
    fechado['status'] = 'fechado'
    fechado['result'] = resultado
    fechado['escritos'] = [str(p) for p in escritos]
    return fechado
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_changeset.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/changeset.py tests/validate_changeset.py
git commit -m "feat: changeset com affected como escopo declarado da mudanca"
```

---

### Task 2: As regras do padrão de protótipo

**Files:**
- Create: `dk/core/prototipo.py`
- Test: `dk/tests/validate_prototipo.py`

**Interfaces:**
- Produces: `core.prototipo.verificar(raiz) -> list[dict]` cobrindo as regras 7, 8, 12, 13, 14 e 15

Estas são as regras que dizem o que é "fugir do padrão". A 14 — variável de tema com
valor cru em vez de token — é a forma mais comum, e a mais fácil de passar despercebida
numa revisão humana.

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""As regras que dizem o que é fugir do padrão, verificadas por código."""
from __future__ import annotations
import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, prototipo  # noqa: E402

errors = []


def projeto_limpo(raiz: Path) -> Path:
    base = raiz / '2-design' / 'prototipo'
    io.atomic_write(base / 'index.html', '<a href="/vitrine">vitrine</a>')
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:var(--token-blue)}')
    return base


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    projeto_limpo(raiz)
    achados = prototipo.verificar(raiz)
    if achados:
        errors.append(f'protótipo limpo não deveria ter achado: {achados}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'vendor' / 'design-system' / 'ds.css', '.x{}')
    if 7 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('cópia vendorizada de design system deveria reprovar (7)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = raiz / '2-design' / 'prototipo'
    io.atomic_write(base / 'index.html', '<p>sem rota</p>')
    io.atomic_write(base / 'styles' / 'tema.css', ':root{--a:var(--b)}')
    if 8 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('protótipo sem rota de vitrine deveria reprovar (8)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'index.html',
                    '<link href="bootstrap.min.css"><a href="/vitrine">v</a>')
    if 12 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('framework CSS concorrente deveria reprovar (12)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'index.html',
                    '<div data-bs-toggle="modal"></div><a href="/vitrine">v</a>')
    if 13 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('API exclusiva do Bootstrap 5 deveria reprovar (13)')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:#009CC5;--espaco:12px}')
    achados = [a for a in prototipo.verificar(raiz) if a['regra'] == 14]
    if not achados:
        errors.append('variável de tema com valor cru deveria reprovar (14)')
    elif '--cor-primaria' not in achados[0]['evidencia']:
        errors.append(f"a evidência não nomeia a variável: {achados[0]['evidencia']}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = projeto_limpo(raiz)
    fonte = base / 'styles' / 'tema.scss'
    saida = base / 'styles' / 'tema.css'
    io.atomic_write(saida, ':root{--a:var(--b)}')
    time.sleep(0.01)
    io.atomic_write(fonte, '// fonte mais nova')
    os.utime(fonte, (time.time(), time.time()))
    if 15 not in {a['regra'] for a in prototipo.verificar(raiz)}:
        errors.append('saída compilada mais velha que a fonte deveria reprovar (15)')

for a in prototipo.verificar(Path(tempfile.mkdtemp())):
    if not a.get('evidencia'):
        errors.append(f'achado sem evidência: {a}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_prototipo.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/prototipo.py`**

```python
#!/usr/bin/env python3
"""As regras do protótipo, portadas do validador do Kit.

São as que dizem, objetivamente, o que é "fugir do padrão". A regra 14 —
variável de tema apontando para valor cru em vez de token — é a que mais escapa
numa revisão humana: o resultado visual fica idêntico, e a ligação com o design
system se perde em silêncio."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

BASE = '2-design/prototipo'

_FRAMEWORKS = ('bootstrap', 'tailwind', 'bulma', 'foundation', 'materialize')
_VALOR_CRU = re.compile(
    r'--([a-z0-9-]*(?:cor|color|espaco|space|fonte|font|raio|radius|sombra|'
    r'shadow)[a-z0-9-]*)\s*:\s*'
    r'(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\)|\d+(?:\.\d+)?(?:px|rem|em))',
    re.I)


def _arquivos(base: Path, *sufixos) -> List[Path]:
    if not base.is_dir():
        return []
    return [p for p in sorted(base.rglob('*'))
            if p.is_file() and p.suffix.lower() in sufixos]


def verificar(raiz: Path) -> List[Dict]:
    raiz = Path(raiz)
    base = raiz / BASE
    achados = []
    if not base.is_dir():
        return achados

    def achado(regra, titulo, evidencia, impacto='medio'):
        achados.append({'regra': regra, 'titulo': titulo,
                        'evidencia': evidencia, 'impacto': impacto})

    # 7 — cópia vendorizada de design system
    for p in base.rglob('*'):
        if not p.is_file():
            continue
        partes = [x.lower() for x in p.relative_to(base).parts]
        if 'vendor' in partes and any('design-system' in x or 'design_system' in x
                                      for x in partes):
            achado(7, 'Protótipo sem cópia vendorizada de design system',
                   f'{p.relative_to(raiz)}: cópia local do design system — '
                   'a fonte é o pacote, não a cópia', 'alto')
            break

    # 8 — rota de vitrine
    html = _arquivos(base, '.html', '.htm')
    if html:
        texto = '\n'.join(p.read_text(encoding='utf-8', errors='replace')
                          for p in html)
        if 'vitrine' not in texto.lower() and 'showcase' not in texto.lower():
            achado(8, 'Protótipo com rota de vitrine',
                   f'{len(html)} arquivo(s) HTML e nenhuma referência a '
                   'vitrine ou showcase')

    # 12 e 13 — framework concorrente e API exclusiva do Bootstrap 5
    for p in html + _arquivos(base, '.css', '.scss', '.js'):
        conteudo = p.read_text(encoding='utf-8', errors='replace')
        baixo = conteudo.lower()
        for fw in _FRAMEWORKS:
            if fw in baixo:
                achado(12, 'Sem framework CSS concorrente',
                       f'{p.relative_to(raiz)}: menciona {fw}', 'alto')
                break
        if 'data-bs-' in baixo:
            achado(13, 'Sem API exclusiva do Bootstrap 5 (`data-bs-*`)',
                   f'{p.relative_to(raiz)}: usa data-bs-*', 'alto')

    # 14 — variável de tema derivada de token, não de valor cru
    for p in _arquivos(base, '.css', '.scss'):
        conteudo = p.read_text(encoding='utf-8', errors='replace')
        for nome, valor in _VALOR_CRU.findall(conteudo):
            achado(14, 'Variáveis de tema derivadas de token, não de valor cru',
                   f'{p.relative_to(raiz)}: --{nome} recebe {valor} direto, '
                   'em vez de var(--token-…)', 'alto')

    # 15 — saída compilada mais nova que a fonte
    for fonte in _arquivos(base, '.scss'):
        saida = fonte.with_suffix('.css')
        if saida.exists() and saida.stat().st_mtime < fonte.stat().st_mtime:
            achado(15, 'Saída compilada mais nova que a fonte SCSS',
                   f'{saida.relative_to(raiz)} é mais velho que '
                   f'{fonte.relative_to(raiz)} — o build não rodou')

    return achados
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_prototipo.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/prototipo.py tests/validate_prototipo.py
git commit -m "feat: regras do padrao de prototipo verificadas por codigo"
```

---

### Task 3: `dk prototipar` na CLI

**Files:**
- Modify: `dk/bin/dk`
- Test: `dk/tests/validate_prototipar_cli.py`

**Interfaces:**
- Produces:
  `dk prototipar --projeto <raiz> --changeset <id> --titulo <t> --origem <o> --alvo <caminho>... [--apply]`
  e `dk prototipar --projeto <raiz> --verificar`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O prototipar abre changeset, verifica o padrão e recusa alvo não declarado."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    base = raiz / '2-design' / 'prototipo'
    io.atomic_write(base / 'index.html', '<a href="/vitrine">vitrine</a>')
    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:#009CC5}')

    v = dk('prototipar', '--projeto', str(raiz), '--verificar')
    if v.returncode == 0:
        errors.append('valor cru no tema deveria reprovar a verificação')
    if 'regra 14' not in v.stdout and '14' not in v.stdout:
        errors.append('a verificação não citou a regra violada')
    if '--cor-primaria' not in v.stdout:
        errors.append('a verificação não nomeou a variável')

    io.atomic_write(base / 'styles' / 'tema.css',
                    ':root{--cor-primaria:var(--token-blue)}')
    v2 = dk('prototipar', '--projeto', str(raiz), '--verificar')
    if v2.returncode != 0:
        errors.append(f'protótipo corrigido deveria passar: {v2.stdout}')

    seco = dk('prototipar', '--projeto', str(raiz),
              '--changeset', 'CS-001', '--titulo', 'ajuste do card',
              '--origem', 'pedido em 04/09',
              '--alvo', '2-design/prototipo/styles')
    if seco.returncode != 0:
        errors.append(f'abrir changeset falhou: {seco.stdout}{seco.stderr}')
    for esperado in ('CS-001', 'affected', '2-design/prototipo/styles'):
        if esperado not in seco.stdout:
            errors.append(f'{esperado!r} ausente da saída')
    if 'simulação' not in seco.stdout:
        errors.append('sem --apply deveria simular')

    sem_alvo = dk('prototipar', '--projeto', str(raiz),
                  '--changeset', 'CS-002', '--titulo', 'x', '--origem', 'y')
    if sem_alvo.returncode == 0:
        errors.append('changeset sem alvo deveria reprovar')
    if 'CS-SEM-ALVO' not in sem_alvo.stdout:
        errors.append('a recusa não citou CS-SEM-ALVO')

    sem_origem = dk('prototipar', '--projeto', str(raiz),
                    '--changeset', 'CS-003', '--titulo', 'x', '--origem', '',
                    '--alvo', '2-design/prototipo/styles')
    if sem_origem.returncode == 0:
        errors.append('changeset sem origem deveria reprovar')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_prototipar_cli.py`
Expected: FAIL — `invalid choice: 'prototipar'`

- [ ] **Step 3: Acrescentar o subcomando**

```python
def cmd_prototipar(args) -> int:
    projeto = Path(args.projeto).resolve()

    if args.verificar:
        achados = prototipo.verificar(projeto)
        for a in achados:
            print(f"regra {a['regra']}: {a['titulo']}")
            print(f"  {a['evidencia']}")
        altos = [a for a in achados if a['impacto'] == 'alto']
        print(f'{len(achados)} achado(s) · {len(altos)} de impacto alto')
        return 1 if achados else 0

    cs = changeset.abrir(args.changeset, args.titulo, args.origem,
                         args.alvo or [])
    problemas = changeset.validar(cs)
    for a in problemas:
        print(f"{a['id']}: {a['titulo']} — {a['evidencia']}")
    if problemas:
        print(f'{len(problemas)} problema(s) — o changeset não foi aberto.')
        return 1

    print(f"{cs['id']}: {cs['title']}")
    print(f"  origem: {cs['source']}")
    print(f"  affected: {', '.join(cs['affected'])}")

    achados = prototipo.verificar(projeto)
    fora = [a for a in achados if a['impacto'] == 'alto']
    if fora:
        print(f'  atenção: {len(fora)} violação(ões) de padrão já existentes '
              'no protótipo — corrija-as no changeset ou em outro')
        for a in fora:
            print(f"    regra {a['regra']}: {a['evidencia']}")

    if not args.apply:
        print('simulação — o changeset não foi gravado. '
              'Use --apply para abrir de fato.')
        return 0

    reg = leitura.Registro()
    destino = projeto / '.dk' / 'changesets'
    op = ops.Operacao(projeto, escopo=['.dk'], registro=reg)
    op.planejar(destino / f"{cs['id']}.json",
                json.dumps(cs, ensure_ascii=False, indent=2) + '\n')
    op.aplicar()
    print(f"aberto: .dk/changesets/{cs['id']}.json")
    return 0
```

E no `main()`:

```python
    pro = sub.add_parser('prototipar', help='changeset e padrão do protótipo')
    pro.add_argument('--projeto', required=True)
    pro.add_argument('--verificar', action='store_true',
                     help='só verifica o padrão do protótipo')
    pro.add_argument('--changeset')
    pro.add_argument('--titulo', default='')
    pro.add_argument('--origem', default='')
    pro.add_argument('--alvo', action='append',
                     help='caminho afetado; repetível. É o escopo da mudança')
    pro.add_argument('--apply', action='store_true')
    pro.set_defaults(func=cmd_prototipar)
```

Acrescente `changeset` e `prototipo` ao import de `core`.

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_prototipar_cli.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add bin/dk tests/validate_prototipar_cli.py
git commit -m "feat: dk prototipar com changeset e verificacao de padrao"
```

---

### Task 4: Porta, skills e agente da etapa `prototipar`

**Files:**
- Create: `dk/skills/dk-prototipar/SKILL.md`
- Create: `dk/skills/dk-prototipar-ajuste/SKILL.md`
- Create: `dk/skills/dk-prototipar-padrao/SKILL.md`
- Create: `dk/agents/dk-prototipar.md`

A `dk-prototipar-ajuste` é a skill que o time vai usar todo dia, e é onde a regra fica
escrita em português: **declare o alvo antes, mexa só nele, e se descobrir que precisa de
mais, abra outro changeset em vez de esticar este.**

- [ ] **Step 1 a 4:** criar os quatro arquivos no formato das etapas anteriores.

- [ ] **Step 5: Rodar a bateria e commitar**

---

### Task 5: E2E — o ajuste fora do escopo é recusado

**Files:**
- Test: `dk/tests/validate_ciclo_prototipar.py`

- [ ] **Step 1: Escrever o teste**

O teste monta um protótipo com dois componentes, abre um changeset declarando **um**, e
exige que a escrita no outro falhe e que o arquivo do outro permaneça byte a byte igual.
É a prova da dor nº 2.

- [ ] **Step 2: Acrescentar ao portão de release e commitar**

---

## Cobertura da spec

Este plano entrega a etapa `prototipar` e as regras 7 a 15 do validador do Kit, que o
plano 3 declarou pendentes.

## Depois deste plano

1. Entregáveis de comunicação: manual de uso, e-mail de entrega, apresentação, slide, guia
2. `modules/design-system/` — o resto do cruzamento DLS × Kit
3. Etapa `handoff`
4. Os demais módulos: git-workflow, liferay-migration, similar-analysis, lean-inception
5. Congelamento das duas bases antigas, com inspeção prévia dos sete clones
