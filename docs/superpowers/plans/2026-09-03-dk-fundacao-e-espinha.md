# DK — Fundação e Espinha E2E · Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o repositório `dk` com os invariantes executáveis e uma espinha vertical que vai do insumo bruto de reunião ao Documento de Requisitos formatado, provada por teste ponta a ponta que roda automaticamente.

**Architecture:** Repositório novo, autônomo, sem dependência do `seakit` nem do `sea-design-kit`. Núcleo determinístico em Python (`core/`) roda antes de qualquer LLM: escrita atômica, envelope de dry-run, registro de leitura obrigatória e validadores. Skills em Markdown ficam atrás de portões de etapa; agentes de etapa enumeram suas skills. Testes são scripts autônomos coletados por `verificar.py`, executados por hook de pre-push cuja ativação é verificada.

**Tech Stack:** Python 3.9+ (stdlib apenas), Markdown com front-matter YAML, JSON Schema, git hooks. Sem pytest, sem dependência externa obrigatória.

**Spec:** `docs/superpowers/specs/2026-09-03-dk-consolidacao-design.md`

## Global Constraints

- Piso de Python: **3.9**. Nenhuma API exclusiva de 3.10+ (`glob(root_dir=)`, `match`/`case`, `X | Y` fora de `from __future__ import annotations`). Isso fecha o CONF-001, que hoje está aberto no `PROJECT_MANIFEST.yaml` do Kit.
- `dependencies_required: []`. Toda dependência externa é opcional e degrada anunciada.
- Testes são scripts autônomos `tests/validate_*.py`, sem framework: acumulam em `errors = []`, imprimem cada erro e saem com código 1 se houver algum. É o padrão do Kit, e `verificar.py` os coleta por glob.
- Toda escrita em disco passa por `core.io.atomic_write` ou `core.io.atomic_json`. Nenhum `open(..., 'w')` direto em código de produção.
- Toda operação que escreve tem modo de simulação, e a simulação é o padrão.
- Nenhum arquivo do `seakit` é lido, referenciado ou alterado.
- Nenhum arquivo do `sea-design-kit` ou do `design-ai-community` é alterado. Porte é cópia com reescrita, na direção deles para o `dk`.
- O repositório do `dk` fica em `/Users/sea/SEA/plugins/dk`.
- Mensagens de commit em português, formato Conventional Commits, sem atribuição de autoria de IA.

---

## File Structure

| Arquivo | Responsabilidade |
|---|---|
| `.claude-plugin/plugin.json` | identidade e versão — **fonte única** |
| `verificar.py` | coletor de testes; substitui pipeline |
| `.githooks/pre-push` | roda `verificar.py` antes do push |
| `core/io.py` | escrita atômica |
| `core/ops.py` | envelope de dry-run e escopo declarado |
| `core/leitura.py` | registro de leitura da sessão |
| `core/registry.py` | leitura e escrita dos registros do projeto |
| `core/versao.py` | propaga a versão da fonte única |
| `docs/contrato-de-resposta.md` | contrato de resposta, referenciado por todas as skills |
| `agents/dk-levantar.md` | orquestrador da etapa, enumera suas skills |
| `skills/dk/SKILL.md` | porta geral, sem portão |
| `skills/dk-levantar-*/SKILL.md` | skills da etapa, com portão |
| `tests/validate_*.py` | um validador por invariante |
| `tests/fixtures/projeto-exemplo/` | projeto de fixture do teste E2E |

---

### Task 1: Esqueleto do repositório e versão em fonte única

**Files:**
- Create: `dk/.claude-plugin/plugin.json`
- Create: `dk/core/__init__.py`
- Create: `dk/core/versao.py`
- Create: `dk/verificar.py`
- Test: `dk/tests/validate_versao_unica.py`

**Interfaces:**
- Consumes: nada
- Produces: `core.versao.versao_canonica() -> str`, `core.versao.fontes() -> dict[str, str]` (caminho relativo → versão declarada); `RAIZ` como `Path` da raiz do repositório

- [ ] **Step 1: Criar o repositório e o esqueleto mínimo**

```bash
mkdir -p /Users/sea/SEA/plugins/dk/{core,tests,skills,agents,docs,.claude-plugin,.githooks}
cd /Users/sea/SEA/plugins/dk
git init
touch core/__init__.py
```

```json
{
  "name": "dk",
  "description": "Processo de design ponta a ponta: auditoria, levantamento, entendimento, entregáveis, protótipo e handoff.",
  "version": "0.1.0",
  "author": { "name": "SEA Tecnologia" },
  "license": "MIT"
}
```

Grave o JSON acima em `.claude-plugin/plugin.json`.

- [ ] **Step 2: Escrever o teste que falha**

Grave em `tests/validate_versao_unica.py`:

```python
#!/usr/bin/env python3
"""A versão é declarada em um lugar só. Toda outra ocorrência é derivada."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import versao  # noqa: E402

errors = []

canonica = versao.versao_canonica()
if not canonica:
    errors.append('versao_canonica() vazia')

for caminho, declarada in versao.fontes().items():
    if declarada != canonica:
        errors.append(f'{caminho} declara {declarada}, canônica é {canonica}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 3: Rodar o teste e confirmar que falha**

Run: `cd /Users/sea/SEA/plugins/dk && python3 tests/validate_versao_unica.py`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.versao'`

- [ ] **Step 4: Implementar `core/versao.py`**

```python
#!/usr/bin/env python3
"""A versão do pacote vive em `.claude-plugin/plugin.json` e em nenhum outro lugar.

Qualquer outro arquivo que precise da versão a recebe daqui, gerada. O Kit anterior
declarava a versão em quatro arquivos e dois já divergiam (achado DK-002)."""
from __future__ import annotations
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLUGIN = RAIZ / '.claude-plugin' / 'plugin.json'


def versao_canonica() -> str:
    return json.loads(PLUGIN.read_text(encoding='utf-8'))['version']


def fontes() -> dict:
    """Todo arquivo que declara versão, mapeado para o valor que ele declara.

    Um arquivo novo que passe a declarar versão entra aqui, ou o teste não o vê."""
    encontradas = {'.claude-plugin/plugin.json': versao_canonica()}
    marketplace = RAIZ / '.claude-plugin' / 'marketplace.json'
    if marketplace.exists():
        dados = json.loads(marketplace.read_text(encoding='utf-8'))
        for plugin in dados.get('plugins', []):
            encontradas['.claude-plugin/marketplace.json'] = plugin.get('version', '')
    return encontradas
```

- [ ] **Step 5: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_versao_unica.py`
Expected: PASS, saída vazia, código 0

- [ ] **Step 6: Criar o coletor de testes**

Grave em `verificar.py`:

```python
#!/usr/bin/env python3
"""Verificação do pacote, sem runner externo.

Roda todo `tests/validate_*.py` como processo próprio e agrega o resultado.
Um validador novo entra por glob — não há lista para esquecer de atualizar."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def main() -> int:
    falhas = []
    # `Path.glob` em vez de `glob.glob(root_dir=)`: root_dir só existe no 3.10,
    # e o piso do pacote é 3.9.
    for teste in sorted(str(p.relative_to(RAIZ))
                        for p in RAIZ.glob('tests/validate_*.py')):
        r = subprocess.run([sys.executable, teste], cwd=str(RAIZ),
                           capture_output=True, text=True)
        marca = 'ok  ' if r.returncode == 0 else 'FALHA'
        print(f'{marca} {teste}')
        if r.returncode != 0:
            falhas.append(teste)
            saida = (r.stdout + r.stderr).strip()
            if saida:
                print('      ' + saida.replace('\n', '\n      '))
    print()
    print(f'{len(falhas)} falha(s)' if falhas else 'tudo verde')
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 7: Rodar o coletor**

Run: `python3 verificar.py`
Expected: `ok   tests/validate_versao_unica.py` e `tudo verde`, código 0

- [ ] **Step 8: Commit**

```bash
git add .claude-plugin/plugin.json core/ tests/ verificar.py
git commit -m "feat: esqueleto do dk com versao em fonte unica"
```

---

### Task 2: Escrita atômica

**Files:**
- Create: `dk/core/io.py`
- Test: `dk/tests/validate_escrita_atomica.py`

**Interfaces:**
- Consumes: nada
- Produces: `core.io.atomic_write(path: Path, texto: str) -> None`, `core.io.atomic_json(path: Path, dados) -> None`

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_escrita_atomica.py`:

```python
#!/usr/bin/env python3
"""Escrita interrompida não corrompe o arquivo que já existia.

O modo `open(..., 'w')` trunca antes de escrever: se o processo morre no meio,
o arquivo fica pela metade. Dois scripts do Kit anterior ainda faziam isso
(achado DK-109)."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    alvo = Path(d) / 'sub' / 'arquivo.txt'

    io.atomic_write(alvo, 'primeiro')
    if alvo.read_text(encoding='utf-8') != 'primeiro':
        errors.append('atomic_write não gravou o conteúdo inicial')

    class Explode(str):
        def encode(self, *a, **k):
            raise RuntimeError('falha simulada no meio da escrita')

    try:
        io.atomic_write(alvo, Explode('segundo'))
    except RuntimeError:
        pass
    else:
        errors.append('a falha simulada não propagou')

    if alvo.read_text(encoding='utf-8') != 'primeiro':
        errors.append('o conteúdo anterior foi corrompido por escrita interrompida')

    sobras = [p.name for p in alvo.parent.iterdir() if p.name != 'arquivo.txt']
    if sobras:
        errors.append(f'arquivo temporário não removido: {sobras}')

    j = Path(d) / 'dados.json'
    io.atomic_json(j, {'a': 1, 'acento': 'ação'})
    if json.loads(j.read_text(encoding='utf-8')) != {'a': 1, 'acento': 'ação'}:
        errors.append('atomic_json não preservou o conteúdo')
    if 'ação' not in j.read_text(encoding='utf-8'):
        errors.append('atomic_json escapou caractere acentuado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python3 tests/validate_escrita_atomica.py`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.io'`

- [ ] **Step 3: Implementar `core/io.py`**

```python
#!/usr/bin/env python3
"""Escrita atômica: arquivo temporário no mesmo diretório, depois `os.replace`.

`os.replace` é atômico dentro do mesmo sistema de arquivos — por isso o temporário
nasce ao lado do alvo, e não em /tmp. Escrita em lugar trunca; esta não."""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write(path: Path, texto: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(texto.encode('utf-8'))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_json(path: Path, dados: Any) -> None:
    atomic_write(Path(path),
                 json.dumps(dados, ensure_ascii=False, indent=2) + '\n')
```

- [ ] **Step 4: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_escrita_atomica.py`
Expected: PASS, código 0

- [ ] **Step 5: Commit**

```bash
git add core/io.py tests/validate_escrita_atomica.py
git commit -m "feat: escrita atomica com temp e os.replace"
```

---

### Task 3: Envelope de dry-run e escopo declarado

**Files:**
- Create: `dk/core/ops.py`
- Test: `dk/tests/validate_dry_run_e_escopo.py`

**Interfaces:**
- Consumes: `core.io.atomic_write`
- Produces: `core.ops.Operacao(alvo: Path, escopo: list)`, com métodos `planejar(path, texto) -> dict` e `aplicar() -> list`; `core.ops.ForaDoEscopo` (exceção)

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_dry_run_e_escopo.py`:

```python
#!/usr/bin/env python3
"""Toda escrita simula antes de aplicar, e só toca o que foi declarado.

Cobre a dor relatada no protótipo: pede-se um ajuste e a ferramenta altera
arquivo que ninguém pediu, quebrando o que já estava pronto."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, ops  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    io.atomic_write(raiz / 'dentro.txt', 'antes')
    io.atomic_write(raiz / 'fora.txt', 'intocado')

    op = ops.Operacao(raiz, escopo=['dentro.txt'])
    plano = op.planejar(raiz / 'dentro.txt', 'depois')

    if plano['acao'] != 'modifica':
        errors.append(f"acao esperada 'modifica', veio {plano['acao']!r}")
    if 'antes' not in plano['diff'] or 'depois' not in plano['diff']:
        errors.append('o plano não mostra o diff do que muda')
    if (raiz / 'dentro.txt').read_text(encoding='utf-8') != 'antes':
        errors.append('planejar() escreveu em disco — simulação deve ser inerte')

    escritos = op.aplicar()
    if (raiz / 'dentro.txt').read_text(encoding='utf-8') != 'depois':
        errors.append('aplicar() não gravou')
    if escritos != [raiz / 'dentro.txt']:
        errors.append(f'aplicar() devolveu {escritos}')

    op2 = ops.Operacao(raiz, escopo=['dentro.txt'])
    try:
        op2.planejar(raiz / 'fora.txt', 'invadido')
    except ops.ForaDoEscopo:
        pass
    else:
        errors.append('escrita fora do escopo declarado não foi recusada')

    if (raiz / 'fora.txt').read_text(encoding='utf-8') != 'intocado':
        errors.append('arquivo fora do escopo foi alterado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python3 tests/validate_dry_run_e_escopo.py`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.ops'`

- [ ] **Step 3: Implementar `core/ops.py`**

```python
#!/usr/bin/env python3
"""Envelope de escrita: declara o escopo, simula, e só então aplica.

Duas garantias. A simulação é inerte — `planejar` nunca toca o disco. E o escopo
é fechado — caminho fora do que foi declarado levanta `ForaDoEscopo` em vez de
ser escrito 'só desta vez'."""
from __future__ import annotations
import difflib
from pathlib import Path
from typing import List

from core import io


class ForaDoEscopo(Exception):
    """Levantada quando a operação tenta escrever fora do alvo declarado."""


class Operacao:
    def __init__(self, alvo: Path, escopo: List[str]) -> None:
        self.alvo = Path(alvo).resolve()
        self.escopo = list(escopo)
        self._pendentes = []  # type: List[tuple]

    def _dentro(self, path: Path) -> bool:
        try:
            rel = Path(path).resolve().relative_to(self.alvo)
        except ValueError:
            return False
        return any(rel == Path(p) or str(rel).startswith(str(Path(p)) + '/')
                   for p in self.escopo)

    def planejar(self, path: Path, texto: str) -> dict:
        path = Path(path)
        if not self._dentro(path):
            raise ForaDoEscopo(
                f'{path} está fora do escopo declarado {self.escopo}')
        anterior = path.read_text(encoding='utf-8') if path.exists() else ''
        diff = '\n'.join(difflib.unified_diff(
            anterior.splitlines(), texto.splitlines(),
            fromfile=f'{path.name} (atual)', tofile=f'{path.name} (proposto)',
            lineterm=''))
        self._pendentes.append((path, texto))
        return {
            'caminho': str(path),
            'acao': 'modifica' if path.exists() else 'cria',
            'diff': diff,
        }

    def aplicar(self) -> List[Path]:
        escritos = []
        for path, texto in self._pendentes:
            io.atomic_write(path, texto)
            escritos.append(path)
        self._pendentes = []
        return escritos
```

- [ ] **Step 4: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_dry_run_e_escopo.py`
Expected: PASS, código 0

- [ ] **Step 5: Commit**

```bash
git add core/ops.py tests/validate_dry_run_e_escopo.py
git commit -m "feat: envelope de dry-run com escopo declarado"
```

---

### Task 4: Registro de leitura — ler antes de escrever

**Files:**
- Create: `dk/core/leitura.py`
- Modify: `dk/core/ops.py` (integrar o registro ao `planejar`)
- Test: `dk/tests/validate_ler_antes_de_escrever.py`

**Interfaces:**
- Consumes: `core.ops.Operacao`
- Produces: `core.leitura.Registro()` com `ler(path) -> str`, `foi_lido(path) -> bool`; `Operacao(alvo, escopo, registro=None, fontes=None)` passa a recusar escrita cujas fontes não foram lidas, com `FonteNaoLida`

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_ler_antes_de_escrever.py`:

```python
#!/usr/bin/env python3
"""Nenhum artefato é gravado sem que sua fonte tenha sido lida na sessão.

É o invariante que fecha a dor nº 1: requisitos que já existem no projeto sendo
ignorados e sobrescritos, em vez de atualizados."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, leitura, ops  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    io.atomic_write(raiz / 'fonte.md', 'requisito existente')
    io.atomic_write(raiz / 'saida.md', 'versão antiga')

    reg = leitura.Registro()
    if reg.foi_lido(raiz / 'fonte.md'):
        errors.append('registro nasceu achando que já leu')

    op = ops.Operacao(raiz, escopo=['saida.md'], registro=reg,
                      fontes=[raiz / 'fonte.md'])
    try:
        op.planejar(raiz / 'saida.md', 'nova versão')
    except ops.FonteNaoLida:
        pass
    else:
        errors.append('escrita sem leitura prévia da fonte não foi recusada')

    conteudo = reg.ler(raiz / 'fonte.md')
    if conteudo != 'requisito existente':
        errors.append('ler() não devolveu o conteúdo do arquivo')
    if not reg.foi_lido(raiz / 'fonte.md'):
        errors.append('ler() não registrou a leitura')

    op2 = ops.Operacao(raiz, escopo=['saida.md'], registro=reg,
                       fontes=[raiz / 'fonte.md'])
    plano = op2.planejar(raiz / 'saida.md', 'nova versão')
    if plano['acao'] != 'modifica':
        errors.append('após a leitura, o plano deveria ser aceito')
    op2.aplicar()
    if (raiz / 'saida.md').read_text(encoding='utf-8') != 'nova versão':
        errors.append('aplicar() não gravou depois da leitura')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python3 tests/validate_ler_antes_de_escrever.py`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.leitura'`

- [ ] **Step 3: Implementar `core/leitura.py`**

```python
#!/usr/bin/env python3
"""Registro do que foi lido na sessão.

Existe para uma coisa só: permitir que a camada de escrita recuse gravar um
artefato cuja fonte ninguém abriu. Escrever sem ler é como o furo aparece —
o requisito que já estava no projeto é substituído em vez de atualizado."""
from __future__ import annotations
from pathlib import Path
from typing import Dict


class Registro:
    def __init__(self) -> None:
        self._lidos = {}  # type: Dict[str, str]

    def ler(self, path: Path) -> str:
        path = Path(path)
        conteudo = path.read_text(encoding='utf-8')
        self._lidos[str(path.resolve())] = conteudo
        return conteudo

    def foi_lido(self, path: Path) -> bool:
        return str(Path(path).resolve()) in self._lidos

    def conteudo(self, path: Path) -> str:
        return self._lidos[str(Path(path).resolve())]
```

- [ ] **Step 4: Integrar ao `core/ops.py`**

Substitua a classe `Operacao` em `core/ops.py` por esta versão, e acrescente a exceção:

```python
class FonteNaoLida(Exception):
    """Levantada quando se tenta escrever sem ler a fonte declarada."""


class Operacao:
    def __init__(self, alvo, escopo, registro=None, fontes=None) -> None:
        self.alvo = Path(alvo).resolve()
        self.escopo = list(escopo)
        self.registro = registro
        self.fontes = [Path(f) for f in (fontes or [])]
        self._pendentes = []  # type: List[tuple]

    def _dentro(self, path: Path) -> bool:
        try:
            rel = Path(path).resolve().relative_to(self.alvo)
        except ValueError:
            return False
        return any(rel == Path(p) or str(rel).startswith(str(Path(p)) + '/')
                   for p in self.escopo)

    def _exigir_leitura(self) -> None:
        if self.registro is None:
            return
        faltando = [str(f) for f in self.fontes if not self.registro.foi_lido(f)]
        if faltando:
            raise FonteNaoLida(
                'fonte declarada não foi lida nesta sessão: ' + ', '.join(faltando))

    def planejar(self, path: Path, texto: str) -> dict:
        path = Path(path)
        if not self._dentro(path):
            raise ForaDoEscopo(
                f'{path} está fora do escopo declarado {self.escopo}')
        self._exigir_leitura()
        anterior = path.read_text(encoding='utf-8') if path.exists() else ''
        diff = '\n'.join(difflib.unified_diff(
            anterior.splitlines(), texto.splitlines(),
            fromfile=f'{path.name} (atual)', tofile=f'{path.name} (proposto)',
            lineterm=''))
        self._pendentes.append((path, texto))
        return {
            'caminho': str(path),
            'acao': 'modifica' if path.exists() else 'cria',
            'diff': diff,
        }

    def aplicar(self) -> List[Path]:
        escritos = []
        for path, texto in self._pendentes:
            io.atomic_write(path, texto)
            escritos.append(path)
        self._pendentes = []
        return escritos
```

- [ ] **Step 5: Rodar os dois testes de operação**

Run: `python3 tests/validate_dry_run_e_escopo.py && python3 tests/validate_ler_antes_de_escrever.py`
Expected: ambos PASS, código 0

- [ ] **Step 6: Commit**

```bash
git add core/leitura.py core/ops.py tests/validate_ler_antes_de_escrever.py
git commit -m "feat: exige leitura da fonte antes de gravar artefato"
```

---

### Task 5: Hook de pre-push com ativação verificada

**Files:**
- Create: `dk/.githooks/pre-push`
- Create: `dk/bin/dk-instalar-hooks`
- Test: `dk/tests/validate_hooks_ativos.py`

**Interfaces:**
- Consumes: `verificar.py`
- Produces: hook executável em `.githooks/pre-push`; `bin/dk-instalar-hooks` que configura `core.hooksPath`

Contexto: no Kit anterior o hook existia e exigia `git config core.hooksPath .githooks` manual por clone. Em nenhum dos três clones verificados isso tinha sido feito, então a validação inteira estava desligada (achado DK-107). Aqui a ativação é verificada por teste.

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_hooks_ativos.py`:

```python
#!/usr/bin/env python3
"""O hook existe, é executável, e o clone está configurado para usá-lo.

Hook que depende de um `git config` manual que ninguém roda é hook desligado."""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []

hook = RAIZ / '.githooks' / 'pre-push'
if not hook.exists():
    errors.append('.githooks/pre-push não existe')
elif not os.access(hook, os.X_OK):
    errors.append('.githooks/pre-push não é executável')

instalador = RAIZ / 'bin' / 'dk-instalar-hooks'
if not instalador.exists():
    errors.append('bin/dk-instalar-hooks não existe')

r = subprocess.run(['git', 'config', 'core.hooksPath'],
                   cwd=str(RAIZ), capture_output=True, text=True)
configurado = r.stdout.strip()
if configurado != '.githooks':
    errors.append(
        f'core.hooksPath é {configurado!r}, esperado ".githooks" — '
        'rode bin/dk-instalar-hooks')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python3 tests/validate_hooks_ativos.py`
Expected: FAIL com as três mensagens — hook ausente, instalador ausente, `core.hooksPath` vazio

- [ ] **Step 3: Criar o hook**

Grave em `.githooks/pre-push`:

```bash
#!/usr/bin/env bash
# Verificação antes do push. O pacote não tem runner externo: esta é a validação.
#
# Ativação: bin/dk-instalar-hooks  (e o teste validate_hooks_ativos.py cobra)
# Pular num push específico: git push --no-verify
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Verificando o pacote antes do push..."
if ! python3 "$RAIZ/verificar.py"; then
  echo
  echo "Push abortado: a verificação falhou. Corrija, ou use --no-verify se for deliberado."
  exit 1
fi
```

- [ ] **Step 4: Criar o instalador**

Grave em `bin/dk-instalar-hooks`:

```bash
#!/usr/bin/env bash
# Aponta o Git deste clone para .githooks. Idempotente.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
git -C "$RAIZ" config core.hooksPath .githooks
chmod +x "$RAIZ/.githooks/pre-push"
echo "core.hooksPath = $(git -C "$RAIZ" config core.hooksPath)"
```

- [ ] **Step 5: Instalar e rodar o teste**

Run: `chmod +x bin/dk-instalar-hooks .githooks/pre-push && bin/dk-instalar-hooks && python3 tests/validate_hooks_ativos.py`
Expected: `core.hooksPath = .githooks`, depois PASS com código 0

- [ ] **Step 6: Commit**

```bash
git add .githooks/pre-push bin/dk-instalar-hooks tests/validate_hooks_ativos.py
git commit -m "feat: pre-push com ativacao verificada por teste"
```

---

### Task 6: Contrato de resposta único

**Files:**
- Create: `dk/docs/contrato-de-resposta.md`
- Test: `dk/tests/validate_contrato_de_resposta.py`

**Interfaces:**
- Consumes: nada
- Produces: `docs/contrato-de-resposta.md` como texto canônico; regra de que nenhuma `SKILL.md` copia o corpo dele, apenas o referencia, e declara `forma-da-saida:` no front-matter

Contexto: no Kit anterior a seção "Resposta final da Skill" estava replicada 53, 46 e 37 vezes, e 48% do corpo das skills era texto duplicado (achado DK-503). É a origem medida da prolixidade.

- [ ] **Step 1: Escrever o contrato**

Grave em `docs/contrato-de-resposta.md`:

```markdown
# Contrato de resposta

Toda skill do `dk` responde segundo este contrato. Nenhuma skill copia este texto —
todas o referenciam, e declaram no front-matter a forma da sua saída:

```yaml
forma-da-saida: frase | tabela | documento
```

## frase

Uma a três frases. Nenhum preâmbulo, nenhuma recapitulação do pedido, nenhuma
lista de passos executados. Se a resposta cabe numa frase, ela é uma frase.

## tabela

Uma tabela com as colunas que o caso pede, precedida de no máximo uma frase de
contexto. Sem repetir em prosa o que a tabela já diz.

## documento

O artefato gravado, mais uma frase dizendo o caminho e o que mudou nele. O conteúdo
do documento não é repetido na resposta.

## Em qualquer forma

- Não descreva o que você vai fazer antes de fazer.
- Não anuncie chamada de ferramenta.
- Números e caminhos exatos; nada aproximado sem dizer que é estimativa.
- Divergência encontrada é reportada, não silenciada.
```

- [ ] **Step 2: Escrever o teste que falha**

Grave em `tests/validate_contrato_de_resposta.py`:

```python
#!/usr/bin/env python3
"""O contrato de resposta é referenciado, nunca copiado.

Toda SKILL.md declara a forma da saída e aponta para o contrato. Nenhuma repete
o corpo dele — foi assim que o Kit anterior acumulou 48% de texto duplicado."""
from __future__ import annotations
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CONTRATO = RAIZ / 'docs' / 'contrato-de-resposta.md'
FORMAS = {'frase', 'tabela', 'documento'}

errors = []

if not CONTRATO.exists():
    errors.append('docs/contrato-de-resposta.md não existe')
    for e in errors:
        print(e)
    sys.exit(1)

corpo = CONTRATO.read_text(encoding='utf-8')
marcadores = [linha.strip() for linha in corpo.splitlines()
              if linha.startswith('## ') and linha.strip() != '## Em qualquer forma']

for skill in sorted(RAIZ.glob('skills/*/SKILL.md')):
    texto = skill.read_text(encoding='utf-8')
    fm = texto.split('---', 2)[1] if texto.startswith('---\n') else ''

    m = re.search(r'^forma-da-saida:\s*(\S+)', fm, re.M)
    if not m:
        errors.append(f'{skill.parent.name}: falta forma-da-saida no front-matter')
    elif m.group(1) not in FORMAS:
        errors.append(f'{skill.parent.name}: forma-da-saida {m.group(1)!r} inválida')

    if 'contrato-de-resposta' not in texto:
        errors.append(f'{skill.parent.name}: não referencia o contrato de resposta')

    for marcador in marcadores:
        if marcador in texto:
            errors.append(
                f'{skill.parent.name}: copia a seção {marcador!r} do contrato '
                'em vez de referenciá-la')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 3: Rodar o teste**

Run: `python3 tests/validate_contrato_de_resposta.py`
Expected: PASS com código 0 — ainda não há skills, e o contrato existe. O teste passa a ter efeito na Task 8, quando a primeira skill nascer.

- [ ] **Step 4: Commit**

```bash
git add docs/contrato-de-resposta.md tests/validate_contrato_de_resposta.py
git commit -m "feat: contrato de resposta unico, referenciado nunca copiado"
```

---

### Task 7: Portão de etapa e orçamento de catálogo

**Files:**
- Create: `dk/core/skills.py`
- Test: `dk/tests/validate_portao_e_orcamento.py`

**Interfaces:**
- Consumes: nada
- Produces: `core.skills.frontmatter(path) -> dict`, `core.skills.inventario() -> list[dict]` (cada item com `nome`, `description`, `etapa`, `portao`), `core.skills.PORTAS` (conjunto dos nomes sem portão), `core.skills.ORCAMENTO_BYTES = 2048`

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_portao_e_orcamento.py`:

```python
#!/usr/bin/env python3
"""Só as portas ficam sem portão, e o catálogo fixo cabe no orçamento.

O Kit anterior carregava 49.678 B de description em toda sessão, ~12.420 tokens,
porque 191 das 275 skills não tinham portão de etapa (achados DK-004 e DK-502)."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import skills  # noqa: E402

errors = []
inventario = skills.inventario()

for item in inventario:
    nome = item['nome']
    if nome in skills.PORTAS:
        if item['portao']:
            errors.append(f'{nome}: é porta, não deveria ter portão')
    else:
        if not item['portao']:
            errors.append(
                f'{nome}: sem portão de etapa — toda skill que não é porta '
                'declara "Use quando a etapa <X> do DK estiver ativa"')
        if not item['etapa']:
            errors.append(f'{nome}: portão sem etapa reconhecível')

sem_portao = [i for i in inventario if not i['portao']]
custo = sum(len(i['description'].encode('utf-8')) for i in sem_portao)
if custo > skills.ORCAMENTO_BYTES:
    errors.append(
        f'catálogo fixo em {custo} B, orçamento é {skills.ORCAMENTO_BYTES} B '
        f'({len(sem_portao)} skills sem portão)')

print(f'catálogo fixo: {custo} B em {len(sem_portao)} skills sem portão '
      f'(orçamento {skills.ORCAMENTO_BYTES} B)')
for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python3 tests/validate_portao_e_orcamento.py`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.skills'`

- [ ] **Step 3: Implementar `core/skills.py`**

```python
#!/usr/bin/env python3
"""Leitura do inventário de skills e das regras de portão.

Portão é a frase na `description` que amarra a skill a uma etapa. Skill com portão
não compete no catálogo genérico: ela só é considerada dentro da sua etapa. Apenas
as portas — uma por etapa, mais a porta geral — ficam sem portão."""
from __future__ import annotations
import re
from pathlib import Path
from typing import List

RAIZ = Path(__file__).resolve().parents[1]

ETAPAS = ('audit', 'levantar', 'entender', 'entregar', 'prototipar', 'handoff')
PORTAS = {'dk'} | {f'dk-{e}' for e in ETAPAS}
ORCAMENTO_BYTES = 2048

_PORTAO = re.compile(
    r'use quando a etapa\s+([a-zà-ú-]+)\s+do dk estiver ativa', re.I)


def frontmatter(path: Path) -> dict:
    texto = Path(path).read_text(encoding='utf-8')
    if not texto.startswith('---\n'):
        return {}
    bruto = texto.split('---', 2)[1]
    campos = {}
    for m in re.finditer(r'^([a-z][a-z-]*):\s*(.*?)(?=\n[a-z][a-z-]*:|\Z)',
                         bruto, re.S | re.M):
        campos[m.group(1)] = m.group(2).strip().strip('"\'')
    return campos


def inventario() -> List[dict]:
    itens = []
    for skill in sorted(RAIZ.glob('skills/*/SKILL.md')):
        campos = frontmatter(skill)
        descricao = campos.get('description', '')
        m = _PORTAO.search(descricao)
        etapa = m.group(1).lower() if m else ''
        itens.append({
            'nome': skill.parent.name,
            'description': descricao,
            'portao': bool(m),
            'etapa': etapa if etapa in ETAPAS else '',
        })
    return itens
```

- [ ] **Step 4: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_portao_e_orcamento.py`
Expected: PASS, imprime `catálogo fixo: 0 B em 0 skills sem portão (orçamento 2048 B)`

- [ ] **Step 5: Commit**

```bash
git add core/skills.py tests/validate_portao_e_orcamento.py
git commit -m "feat: portao de etapa e orcamento de catalogo verificado"
```

---

### Task 8: Enumeração — toda skill alcançável pelo seu agente

**Files:**
- Create: `dk/agents/dk-levantar.md`
- Create: `dk/skills/dk/SKILL.md`
- Create: `dk/skills/dk-levantar/SKILL.md`
- Test: `dk/tests/validate_enumeracao.py`

**Interfaces:**
- Consumes: `core.skills.inventario`, `core.skills.ETAPAS`
- Produces: convenção de que `agents/dk-<etapa>.md` contém uma lista `## Skills desta etapa` com um item por skill da etapa

Contexto: seis dos oito orquestradores do Kit nomeavam uma única skill — o de Git nomeava 1 das 37 (achado DK-506). Era por isso que as skills precisavam ficar no catálogo: sem enumeração, o portão as tornaria inalcançáveis.

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_enumeracao.py`:

```python
#!/usr/bin/env python3
"""Toda skill com portão é nomeada pelo agente da sua etapa.

Portão sem enumeração apaga capacidade: a skill deixa o catálogo e ninguém
consegue chegar nela."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import skills  # noqa: E402

errors = []
inventario = skills.inventario()
por_etapa = {}
for item in inventario:
    if item['etapa']:
        por_etapa.setdefault(item['etapa'], []).append(item['nome'])

for etapa, nomes in sorted(por_etapa.items()):
    agente = RAIZ / 'agents' / f'dk-{etapa}.md'
    if not agente.exists():
        errors.append(f'etapa {etapa}: falta agents/dk-{etapa}.md')
        continue
    texto = agente.read_text(encoding='utf-8')
    if '## Skills desta etapa' not in texto:
        errors.append(f'agents/dk-{etapa}.md: falta a seção "## Skills desta etapa"')
    for nome in nomes:
        if nome not in texto:
            errors.append(f'agents/dk-{etapa}.md não enumera {nome}')

for porta in sorted(skills.PORTAS):
    if porta == 'dk':
        continue
    etapa = porta[len('dk-'):]
    if (RAIZ / 'skills' / porta / 'SKILL.md').exists():
        if not (RAIZ / 'agents' / f'dk-{etapa}.md').exists():
            errors.append(f'porta {porta} existe sem agents/dk-{etapa}.md')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste e confirmar que passa vazio**

Run: `python3 tests/validate_enumeracao.py`
Expected: PASS, código 0 — ainda não há skills. O passo seguinte cria a primeira e o teste passa a ter conteúdo.

- [ ] **Step 3: Criar a porta geral**

Grave em `skills/dk/SKILL.md`:

```markdown
---
name: dk
description: Porta de entrada do DK. Use quando alguém disser dk, design kit, ou pedir trabalho de projeto de design sem citar apelido nenhum - auditar o projeto, levantar requisitos, entender a demanda, gerar entregável, mexer no protótipo ou preparar o handoff. Lê o estado do projeto, escolhe a etapa e despacha para o agente dela. Não use para executar o trabalho da etapa: isso é do agente que ela aciona.
argument-hint: "[o pedido em linguagem natural]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: frase
---

# dk — porta de entrada

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Leia o estado do projeto: `registry/` e `projeto.yml`, se existirem.
2. Se não existirem, a etapa é `audit`.
3. Case o pedido com a etapa:

   | Pedido menciona | Etapa |
   |---|---|
   | auditar, mapear, entender o repositório, conformidade | `audit` |
   | reunião, ata, transcrição, regra de negócio, requisito | `levantar` |
   | lacuna, cobertura, léxico, dúvida, premissa | `entender` |
   | documento, PDF, manual, e-mail, apresentação, slide | `entregar` |
   | protótipo, tela, componente, token | `prototipar` |
   | handoff, passagem, desenvolvimento | `handoff` |

4. Despache para `agents/dk-<etapa>.md`. Não execute o trabalho da etapa aqui.

## Resposta

Uma frase: qual etapa foi escolhida e por quê.
```

- [ ] **Step 4: Criar a porta e o agente da etapa `levantar`**

Grave em `skills/dk-levantar/SKILL.md`:

```markdown
---
name: dk-levantar
description: Porta da etapa de levantamento do DK. Use quando o trabalho for transformar insumo de reunião em ata, regras de negócio e requisitos rastreáveis. Ela lê o que já existe no projeto antes de propor qualquer escrita, e despacha para as skills da etapa.
argument-hint: "[caminho do insumo ou o pedido]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: frase
---

# dk-levantar — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Leia `registry/requisitos.json` e `registry/regras.json` se existirem. Sempre,
   antes de qualquer proposta de escrita.
2. Despache para `agents/dk-levantar.md`, que enumera as skills da etapa.

## Resposta

Uma frase: o que já existia no projeto e qual skill da etapa foi acionada.
```

Grave em `agents/dk-levantar.md`:

```markdown
---
name: dk-levantar
description: Orquestrador da etapa de levantamento do DK — insumo de reunião até requisitos rastreáveis.
---

# Etapa: levantar

Conduz o caminho `insumo bruto → ata → regras de negócio → requisitos`.

## Invariantes da etapa

- Nenhuma escrita antes de ler `registry/requisitos.json` e `registry/regras.json`.
- Requisito que já existe é **atualizado**, nunca duplicado ao lado.
- Toda escrita simula antes de aplicar.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-levantar-ata` | há insumo bruto de reunião a estruturar |
| `dk-levantar-regras` | há ata e faltam as regras de negócio |
| `dk-levantar-requisitos` | há regras e faltam requisitos, ou requisitos a atualizar |

## Procedimento

1. Determine em que ponto do caminho o projeto está, pelo que existe em `registry/`.
2. Acione a skill correspondente.
3. Ao fim, informe o que mudou no registro, em uma frase.
```

- [ ] **Step 5: Rodar os três validadores afetados**

Run: `python3 tests/validate_enumeracao.py && python3 tests/validate_portao_e_orcamento.py && python3 tests/validate_contrato_de_resposta.py`
Expected: os três PASS. O de orçamento imprime o custo das duas portas, bem abaixo de 2048 B.

- [ ] **Step 6: Commit**

```bash
git add skills/dk skills/dk-levantar agents/dk-levantar.md tests/validate_enumeracao.py
git commit -m "feat: porta geral, porta de levantamento e regra de enumeracao"
```

---

### Task 9: Registro do projeto

**Files:**
- Create: `dk/core/registry.py`
- Test: `dk/tests/validate_registry.py`

**Interfaces:**
- Consumes: `core.io.atomic_json`, `core.leitura.Registro`
- Produces: `core.registry.carregar(raiz, nome) -> list[dict]`, `core.registry.upsert(itens, novo, chave='id') -> tuple[list, str]` devolvendo a lista e `'criado'` ou `'atualizado'`, `core.registry.gravar(raiz, nome, itens) -> None`

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_registry.py`:

```python
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
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python3 tests/validate_registry.py`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.registry'`

- [ ] **Step 3: Implementar `core/registry.py`**

```python
#!/usr/bin/env python3
"""Registros do projeto: requisitos, regras, atas, decisões, pendências.

`upsert` é o coração: item com id que já existe é fundido, não anexado. O Kit
anterior gravava e não relia, e por isso o mesmo requisito voltava duplicado a
cada levantamento (achado DK-104)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Tuple

from core import io


def _caminho(raiz: Path, nome: str) -> Path:
    return Path(raiz) / 'registry' / f'{nome}.json'


def carregar(raiz: Path, nome: str) -> List[dict]:
    path = _caminho(raiz, nome)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding='utf-8'))


def gravar(raiz: Path, nome: str, itens: List[dict]) -> None:
    io.atomic_json(_caminho(raiz, nome), itens)


def upsert(itens: List[dict], novo: dict, chave: str = 'id') -> Tuple[List[dict], str]:
    """Funde `novo` na lista. Campo ausente em `novo` preserva o valor anterior."""
    saida = [dict(i) for i in itens]
    for i, existente in enumerate(saida):
        if existente.get(chave) == novo.get(chave):
            fundido = dict(existente)
            fundido.update(novo)
            saida[i] = fundido
            return saida, 'atualizado'
    saida.append(dict(novo))
    return saida, 'criado'
```

- [ ] **Step 4: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_registry.py`
Expected: PASS, código 0

- [ ] **Step 5: Commit**

```bash
git add core/registry.py tests/validate_registry.py
git commit -m "feat: registro do projeto com upsert que atualiza em vez de duplicar"
```

---

### Task 10: Ferramenta da espinha — `bin/dk levantar`

**Files:**
- Create: `dk/core/espinha.py`
- Create: `dk/bin/dk`
- Test: `dk/tests/validate_espinha_unidades.py`

**Interfaces:**
- Consumes: `core.registry`, `core.ops`, `core.leitura`, `core.io`
- Produces: `core.espinha.ata(texto_bruto) -> dict`, `core.espinha.regras(ata) -> list[dict]`, `core.espinha.requisitos(regras) -> list[dict]`, `core.espinha.cobertura(requisitos, regras) -> dict`

Nota de escopo: estas funções fazem a parte **determinística** — estrutura, identificação e reconciliação. A redação em linguagem natural fica com a skill, que chama estas funções. É a divisão que a spec pede: código determinístico onde não há raciocínio.

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_espinha_unidades.py`:

```python
#!/usr/bin/env python3
"""As unidades determinísticas da espinha, isoladas."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import espinha  # noqa: E402

errors = []

BRUTO = """Reunião 14/08 — Convênios
Fulana (gestora): o convênio não expira sozinho, quem tira do ar é o gestor.
Beltrano: e quando o prazo vence?
Fulana: fica vencido na lista, mas continua no ar até alguém revogar.
"""

a = espinha.ata(BRUTO)
if not a.get('data'):
    errors.append('ata sem data extraída')
if not a.get('participantes'):
    errors.append('ata sem participantes extraídos')
if 'Fulana' not in a.get('participantes', []):
    errors.append(f"participantes não incluem Fulana: {a.get('participantes')}")
if not a.get('falas'):
    errors.append('ata sem falas')

rs = espinha.regras(a)
if not rs:
    errors.append('nenhuma regra candidata extraída da ata')
for r in rs:
    if not r.get('id', '').startswith('RN-'):
        errors.append(f'regra sem id no padrão RN-: {r.get("id")!r}')
    if not r.get('citacao'):
        errors.append(f'{r.get("id")}: regra sem citação de origem')

reqs = espinha.requisitos(rs)
for q in reqs:
    if not q.get('id', '').startswith('REQ-'):
        errors.append(f'requisito sem id no padrão REQ-: {q.get("id")!r}')
    if not q.get('deriva_de'):
        errors.append(f'{q.get("id")}: requisito sem vínculo com a regra de origem')

cob = espinha.cobertura(reqs, rs)
if cob['regras_sem_requisito']:
    errors.append(f"regras sem requisito: {cob['regras_sem_requisito']}")
if cob['total_regras'] != len(rs):
    errors.append('cobertura contou regras errado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python3 tests/validate_espinha_unidades.py`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.espinha'`

- [ ] **Step 3: Implementar `core/espinha.py`**

```python
#!/usr/bin/env python3
"""Parte determinística da espinha: estrutura, identifica e reconcilia.

O que exige raciocínio — redigir a regra em linguagem de negócio, julgar se duas
regras são a mesma — fica com a skill. O que é forma, extração e vínculo fica aqui,
onde é testável e barato."""
from __future__ import annotations
import re
from typing import Dict, List

_DATA = re.compile(r'\b(\d{2})/(\d{2})(?:/(\d{2,4}))?\b')
_FALA = re.compile(r'^([A-ZÀ-Ú][\wÀ-ú.\- ]{1,40}?)\s*(?:\(([^)]*)\))?\s*:\s*(.+)$')


def ata(texto_bruto: str) -> Dict:
    """Estrutura o insumo bruto: data, participantes e falas atribuídas."""
    linhas = [l.strip() for l in texto_bruto.splitlines() if l.strip()]
    data = ''
    m = _DATA.search(texto_bruto)
    if m:
        data = '/'.join(p for p in m.groups() if p)

    falas = []
    participantes = []
    for linha in linhas:
        f = _FALA.match(linha)
        if not f:
            continue
        nome = f.group(1).strip()
        if nome not in participantes:
            participantes.append(nome)
        falas.append({'quem': nome, 'papel': (f.group(2) or '').strip(),
                      'fala': f.group(3).strip()})

    titulo = linhas[0] if linhas else ''
    return {'titulo': titulo, 'data': data,
            'participantes': participantes, 'falas': falas}


_MARCA_REGRA = re.compile(
    r'\b(não|nao|sempre|nunca|só|so|apenas|quem|quando|deve|precisa|fica|continua)\b',
    re.I)


def regras(ata_estruturada: Dict) -> List[Dict]:
    """Candidatas a regra de negócio, cada uma com a citação que a originou.

    Candidata, não regra: quem decide se vira regra é gente. O que o código
    garante é que nenhuma nasce sem procedência."""
    saida = []
    for i, fala in enumerate(ata_estruturada.get('falas', []), start=1):
        if not _MARCA_REGRA.search(fala['fala']):
            continue
        saida.append({
            'id': f'RN-{len(saida) + 1:03d}',
            'enunciado': fala['fala'],
            'citacao': fala['fala'],
            'fonte': f"{ata_estruturada.get('titulo', '')} — {fala['quem']}",
            'autoridade': 'cliente' if 'gestor' in fala.get('papel', '').lower()
                          else 'equipe',
        })
    return saida


def requisitos(lista_regras: List[Dict]) -> List[Dict]:
    """Um requisito por regra, vinculado à regra que o originou."""
    return [{
        'id': f'REQ-{i:03d}',
        'titulo': r['enunciado'],
        'deriva_de': r['id'],
        'fonte': r.get('fonte', ''),
    } for i, r in enumerate(lista_regras, start=1)]


def cobertura(lista_requisitos: List[Dict], lista_regras: List[Dict]) -> Dict:
    """Toda regra precisa de pelo menos um requisito. O que faltar é furo."""
    cobertas = {q.get('deriva_de') for q in lista_requisitos}
    faltando = [r['id'] for r in lista_regras if r['id'] not in cobertas]
    return {
        'total_regras': len(lista_regras),
        'total_requisitos': len(lista_requisitos),
        'regras_sem_requisito': faltando,
    }
```

- [ ] **Step 4: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_espinha_unidades.py`
Expected: PASS, código 0

- [ ] **Step 5: Criar a CLI**

Grave em `bin/dk`:

```python
#!/usr/bin/env python3
"""CLI do dk. Simula por padrão; `--apply` é explícito."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import espinha, leitura, ops, registry  # noqa: E402


def cmd_levantar(args) -> int:
    projeto = Path(args.projeto).resolve()
    reg = leitura.Registro()

    fontes = []
    for nome in ('requisitos', 'regras'):
        p = projeto / 'registry' / f'{nome}.json'
        if p.exists():
            reg.ler(p)
            fontes.append(p)

    bruto = Path(args.insumo).read_text(encoding='utf-8')
    a = espinha.ata(bruto)
    novas_regras = espinha.regras(a)
    novos_req = espinha.requisitos(novas_regras)

    regras_atuais = registry.carregar(projeto, 'regras')
    req_atuais = registry.carregar(projeto, 'requisitos')
    acoes = {'criado': 0, 'atualizado': 0}
    for r in novas_regras:
        regras_atuais, acao = registry.upsert(regras_atuais, r)
        acoes[acao] += 1
    for q in novos_req:
        req_atuais, acao = registry.upsert(req_atuais, q)
        acoes[acao] += 1

    op = ops.Operacao(projeto, escopo=['registry'], registro=reg, fontes=fontes)
    planos = [
        op.planejar(projeto / 'registry' / 'regras.json',
                    json.dumps(regras_atuais, ensure_ascii=False, indent=2) + '\n'),
        op.planejar(projeto / 'registry' / 'requisitos.json',
                    json.dumps(req_atuais, ensure_ascii=False, indent=2) + '\n'),
    ]

    if not args.apply:
        for p in planos:
            print(f"{p['acao']}: {p['caminho']}")
        print(f"regras {len(novas_regras)} · requisitos {len(novos_req)} · "
              f"criados {acoes['criado']} · atualizados {acoes['atualizado']}")
        print('simulação — nada foi gravado. Use --apply para aplicar.')
        return 0

    op.aplicar()
    print(f"gravado: criados {acoes['criado']}, atualizados {acoes['atualizado']}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog='dk')
    sub = p.add_subparsers(dest='cmd', required=True)
    lev = sub.add_parser('levantar', help='insumo de reunião → regras e requisitos')
    lev.add_argument('--projeto', required=True)
    lev.add_argument('--insumo', required=True)
    lev.add_argument('--apply', action='store_true',
                     help='aplica; sem esta flag, apenas simula')
    lev.set_defaults(func=cmd_levantar)
    args = p.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 6: Tornar executável e conferir a simulação**

Run: `chmod +x bin/dk && python3 verificar.py`
Expected: todos os validadores verdes

- [ ] **Step 7: Commit**

```bash
git add core/espinha.py bin/dk tests/validate_espinha_unidades.py
git commit -m "feat: unidades deterministicas da espinha e CLI dk levantar"
```

---

### Task 11: Skills da etapa `levantar`

**Files:**
- Create: `dk/skills/dk-levantar-ata/SKILL.md`
- Create: `dk/skills/dk-levantar-regras/SKILL.md`
- Create: `dk/skills/dk-levantar-requisitos/SKILL.md`

**Interfaces:**
- Consumes: `bin/dk levantar`, `agents/dk-levantar.md`
- Produces: as três skills enumeradas pelo agente da Task 8

- [ ] **Step 1: Criar `dk-levantar-ata`**

```markdown
---
name: dk-levantar-ata
description: Transforma insumo bruto de reunião - transcrição automática, anotação solta ou rascunho - em ata estruturada com data, participantes e falas atribuídas. Use quando a etapa levantar do DK estiver ativa e houver insumo de reunião ainda não estruturado.
argument-hint: "[caminho do insumo bruto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: documento
---

# dk-levantar-ata

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Entradas

Um arquivo de insumo em `0-apoio/reunioes/`.

## Procedimento

1. Leia a ata anterior, se existir, antes de qualquer proposta.
2. Rode a estruturação determinística:
   `bin/dk levantar --projeto <raiz> --insumo <arquivo>`
3. Revise o que o comando extraiu: participante mal atribuído e fala truncada são
   erros de forma que você corrige; o conteúdo da fala não se altera.
4. Aplique com `--apply` somente após a simulação estar correta.

## Regras

- Fala é citada, nunca parafraseada.
- Participante sem nome identificável fica como `não identificado`, não é inventado.
- Ata que já existe é atualizada; não se cria uma segunda ata da mesma reunião.

## Resposta

O caminho da ata e uma frase dizendo quantas falas foram estruturadas e o que mudou
em relação à versão anterior, se havia.
```

- [ ] **Step 2: Criar `dk-levantar-regras`**

```markdown
---
name: dk-levantar-regras
description: Extrai regras de negócio candidatas de uma ata, cada uma com a citação literal que a originou e a autoridade de quem disse. Use quando a etapa levantar do DK estiver ativa e houver ata estruturada sem regras derivadas.
argument-hint: "[caminho da ata]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-levantar-regras

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Leia `registry/regras.json` antes de propor qualquer coisa.
2. Rode a extração determinística pela CLI, em simulação.
3. Para cada candidata, decida: é regra de negócio, ou é comentário? Candidata
   descartada vira registro com motivo, não desaparece.
4. Regra que já existe no registro é **atualizada**. Nunca some uma segunda com
   o mesmo enunciado.

## Regras

- Regra sem citação de origem é recusada.
- Regra atribuída ao cliente sem citação vira `autoridade: inferida`, que é o que
  ela de fato é.

## Resposta

Tabela com `id`, `enunciado`, `autoridade`, `origem` e se foi criada ou atualizada.
```

- [ ] **Step 3: Criar `dk-levantar-requisitos`**

```markdown
---
name: dk-levantar-requisitos
description: Deriva requisitos rastreáveis das regras de negócio, vinculando cada requisito à regra que o originou, e atualiza os requisitos que já existem no projeto em vez de duplicá-los. Use quando a etapa levantar do DK estiver ativa e houver regras sem requisito correspondente.
argument-hint: "[opcional: id da regra]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-levantar-requisitos

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. **Leia `registry/requisitos.json` e todo documento de requisitos já existente
   no projeto.** Esta leitura é obrigatória: sem ela a gravação é recusada pelo
   próprio mecanismo de escrita.
2. Rode a derivação em simulação e leia o diff.
3. Requisito cujo `deriva_de` já existe é atualizado no lugar. Requisito novo é
   acrescentado com id na sequência.
4. Aplique com `--apply`.

## Regras

- Requisito sem `deriva_de` é recusado.
- Requisito que já existia e não mudou não é reescrito — não gere ruído no diff.
- Requisito removido de uma regra revogada é marcado, não apagado.

## Resposta

Tabela com `id`, `titulo`, `deriva_de` e ação — criado ou atualizado — e uma frase
com o total de regras ainda sem requisito.
```

- [ ] **Step 4: Enumerar as três no agente**

O agente `agents/dk-levantar.md` da Task 8 já lista as três skills na seção
`## Skills desta etapa`. Confirme que os nomes batem exatamente.

- [ ] **Step 5: Rodar a bateria**

Run: `python3 verificar.py`
Expected: tudo verde — em especial `validate_enumeracao`, `validate_portao_e_orcamento` e `validate_contrato_de_resposta`

- [ ] **Step 6: Commit**

```bash
git add skills/dk-levantar-ata skills/dk-levantar-regras skills/dk-levantar-requisitos
git commit -m "feat: skills da etapa levantar com portao e contrato de resposta"
```

---

### Task 12: Teste E2E da espinha

**Files:**
- Create: `dk/tests/fixtures/projeto-exemplo/0-apoio/reunioes/2026-08-14-convenios.md`
- Create: `dk/tests/fixtures/projeto-exemplo/2026-08-28-convenios-revisao.md`
- Test: `dk/tests/validate_ciclo_ponta_a_ponta.py`

**Interfaces:**
- Consumes: `bin/dk levantar`, `core.registry`
- Produces: a prova das quatro asserções da spec

Contexto: o Kit anterior **tinha** um `tests/validate_ciclo_ponta_a_ponta.py`. O teste existia e nunca rodava, porque `core.hooksPath` estava desconfigurado em todos os clones. Por isso a Task 5 vem antes desta.

- [ ] **Step 1: Criar as fixtures**

Grave em `tests/fixtures/projeto-exemplo/0-apoio/reunioes/2026-08-14-convenios.md`:

```markdown
Reunião 14/08 — Convênios
Fulana (gestora): o convênio não expira sozinho, quem tira do ar é o gestor.
Beltrano: e quando o prazo vence?
Fulana: fica vencido na lista, mas continua no ar até alguém revogar.
```

Grave em `tests/fixtures/projeto-exemplo/2026-08-28-convenios-revisao.md`:

```markdown
Reunião 28/08 — Convênios
Fulana (gestora): o convênio não expira sozinho, quem tira do ar é o gestor, e agora precisa registrar o motivo da revogação.
Beltrano: e quando o prazo vence?
Fulana: fica vencido na lista, mas continua no ar até alguém revogar.
```

- [ ] **Step 2: Escrever o teste que falha**

Grave em `tests/validate_ciclo_ponta_a_ponta.py`:

```python
#!/usr/bin/env python3
"""O ciclo inteiro: insumo de reunião → regras → requisitos, com as quatro asserções.

A quarta é a que importa mais: insumo alterado ATUALIZA o requisito existente em
vez de criar um novo ao lado. É o teste de regressão do furo relatado pelo time."""
from __future__ import annotations
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import registry  # noqa: E402

FIXTURE = RAIZ / 'tests' / 'fixtures' / 'projeto-exemplo'
errors = []


def rodar(projeto: Path, insumo: Path):
    return subprocess.run(
        [sys.executable, str(RAIZ / 'bin' / 'dk'), 'levantar',
         '--projeto', str(projeto), '--insumo', str(insumo), '--apply'],
        capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    shutil.copytree(FIXTURE, projeto)
    primeiro = projeto / '0-apoio' / 'reunioes' / '2026-08-14-convenios.md'

    # simulação não grava
    seco = subprocess.run(
        [sys.executable, str(RAIZ / 'bin' / 'dk'), 'levantar',
         '--projeto', str(projeto), '--insumo', str(primeiro)],
        capture_output=True, text=True)
    if seco.returncode != 0:
        errors.append(f'simulação falhou: {seco.stdout}{seco.stderr}')
    if (projeto / 'registry' / 'requisitos.json').exists():
        errors.append('a simulação gravou em disco')

    # asserção 1: o artefato foi gerado
    r1 = rodar(projeto, primeiro)
    if r1.returncode != 0:
        errors.append(f'primeira execução falhou: {r1.stdout}{r1.stderr}')
    if not (projeto / 'registry' / 'requisitos.json').exists():
        errors.append('asserção 1: requisitos.json não foi gerado')

    # asserção 2: o registro foi atualizado, não só o arquivo
    regras_1 = registry.carregar(projeto, 'regras')
    req_1 = registry.carregar(projeto, 'requisitos')
    if not regras_1:
        errors.append('asserção 2: nenhuma regra no registro')
    if not req_1:
        errors.append('asserção 2: nenhum requisito no registro')
    for q in req_1:
        if not q.get('deriva_de'):
            errors.append(f"asserção 2: {q.get('id')} sem vínculo com a regra")

    # asserção 3: rodar de novo com o mesmo insumo não duplica
    r2 = rodar(projeto, primeiro)
    if r2.returncode != 0:
        errors.append(f'segunda execução falhou: {r2.stdout}{r2.stderr}')
    req_2 = registry.carregar(projeto, 'requisitos')
    if len(req_2) != len(req_1):
        errors.append(
            f'asserção 3: idempotência quebrada — {len(req_1)} → {len(req_2)} requisitos')
    if registry.carregar(projeto, 'regras') != regras_1:
        errors.append('asserção 3: o registro de regras mudou sem insumo novo')

    # asserção 4: insumo alterado ATUALIZA o existente, não cria ao lado
    revisao = projeto / '2026-08-28-convenios-revisao.md'
    r3 = rodar(projeto, revisao)
    if r3.returncode != 0:
        errors.append(f'terceira execução falhou: {r3.stdout}{r3.stderr}')
    req_3 = registry.carregar(projeto, 'requisitos')
    if len(req_3) != len(req_1):
        errors.append(
            f'asserção 4: o insumo revisado criou requisito ao lado — '
            f'{len(req_1)} → {len(req_3)}. É exatamente o furo que o DK existe para impedir.')
    alvo = [q for q in req_3 if q['id'] == req_1[0]['id']]
    if not alvo:
        errors.append('asserção 4: o requisito original sumiu')
    elif 'motivo da revogação' not in alvo[0]['titulo']:
        errors.append(
            f"asserção 4: o requisito não foi atualizado com o texto novo: "
            f"{alvo[0]['titulo']!r}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 3: Rodar o teste**

Run: `python3 tests/validate_ciclo_ponta_a_ponta.py`
Expected: PASS. Se a asserção 4 falhar, o `upsert` da Task 9 ou a geração de id em `core/espinha.py` estão criando id novo para a mesma regra — corrija a derivação de id antes de seguir, porque é o defeito central que este plano existe para impedir.

- [ ] **Step 4: Rodar a bateria inteira**

Run: `python3 verificar.py`
Expected: `tudo verde`

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures tests/validate_ciclo_ponta_a_ponta.py
git commit -m "test: ciclo ponta a ponta com as quatro assercoes da espinha"
```

---

### Task 13: Contrato para agentes — `llms.txt` e `llms-full.txt`

**Files:**
- Create: `dk/llms.txt`
- Create: `dk/llms-full.txt`
- Create: `dk/CLAUDE.md`
- Test: `dk/tests/validate_contrato_llm.py`

**Interfaces:**
- Consumes: `core.skills.ETAPAS`, `core.versao.versao_canonica`
- Produces: os dois contratos e a regra de que o `CLAUDE.md` referencia em vez de repetir

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_contrato_llm.py`:

```python
#!/usr/bin/env python3
"""Os dois contratos existem, têm papéis diferentes, e nada os copia.

llms.txt é roteador: curto, aponta. llms-full.txt é contrato: completo, tem os
invariantes. O CLAUDE.md referencia os dois e não repete nenhum."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []

curto = RAIZ / 'llms.txt'
longo = RAIZ / 'llms-full.txt'
claude = RAIZ / 'CLAUDE.md'

for f in (curto, longo, claude):
    if not f.exists():
        errors.append(f'{f.name} não existe')

if not errors:
    t_curto = curto.read_text(encoding='utf-8')
    t_longo = longo.read_text(encoding='utf-8')
    t_claude = claude.read_text(encoding='utf-8')

    if len(t_curto.encode('utf-8')) > 4096:
        errors.append(f'llms.txt tem {len(t_curto.encode("utf-8"))} B — '
                      'é roteador, não enciclopédia; limite 4096 B')
    if 'NON-NEGOTIABLE INVARIANTS' not in t_longo:
        errors.append('llms-full.txt sem a seção NON-NEGOTIABLE INVARIANTS')
    if len(t_longo) <= len(t_curto):
        errors.append('llms-full.txt não é mais completo que o llms.txt')

    if 'llms-full.txt' not in t_claude:
        errors.append('CLAUDE.md não referencia o llms-full.txt')
    if len(t_claude.encode('utf-8')) > 2048:
        errors.append(f'CLAUDE.md tem {len(t_claude.encode("utf-8"))} B — '
                      'ele referencia, não repete; limite 2048 B')

    for bloco in [b for b in t_longo.split('\n\n') if len(b) > 200]:
        if bloco in t_claude:
            errors.append('CLAUDE.md copia um bloco do llms-full.txt')
            break

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_contrato_llm.py`
Expected: FAIL com os três arquivos ausentes

- [ ] **Step 3: Escrever `llms.txt`**

```markdown
# dk

Processo de design ponta a ponta: da reunião com o cliente ao handoff para
desenvolvimento. Plugin de Claude Code, autônomo, sem dependências obrigatórias.

## O que é

O `dk` conduz seis etapas, nesta ordem: `audit`, `levantar`, `entender`,
`entregar`, `prototipar`, `handoff`. Cada etapa tem uma porta e um agente que
enumera as skills dela.

## Entrada

- Skill `dk` — porta geral. Lê o estado do projeto e escolhe a etapa.
- CLI `bin/dk` — parte determinística. Simula por padrão; `--apply` é explícito.

## Regras críticas

- Nenhum artefato é gravado sem que sua fonte tenha sido lida.
- Toda escrita declara escopo, simula, e só então aplica.
- Requisito que já existe é atualizado, nunca duplicado.

## Onde está o detalhe

- Contrato completo e invariantes: `llms-full.txt`
- Contrato de resposta das skills: `docs/contrato-de-resposta.md`
- Políticas de governança: `governance/`
- Validadores: `tests/validate_*.py`, coletados por `verificar.py`
```

- [ ] **Step 4: Escrever `llms-full.txt`**

Grave o conteúdo abaixo. É o contrato completo; nenhum outro arquivo o repete.

```markdown
# dk — contrato para agentes

## Visão

O `dk` conduz um projeto de design da reunião com o cliente ao handoff para
desenvolvimento, produzindo artefatos rastreáveis em cada etapa. Ele não é uma
biblioteca de componentes: governa processo e artefato.

## Arquitetura

Núcleo determinístico em Python roda antes de qualquer LLM. A LLM entra onde há
raciocínio — redigir, julgar relevância, decidir se duas regras são a mesma. Forma,
extração, vínculo e validação são código.

```
bin/dk  →  core/  →  registry/  →  skills (LLM)  →  artefato
```

## Terminologia

- **Etapa** — uma das seis fases: audit, levantar, entender, entregar, prototipar, handoff.
- **Porta** — a skill sem portão que dá entrada numa etapa.
- **Portão** — a frase na description que amarra a skill a uma etapa.
- **Registro** — arquivo em `registry/` com os itens de um tipo: regras, requisitos, decisões.
- **Procedência** — data, fonte, autoria e citação literal que sustentam um item.

## Modelo operacional

1. A porta `dk` lê o estado do projeto e escolhe a etapa.
2. O agente da etapa enumera suas skills e escolhe uma.
3. A skill lê o que já existe, simula a escrita, mostra o diff.
4. Aplicar é explícito.

## Estrutura

`core/` núcleo · `skills/` skills planas · `agents/` um por etapa ·
`modules/` módulos com manifesto próprio · `governance/` políticas ·
`tests/` validadores · `verificar.py` coletor.

## Etapas e portas

| Etapa | Porta | Entrega |
|---|---|---|
| audit | `dk-audit` | mapa do projeto e conformidade |
| levantar | `dk-levantar` | ata, regras de negócio, requisitos |
| entender | `dk-entender` | cobertura, lacunas, léxico |
| entregar | `dk-entregar` | documento formatado para o cliente |
| prototipar | `dk-prototipar` | protótipo, tokens, componentes |
| handoff | `dk-handoff` | passagem para desenvolvimento |

## Skills

Toda skill declara `name`, `description`, `argument-hint`, `allowed-tools` e
`forma-da-saida`. Toda skill que não é porta declara o portão da sua etapa.

## Agentes e enumeração

`agents/dk-<etapa>.md` contém a seção `## Skills desta etapa` listando cada skill
da etapa. Skill com portão que não aparece ali é inalcançável, e o validador reprova.

## CLI

`bin/dk <comando> --projeto <raiz> [--apply]`. Sem `--apply`, simula e imprime o diff.

## Registros

`registry/<tipo>.json`, lista de objetos com `id`. Item com id existente é fundido,
nunca anexado. Campo ausente na atualização preserva o valor anterior.

## Validação

`python3 verificar.py` roda todo `tests/validate_*.py`. `--release` roda o portão
de release. O hook `pre-push` chama o coletor, e sua ativação é verificada por teste.

## Compatibilidade

O `dk` é autônomo. Não lê, referencia nem depende de `seakit`, `sea-design-kit` ou
`design-ai-community`. Nenhuma dependência externa é obrigatória.

## Processo de extensão

Skill nova precisa: portão da etapa, enumeração no agente da etapa, `forma-da-saida`,
referência ao contrato de resposta, e passar em `verificar.py`. Skill que duplica
capacidade existente é recusada na revisão — a política está em
`governance/naming-conventions.md`.

## NON-NEGOTIABLE INVARIANTS

- Nenhum artefato é gravado sem que sua fonte tenha sido lida na sessão.
- Toda operação de escrita declara escopo; escrita fora do escopo é recusada.
- Toda operação de escrita simula por padrão; aplicar é explícito.
- Toda escrita é atômica: arquivo temporário no mesmo diretório e `os.replace`.
- O contrato de resposta é referenciado, nunca copiado.
- Nenhuma operação lê o repositório inteiro por padrão.
- Uma informação tem uma fonte canônica; toda outra ocorrência é derivada.
- Toda skill que não é porta declara o portão da sua etapa.
- Toda skill com portão é enumerada pelo agente da sua etapa.
- Nenhuma dependência externa é obrigatória; ausência degrada anunciada.
- O pacote não é publicado sem o teste de ciclo ponta a ponta verde.
```

- [ ] **Step 5: Escrever o `CLAUDE.md` curto**

```markdown
# dk

Plugin de processo de design ponta a ponta.

O contrato completo, com os invariantes inegociáveis, está em `llms-full.txt`.
O roteador de conhecimento está em `llms.txt`. Este arquivo não repete nenhum dos dois.

## Antes de qualquer trabalho

1. Leia o estado do projeto antes de propor escrita.
2. Simule antes de aplicar.
3. Responda segundo `docs/contrato-de-resposta.md`.
```

- [ ] **Step 6: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_contrato_llm.py && python3 verificar.py`
Expected: ambos PASS

- [ ] **Step 7: Commit**

```bash
git add llms.txt llms-full.txt CLAUDE.md tests/validate_contrato_llm.py
git commit -m "feat: llms.txt roteador e llms-full.txt com invariantes"
```

---

### Task 14: Governança recuperada do ancestral

**Files:**
- Create: `dk/governance/` (11 arquivos copiados e revisados)
- Create: `dk/.gitlab/CODEOWNERS`
- Create: `dk/.gitlab/merge_request_templates/padrao.md`
- Test: `dk/tests/validate_governanca.py`

**Interfaces:**
- Consumes: `design-ai-community/governance/` (somente leitura)
- Produces: as políticas ativas no `dk`

Contexto: as 11 políticas já existem em disco e nunca foram carregadas para o Kit (achado DK-110). O `naming-conventions.md`, de 14/05, cobre a política de depreciação de nome de skill que trava um pedido desde 04/08.

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_governanca.py`:

```python
#!/usr/bin/env python3
"""As políticas de governança estão presentes e têm dono declarado."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
OBRIGATORIAS = [
    'naming-conventions.md', 'versioning-policy.md', 'review-process.md',
    'content-lifecycle.md', 'delivery-checklist.md', 'input-contract.md',
    'OWNERS.md', 'README.md',
]

errors = []
gov = RAIZ / 'governance'

for nome in OBRIGATORIAS:
    f = gov / nome
    if not f.exists():
        errors.append(f'governance/{nome} ausente')
        continue
    texto = f.read_text(encoding='utf-8')
    if nome != 'README.md' and 'owner:' not in texto and 'Owner' not in texto:
        errors.append(f'governance/{nome} sem dono declarado')
    if 'TBD' in texto:
        errors.append(f'governance/{nome} contém TBD — política sem dono real')

for caminho in ('.gitlab/CODEOWNERS', '.gitlab/merge_request_templates/padrao.md'):
    if not (RAIZ / caminho).exists():
        errors.append(f'{caminho} ausente')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_governanca.py`
Expected: FAIL listando os 10 arquivos ausentes

- [ ] **Step 3: Copiar as políticas do ancestral**

```bash
cd /Users/sea/SEA/plugins/dk
mkdir -p governance .gitlab/merge_request_templates
cp /Users/sea/SEA/plugins/design-ai-community/governance/*.md governance/
cp /Users/sea/SEA/plugins/design-ai-community/.gitlab/CODEOWNERS .gitlab/
cp /Users/sea/SEA/plugins/design-ai-community/.gitlab/merge_request_templates/* \
   .gitlab/merge_request_templates/
```

- [ ] **Step 4: Revisar cada política**

Abra cada arquivo em `governance/` e faça três correções, sem reescrever o conteúdo:

1. Troque toda referência a `design-ai-community` por `dk`.
2. Substitua todo `owner: TBD` e `reviewers: [TBD]` pelo dono real. Política sem
   dono é o que a auditoria chama de contrato sem fonte canônica — o teste do
   Step 1 reprova `TBD`.
3. Onde a política citar caminho que não existe no `dk`, ajuste o caminho ou
   remova a linha. Não invente estrutura para casar com a política.

- [ ] **Step 5: Rodar o teste e confirmar que passa**

Run: `python3 tests/validate_governanca.py && python3 verificar.py`
Expected: ambos PASS

- [ ] **Step 6: Commit**

```bash
git add governance .gitlab tests/validate_governanca.py
git commit -m "feat: recupera as politicas de governanca do ancestral"
```

---

### Task 15: Portão de release

**Files:**
- Create: `dk/tests/validate_release_gate.py`
- Modify: `dk/verificar.py` (adicionar o modo `--release`)

**Interfaces:**
- Consumes: todos os validadores anteriores
- Produces: `verificar.py --release` que reprova publicação com qualquer item do portão aberto

- [ ] **Step 1: Escrever o teste que falha**

Grave em `tests/validate_release_gate.py`:

```python
#!/usr/bin/env python3
"""O portão de release: nada é publicado com um item aberto.

O primeiro item é o que impede repetir o erro de origem do Kit anterior —
publicar sem o ciclo provado ponta a ponta."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

ITENS = [
    ('teste E2E da espinha verde', 'tests/validate_ciclo_ponta_a_ponta.py'),
    ('hooks ativos e verificados', 'tests/validate_hooks_ativos.py'),
    ('escrita atômica', 'tests/validate_escrita_atomica.py'),
    ('dry-run e escopo declarado', 'tests/validate_dry_run_e_escopo.py'),
    ('ler antes de escrever', 'tests/validate_ler_antes_de_escrever.py'),
    ('versão em fonte única', 'tests/validate_versao_unica.py'),
    ('portão e orçamento de catálogo', 'tests/validate_portao_e_orcamento.py'),
    ('enumeração por agente', 'tests/validate_enumeracao.py'),
    ('contrato de resposta', 'tests/validate_contrato_de_resposta.py'),
    ('llms.txt e llms-full.txt', 'tests/validate_contrato_llm.py'),
    ('governança recuperada', 'tests/validate_governanca.py'),
]

errors = []
for rotulo, teste in ITENS:
    caminho = RAIZ / teste
    if not caminho.exists():
        errors.append(f'[ ] {rotulo} — {teste} não existe')
        continue
    r = subprocess.run([sys.executable, str(caminho)], cwd=str(RAIZ),
                       capture_output=True, text=True)
    marca = '[x]' if r.returncode == 0 else '[ ]'
    print(f'{marca} {rotulo}')
    if r.returncode != 0:
        errors.append(f'{rotulo}: {teste} reprovou')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar o teste**

Run: `python3 tests/validate_release_gate.py`
Expected: PASS com os 11 itens marcados `[x]`

- [ ] **Step 3: Ligar o modo `--release` ao coletor**

Em `verificar.py`, dentro de `main()`, antes do `return`, acrescente:

```python
    if '--release' in sys.argv:
        r = subprocess.run([sys.executable, 'tests/validate_release_gate.py'],
                           cwd=str(RAIZ), capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode != 0:
            print('portão de release fechado — publicação bloqueada')
            return 1
        print('portão de release aberto')
```

- [ ] **Step 4: Conferir os dois modos**

Run: `python3 verificar.py && python3 verificar.py --release`
Expected: `tudo verde` e `portão de release aberto`

- [ ] **Step 5: Commit**

```bash
git add tests/validate_release_gate.py verificar.py
git commit -m "feat: portao de release que bloqueia publicacao com item aberto"
```

---

## Cobertura da spec

Este plano entrega as seções 4.1 a 4.4, 6, 7 e 9 da spec. Fica explicitamente para os
planos seguintes, com o motivo:

| Item da spec | Plano | Por quê |
|---|---|---|
| Invariante `MAP ANTES DE LER` (4.4) | com `dk audit` | é o invariante da varredura, e a varredura nasce na etapa `audit` |
| Porte das 27 regras de validação (5.0.1) | com `dk audit` | validam estrutura de **projeto**, que só existe quando o `audit` mapeia um |
| Destino das 275 skills (5.0) | um plano por família | cada família é um subsistema testável por si |
| Camada de entregável e pipeline de renderização (5.1, 5.2) | plano 2 | depende da espinha gravando registro correto |
| Módulo design-system (5.3) | plano 4 | maior item; depende do cruzamento decidido na spec |
| Congelamento das bases antigas (10) | último | só depois de o `dk` cobrir o que elas cobriam |

## Depois deste plano

Cada família seguinte ganha plano próprio, sempre atrás da espinha já provada, na ordem:

1. `dk audit` e a camada de repository intelligence
2. Camada de entregável — as 9 skills do community, com o pipeline HTML canônico
3. Etapa `entender` — as skills de cobertura, lacuna e léxico portadas do Kit
4. `modules/design-system/` — cruzamento DLS × Kit conforme a seção 5.3 da spec
5. `modules/git-workflow/`, `modules/liferay-migration/`, `modules/similar-analysis/`, `modules/lean-inception/`
6. Congelamento do `sea-design-kit` e do `design-ai-community`, com inspeção prévia dos sete clones

Nenhuma família entra antes de `python3 verificar.py --release` estar aberto.
