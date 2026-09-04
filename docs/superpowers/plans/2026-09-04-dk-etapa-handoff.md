# DK — Etapa `handoff` · Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fechar o pipeline. O `handoff` é a etapa onde tudo que as anteriores produziram é cobrado de uma vez: sem cobertura fechada, sem inconsistência bloqueante, sem lacuna crítica aberta e sem violação de padrão, o pacote não sai.

**Architecture:** `core/prontidao` agrega os verificadores das cinco etapas anteriores num gate único — é a peça que faz o handoff valer alguma coisa. `core/rastreabilidade` monta a matriz bidirecional regra ↔ requisito ↔ entregável ↔ changeset, que vai dentro do pacote. O documento usa o pipeline de entregável que já existe.

**Tech Stack:** Python 3.9+ (stdlib apenas).

**Spec:** `docs/superpowers/specs/2026-09-03-dk-consolidacao-design.md`
**Planos anteriores:** fundação e espinha · audit · entregável · entender · prototipar

## Global Constraints

Valem todas as dos planos anteriores, e mais estas:

- **O gate agrega, não duplica.** `core/prontidao` chama `cobertura`, `consistencia`,
  `lacunas`, `prototipo`, `padrao` e `entregaveis`. Nenhuma verificação nova é escrita
  aqui; o handoff é o lugar onde as existentes são cobradas juntas.
- **Bloqueio tem motivo e caminho.** Cada item que trava o handoff diz qual etapa
  resolve e qual comando rodar.
- **O orçamento de catálogo é decidido, não estourado em silêncio.** Este plano fecha
  a colisão registrada no plano 5.

## O que é portado, e de onde

| Capacidade | Origem | Forma no `dk` |
|---|---|---|
| Gate de aprovação antes de exportar | `sea-ux-handoff` (Kit) | `core/prontidao.py` |
| Matriz de rastreabilidade bidirecional | `sea-ux-traceability` (Kit) | `core/rastreabilidade.py` |
| Prontidão agregando DoD | `sea-ux-delivery-readiness` (Kit) | itens do gate |
| Seções do documento de handoff | `gerar-handoff-desenvolvimento` (community) | contrato `handoff` |
| Triagem de dúvida de desenvolvimento | `sea-ux-dev-question-analyzer` (Kit) | skill `dk-handoff-duvida` |

---

### Task 1: Orçamento de catálogo — fechar a colisão

**Files:**
- Modify: `dk/core/skills.py`
- Modify: `dk/tests/validate_portao_e_orcamento.py`

O plano 5 registrou: 1.814 B de 2.048, e a sétima porta estoura. O número 2.048 foi
escolhido antes de o desenho ter forma. Agora ele tem: **sete portas, uma por etapa mais
a porta geral.** O orçamento passa a ser derivado disso, com folga declarada, e a regra
nova é que uma oitava porta exige decisão explícita — não cabe por acaso.

- [ ] **Step 1: Ajustar o orçamento com a justificativa no código**

```python
# Sete portas: uma por etapa mais a porta geral. A 2.560 B (~640 tokens) o catálogo
# fixo custa 5% dos 49.678 B que o Kit anterior gastava em toda sessão, e cabe com
# folga no CORE CONTEXT de 3k tokens que a spec fixou.
#
# A folga não é convite: `MAX_PORTAS` trava em sete. Porta nova exige mudar este
# número, e mudar este número é uma decisão que aparece no diff.
ORCAMENTO_BYTES = 2560
MAX_PORTAS = 7
```

- [ ] **Step 2: Acrescentar a trava de quantidade ao teste**

```python
sem_portao = [i for i in inventario if not i['portao']]
if len(sem_portao) > skills.MAX_PORTAS:
    errors.append(
        f'{len(sem_portao)} skills sem portão para no máximo '
        f'{skills.MAX_PORTAS} portas — porta nova exige decisão explícita')
```

- [ ] **Step 3: Rodar e commitar**

```bash
python3 tests/validate_portao_e_orcamento.py
git add core/skills.py tests/validate_portao_e_orcamento.py
git commit -m "feat: orcamento de catalogo derivado das sete portas, com trava de quantidade"
```

---

### Task 2: O gate de prontidão

**Files:**
- Create: `dk/core/prontidao.py`
- Test: `dk/tests/validate_prontidao.py`

**Interfaces:**
- Produces: `core.prontidao.avaliar(raiz) -> dict` com `pronto`, `bloqueios`, `avisos`,
  `itens` — cada item com `nome`, `estado`, `evidencia`, `resolve_em`, `comando`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O handoff só sai com o pipeline fechado.

O gate não inventa verificação: ele cobra, de uma vez, as que as etapas
anteriores já fazem. Cada bloqueio diz qual etapa resolve e qual comando rodar."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, padrao, prontidao, registry  # noqa: E402

errors = []


def projeto_com_furo(raiz: Path) -> Path:
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'o gestor revoga o convênio'},
        {'id': 'RN-099', 'enunciado': 'revogado não reativa'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'revogação manual pelo gestor',
         'deriva_de': 'RN-001'},
    ])
    return raiz


with tempfile.TemporaryDirectory() as d:
    raiz = projeto_com_furo(Path(d))
    r = prontidao.avaliar(raiz)

    if r['pronto']:
        errors.append('projeto com regra órfã e lacunas não deveria estar pronto')
    if not r['bloqueios']:
        errors.append('nenhum bloqueio num projeto com furo')

    nomes = {i['nome'] for i in r['itens']}
    for esperado in ('cobertura', 'consistencia', 'lacunas', 'padrao',
                     'prototipo', 'entregaveis'):
        if esperado not in nomes:
            errors.append(f'o gate não cobra {esperado}')

    for i in r['itens']:
        for campo in ('nome', 'estado', 'evidencia', 'resolve_em', 'comando'):
            if campo not in i:
                errors.append(f"{i.get('nome')}: item do gate sem {campo}")
        if i['estado'] not in ('ok', 'bloqueio', 'aviso'):
            errors.append(f"{i['nome']}: estado inválido {i['estado']!r}")

    cob = [i for i in r['itens'] if i['nome'] == 'cobertura'][0]
    if cob['estado'] != 'bloqueio':
        errors.append('regra órfã deveria bloquear a cobertura')
    if 'RN-099' not in cob['evidencia']:
        errors.append(f"a evidência não nomeia a regra órfã: {cob['evidencia']}")
    if 'entender' not in cob['resolve_em']:
        errors.append('o bloqueio de cobertura deveria apontar a etapa entender')
    if 'dk entender' not in cob['comando']:
        errors.append('o bloqueio deveria dar o comando que resolve')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001',
         'enunciado': 'o gestor com perfil de acesso revoga o convênio; '
                      'objetivo é reduzir o indicador de vencidos; escopo '
                      'restrito ao módulo; integra com o portal; migra dado '
                      'do cadastro atual; hoje é planilha'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001',
         'titulo': 'revogação manual pelo gestor com perfil de acesso; '
                   'objetivo, escopo, integração, dado migrado e prazo definidos',
         'deriva_de': 'RN-001'},
    ])
    io.atomic_write(raiz / padrao.destino('requisitos') / 'requisitos-2026-09-04.html',
                    '<p>REQ-001</p>')
    io.atomic_write(raiz / padrao.destino('ata') / 'ata-2026-09-04.html', '<p>ok</p>')

    r = prontidao.avaliar(raiz)
    cob = [i for i in r['itens'] if i['nome'] == 'cobertura'][0]
    if cob['estado'] == 'bloqueio':
        errors.append(f"cobertura fechada não deveria bloquear: {cob['evidencia']}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_prontidao.py`
Expected: FAIL com `ImportError: cannot import name 'prontidao'`

- [ ] **Step 3: Implementar `core/prontidao.py`**

```python
#!/usr/bin/env python3
"""O gate do handoff: o pipeline inteiro cobrado de uma vez.

Nenhuma verificação nova nasce aqui. O handoff é o lugar onde as verificações
que cada etapa já faz são cobradas juntas — e é isso que dá sentido a ele ser a
última etapa.

Todo bloqueio diz qual etapa resolve e qual comando rodar. Bloqueio sem saída é
só um muro."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

from core import (cobertura, consistencia, entregaveis, lacunas, padrao,
                  prototipo, registry)


def _item(nome, estado, evidencia, resolve_em, comando) -> Dict:
    return {'nome': nome, 'estado': estado, 'evidencia': evidencia,
            'resolve_em': resolve_em, 'comando': comando}


def avaliar(raiz: Path) -> Dict:
    raiz = Path(raiz)
    itens = []

    cob = cobertura.matriz(raiz)
    orfas = cob['regras_sem_requisito']
    sem_regra = cob['requisitos_sem_regra']
    if orfas or sem_regra:
        partes = []
        if orfas:
            partes.append('regra sem requisito: ' + ', '.join(orfas))
        if sem_regra:
            partes.append('requisito sem regra: ' + ', '.join(sem_regra))
        itens.append(_item('cobertura', 'bloqueio', ' · '.join(partes),
                           'entender', 'dk entender --projeto <raiz>'))
    else:
        itens.append(_item(
            'cobertura', 'ok',
            f"{cob['totais']['regras']} regras e {cob['totais']['requisitos']} "
            'requisitos, todos com par', 'entender',
            'dk entender --projeto <raiz>'))

    fora = cob['requisitos_sem_entregavel']
    if fora:
        itens.append(_item(
            'entregaveis', 'bloqueio',
            'requisito que não aparece em nenhum entregável: ' + ', '.join(fora),
            'entregar', 'dk entregar --tipo requisitos --projeto <raiz>'))
    else:
        itens.append(_item('entregaveis', 'ok',
                           'todo requisito aparece em algum entregável',
                           'entregar', 'dk entregar --projeto <raiz>'))

    inc = consistencia.analisar(registry.carregar(raiz, 'regras'),
                                registry.carregar(raiz, 'requisitos'))
    bloqueia = [a for a in inc if a['urgencia'] == 'BLOQUEIA-AVANCO']
    candidatos = [a for a in inc if a['decidido_por'] == 'skill']
    if bloqueia:
        itens.append(_item(
            'consistencia', 'bloqueio',
            f'{len(bloqueia)} inconsistência(s) que bloqueiam avanço: '
            + ', '.join(sorted({a['tipo'] for a in bloqueia})),
            'entender', 'dk entender --projeto <raiz>'))
    elif candidatos:
        itens.append(_item(
            'consistencia', 'aviso',
            f'{len(candidatos)} candidato(s) que a skill precisa julgar antes '
            'de fechar', 'entender', 'dk entender --projeto <raiz>'))
    else:
        itens.append(_item('consistencia', 'ok',
                           f'{len(inc)} achado(s), nenhum bloqueante',
                           'entender', 'dk entender --projeto <raiz>'))

    lac = lacunas.analisar(raiz)
    criticas = [a for a in lac
                if a['prioridade'] == 'CRITICA' and a['status'] == 'AUSENTE']
    parciais = [a for a in lac if a['status'] == 'PARCIAL']
    if criticas:
        itens.append(_item(
            'lacunas', 'bloqueio',
            f'{len(criticas)} lacuna(s) crítica(s) ausente(s): '
            + ', '.join(a['tema'] for a in criticas),
            'levantar', 'dk levantar --projeto <raiz> --insumo <arquivo>'))
    elif parciais:
        itens.append(_item(
            'lacunas', 'aviso',
            f'{len(parciais)} item(ns) do checklist só com menção isolada',
            'levantar', 'dk levantar --projeto <raiz> --insumo <arquivo>'))
    else:
        itens.append(_item('lacunas', 'ok', 'checklist de discovery coberto',
                           'levantar', 'dk levantar --projeto <raiz>'))

    estrutura = padrao.verificar(raiz)
    altos = [a for a in estrutura if a['impacto'] == 'alto']
    if altos:
        itens.append(_item(
            'padrao', 'bloqueio',
            f'{len(altos)} violação(ões) estrutural(is): '
            + '; '.join(a['evidencia'][:60] for a in altos[:3]),
            'audit', 'dk audit --projeto <raiz>'))
    elif estrutura:
        itens.append(_item(
            'padrao', 'aviso',
            f'{len(estrutura)} achado(s) estrutural(is) de impacto menor',
            'audit', 'dk audit --projeto <raiz>'))
    else:
        itens.append(_item('padrao', 'ok', 'estrutura do projeto em conformidade',
                           'audit', 'dk audit --projeto <raiz>'))

    proto = prototipo.verificar(raiz)
    proto_altos = [a for a in proto if a['impacto'] == 'alto']
    if proto_altos:
        itens.append(_item(
            'prototipo', 'bloqueio',
            f'{len(proto_altos)} violação(ões) de padrão no protótipo: '
            + '; '.join(f"regra {a['regra']}" for a in proto_altos[:4]),
            'prototipar', 'dk prototipar --projeto <raiz> --verificar'))
    elif proto:
        itens.append(_item(
            'prototipo', 'aviso',
            f'{len(proto)} achado(s) de padrão no protótipo',
            'prototipar', 'dk prototipar --projeto <raiz> --verificar'))
    else:
        itens.append(_item('prototipo', 'ok', 'protótipo dentro do padrão',
                           'prototipar', 'dk prototipar --projeto <raiz> --verificar'))

    bloqueios = [i for i in itens if i['estado'] == 'bloqueio']
    avisos = [i for i in itens if i['estado'] == 'aviso']
    return {
        'pronto': not bloqueios,
        'bloqueios': bloqueios,
        'avisos': avisos,
        'itens': itens,
    }
```

- [ ] **Step 4: Rodar, confirmar que passa e commitar**

```bash
python3 tests/validate_prontidao.py
git add core/prontidao.py tests/validate_prontidao.py
git commit -m "feat: gate de prontidao agregando as verificacoes das cinco etapas"
```

---

### Task 3: Matriz de rastreabilidade

**Files:**
- Create: `dk/core/rastreabilidade.py`
- Test: `dk/tests/validate_rastreabilidade.py`

**Interfaces:**
- Produces: `core.rastreabilidade.matriz(raiz) -> list[dict]` com uma linha por requisito,
  ligando regra de origem, citação, entregável onde aparece e changeset que o tocou;
  `core.rastreabilidade.markdown(linhas) -> str`

- [ ] **Step 1: Escrever o teste**

```python
#!/usr/bin/env python3
"""A matriz liga o requisito à sua origem e ao seu destino, nos dois sentidos."""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, padrao, rastreabilidade, registry  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'o gestor revoga',
         'citacao': 'quem tira do ar é o gestor', 'fonte': 'ata 14/08'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'revogação manual', 'deriva_de': 'RN-001'},
        {'id': 'REQ-002', 'titulo': 'sem origem'},
    ])
    io.atomic_write(raiz / padrao.destino('requisitos') / 'requisitos.html',
                    '<p>REQ-001 consta aqui</p>')
    io.atomic_write(raiz / '.dk' / 'changesets' / 'CS-001.json',
                    json.dumps({'id': 'CS-001', 'title': 'ajuste',
                                'affected': ['2-design/prototipo'],
                                'requisitos': ['REQ-001']}))

    linhas = rastreabilidade.matriz(raiz)
    por_id = {l['requisito']: l for l in linhas}

    if len(linhas) != 2:
        errors.append(f'esperadas 2 linhas, vieram {len(linhas)}')

    a = por_id.get('REQ-001', {})
    if a.get('regra') != 'RN-001':
        errors.append(f"REQ-001 sem a regra de origem: {a.get('regra')}")
    if 'quem tira do ar' not in (a.get('citacao') or ''):
        errors.append('a citação de origem não chegou à matriz')
    if not a.get('entregaveis'):
        errors.append('REQ-001 aparece no entregável e a matriz não viu')
    if 'CS-001' not in (a.get('changesets') or []):
        errors.append('o changeset que tocou o requisito não foi ligado')

    b = por_id.get('REQ-002', {})
    if b.get('regra'):
        errors.append('REQ-002 não tem origem; a matriz não pode inventar uma')
    if b.get('estado') != 'sem origem':
        errors.append(f"REQ-002 deveria ser marcado: {b.get('estado')}")

    md = rastreabilidade.markdown(linhas)
    if 'REQ-001' not in md or '| ' not in md:
        errors.append('markdown() não produziu tabela com os requisitos')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Implementar `core/rastreabilidade.py`**

```python
#!/usr/bin/env python3
"""Matriz bidirecional: de onde o requisito veio e para onde ele foi.

Uma linha por requisito. Para trás, a regra e a citação que o originaram; para
frente, o entregável onde aparece e o changeset que o tocou. Requisito sem origem
é marcado, nunca preenchido por dedução."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from core import padrao, registry


def _changesets(raiz: Path) -> List[dict]:
    pasta = Path(raiz) / '.dk' / 'changesets'
    if not pasta.is_dir():
        return []
    saida = []
    for arq in sorted(pasta.glob('*.json')):
        try:
            saida.append(json.loads(arq.read_text(encoding='utf-8')))
        except json.JSONDecodeError:
            continue
    return saida


def _entregaveis(raiz: Path) -> List[tuple]:
    saida = []
    for chave in ('requisitos', 'visao', 'ata'):
        pasta = Path(raiz) / padrao.destino(chave)
        if not pasta.is_dir():
            continue
        for arq in sorted(pasta.iterdir()):
            if arq.suffix.lower() in ('.html', '.md'):
                saida.append((str(arq.relative_to(raiz)),
                              arq.read_text(encoding='utf-8', errors='replace')))
    return saida


def matriz(raiz: Path) -> List[Dict]:
    raiz = Path(raiz)
    regras = {r['id']: r for r in registry.carregar(raiz, 'regras')}
    docs = _entregaveis(raiz)
    changesets = _changesets(raiz)

    linhas = []
    for q in registry.carregar(raiz, 'requisitos'):
        origem = q.get('deriva_de')
        regra = regras.get(origem) if origem else None
        onde = [caminho for caminho, texto in docs if q['id'] in texto]
        tocado = [cs['id'] for cs in changesets
                  if q['id'] in (cs.get('requisitos') or [])]

        if regra:
            estado = 'rastreado' if onde else 'sem entregável'
        else:
            estado = 'sem origem'

        linhas.append({
            'requisito': q['id'],
            'titulo': q.get('titulo', ''),
            'regra': regra['id'] if regra else '',
            'citacao': (regra or {}).get('citacao', ''),
            'fonte': (regra or {}).get('fonte', ''),
            'entregaveis': onde,
            'changesets': tocado,
            'estado': estado,
        })
    return linhas


def markdown(linhas: List[Dict]) -> str:
    saida = ['| Requisito | Origem | Citação | Entregável | Changeset | Estado |',
             '|---|---|---|---|---|---|']
    for l in linhas:
        saida.append(
            f"| {l['requisito']} | {l['regra'] or '—'} | "
            f"{(l['citacao'] or '—')[:50]} | "
            f"{', '.join(l['entregaveis']) or '—'} | "
            f"{', '.join(l['changesets']) or '—'} | {l['estado']} |")
    return '\n'.join(saida)
```

- [ ] **Step 3: Rodar e commitar**

---

### Task 4: Contrato do handoff e `dk handoff`

**Files:**
- Modify: `dk/core/entregaveis.py` (contrato `handoff`)
- Modify: `dk/bin/dk`
- Test: `dk/tests/validate_handoff_cli.py`

O contrato do handoff traz as seções do `gerar-handoff-desenvolvimento` do community:
visão geral, tokens, inventário de componentes, especificação por tela, fluxos críticos,
mais a matriz de rastreabilidade e o bloco de pendências.

- [ ] **Step 1: Acrescentar o contrato**

```python
    'handoff': {
        'titulo': 'Handoff para Desenvolvimento',
        'secoes': [
            'Visão geral',
            'Escopo deste handoff',
            'Design tokens',
            'Inventário de componentes',
            'Especificação por tela',
            'Fluxos críticos',
            'Rastreabilidade',
            'Pendências e dependências',
        ],
        'proibidas': [],
    },
```

- [ ] **Step 2: Escrever o teste do comando**

```python
#!/usr/bin/env python3
"""O handoff só sai com o gate aberto, e leva a matriz dentro."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import io, padrao, registry  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'x'}, {'id': 'RN-002', 'enunciado': 'y'}])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'a', 'deriva_de': 'RN-001'}])

    r = dk('handoff', '--projeto', str(raiz))
    if r.returncode == 0:
        errors.append('gate com bloqueio deveria reprovar')
    if 'cobertura' not in r.stdout:
        errors.append('o gate não listou o item que bloqueou')
    if 'dk entender' not in r.stdout:
        errors.append('o bloqueio não deu o comando que resolve')
    if list((raiz / padrao.destino('handoff')).glob('*.html')):
        errors.append('gate fechado e mesmo assim gerou o pacote')

    forcado = dk('handoff', '--projeto', str(raiz), '--matriz')
    if forcado.returncode != 0:
        errors.append('--matriz é só leitura e não deveria depender do gate')
    if 'REQ-001' not in forcado.stdout:
        errors.append('--matriz não emitiu a linha do requisito')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 3: Acrescentar o subcomando**

```python
def cmd_handoff(args) -> int:
    projeto = Path(args.projeto).resolve()

    if args.matriz:
        print(rastreabilidade.markdown(rastreabilidade.matriz(projeto)))
        return 0

    r = prontidao.avaliar(projeto)
    for i in r['itens']:
        marca = {'ok': '[x]', 'aviso': '[!]', 'bloqueio': '[ ]'}[i['estado']]
        print(f"{marca} {i['nome']}: {i['evidencia']}")
        if i['estado'] != 'ok':
            print(f"      resolve em `{i['resolve_em']}` — {i['comando']}")

    if not r['pronto']:
        print(f"\n{len(r['bloqueios'])} bloqueio(s) — o pacote de handoff "
              'não foi gerado.')
        return 1

    if r['avisos']:
        print(f"\n{len(r['avisos'])} aviso(s) — o pacote sai, com ressalva.")

    if not args.corpo:
        print('\ngate aberto. Rode de novo com --corpo <arquivo.md> para gerar '
              'o pacote.')
        return 0

    corpo = Path(args.corpo).read_text(encoding='utf-8')
    if '{{RASTREABILIDADE}}' in corpo:
        corpo = corpo.replace(
            '{{RASTREABILIDADE}}',
            rastreabilidade.markdown(rastreabilidade.matriz(projeto)))

    achados = entregaveis.validar('handoff', corpo)
    for a in achados:
        print(f"{a['id']}: {a['titulo']} — {a['evidencia']}")
    if [a for a in achados if a['impacto'] == 'alto']:
        print('o pacote não foi gerado.')
        return 1

    html = documento.montar('Handoff para Desenvolvimento', projeto.name,
                            corpo, {'Projeto': projeto.name,
                                    'Gerado em': _hoje()})
    pasta = padrao.destino('handoff')
    alvo = projeto / pasta / f'handoff-{_hoje_iso()}.html'
    reg = leitura.Registro()
    fontes = []
    if alvo.exists():
        reg.ler(alvo)
        fontes.append(alvo)
    op = ops.Operacao(projeto, escopo=[pasta], registro=reg, fontes=fontes)
    plano = op.planejar(alvo, html)
    print(f"{plano['acao']}: {plano['caminho']}")
    if not args.apply:
        print('simulação — nada foi gravado. Use --apply para aplicar.')
        return 0
    op.aplicar()
    print(f'gravado: {alvo.relative_to(projeto)}')
    return 0
```

Parser:

```python
    han = sub.add_parser('handoff', help='gate de prontidão e pacote de handoff')
    han.add_argument('--projeto', required=True)
    han.add_argument('--matriz', action='store_true',
                     help='só emite a matriz de rastreabilidade')
    han.add_argument('--corpo')
    han.add_argument('--apply', action='store_true')
    han.set_defaults(func=cmd_handoff)
```

- [ ] **Step 4: Rodar e commitar**

---

### Task 5: Porta, skills e agente da etapa `handoff`

**Files:**
- Create: `dk/skills/dk-handoff/SKILL.md`
- Create: `dk/skills/dk-handoff-pacote/SKILL.md`
- Create: `dk/skills/dk-handoff-duvida/SKILL.md`
- Create: `dk/agents/dk-handoff.md`

A `dk-handoff-duvida` porta a triagem do `sea-ux-dev-question-analyzer`: dúvida que chega
do desenvolvimento é classificada em requisito, regra, fluxo, visual, conteúdo, restrição
técnica, defeito documental ou solicitação de mudança — e cada classe volta para uma etapa
diferente do pipeline.

---

### Task 6: E2E — o handoff bloqueia e depois libera

**Files:**
- Test: `dk/tests/validate_ciclo_handoff.py`

O teste monta um projeto com furo, exige bloqueio, fecha o furo, e exige liberação.
É a prova de que o gate mede o estado e não uma flag.

---

## Cobertura da spec

Fecha o pipeline de seis etapas da seção 4.2 da spec e a decisão de orçamento de catálogo.

## Depois deste plano

1. Entregáveis de comunicação: manual, e-mail, apresentação, slide, guia
2. `modules/design-system/` — o resto do cruzamento DLS × Kit
3. Os demais módulos: git-workflow, liferay-migration, similar-analysis, lean-inception
4. Congelamento das duas bases antigas, com inspeção prévia dos sete clones
