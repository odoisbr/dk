# DK — Etapa `entender` · Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar ao `dk` a capacidade de detectar o que **falta** e o que **não fecha** — lacuna contra checklist, inconsistência entre requisitos, cobertura entre registro e entregável. É a etapa que ataca o furo na origem.

**Architecture:** `core/cobertura` cruza os registros entre si e com os entregáveis. `core/consistencia` implementa os seis tipos de inconsistência portados do community — quatro determinísticos, um parcial, um declaradamente da LLM. `core/lacunas` compara o registro contra um checklist de discovery versionado como dado, não como código. `dk entender` roda os três e emite um só relatório.

**Tech Stack:** Python 3.9+ (stdlib apenas).

**Spec:** `docs/superpowers/specs/2026-09-03-dk-consolidacao-design.md`
**Planos anteriores:** fundação e espinha · audit e repository intelligence · camada de entregável

## Global Constraints

Valem todas as dos planos anteriores, e mais estas:

- **O que a LLM decide, o código não finge decidir.** Conflito semântico entre requisitos exige leitura; o código marca o par como candidato e diz que a decisão é da skill. Fingir determinismo onde não há é pior que não ter.
- **Lacuna só existe com âncora no checklist.** "Seria bom saber" não vira achado. É a regra 1 de classificação do community, e ela entra como código.
- **O checklist é dado, não código.** Vive em `templates/checklist-discovery.json` e é editável sem tocar em Python.

## Reordenação em relação ao plano 3

O plano 3 declarou os entregáveis de comunicação — manual, e-mail, apresentação, slide, guia — como próximos. **Foram trocados por esta etapa**, por dois motivos: `entender` está na lista de etapas que o usuário descreveu, e é ela que ataca o furo relatado. O `upsert` do registro impede **duplicar** requisito; detectar lacuna é o que impede requisito **passar batido**. Os entregáveis de comunicação passam para o plano 5.

## O que é portado, e de onde

| Capacidade | Origem | Forma no `dk` |
|---|---|---|
| Seis tipos de inconsistência | `validar-consistencia-requisitos` (community) | `core/consistencia.py` |
| Urgência: bloqueia-avanço, resolve-antes-do-design, pode-postergar | idem | campo `urgencia` do achado |
| Checklist × transcrição, com 4 status | `identificar-lacunas` (community) | `core/lacunas.py` |
| Prioridade: crítica, importante, desejável | idem | campo `prioridade` do achado |
| Cobertura requisito → história → entregável | `sea-ux-requirement-coverage` (Kit) | `core/cobertura.py` |
| Matriz Certezas, Suposições e Dúvidas | `sea-ux-csd` (Kit) | skill `dk-entender-csd` |
| Léxico e termo ambíguo | `sea-ux-lexicon` (Kit) | skill `dk-entender-lexico` |

---

### Task 1: Matriz de cobertura

**Files:**
- Create: `dk/core/cobertura.py`
- Modify: `dk/core/espinha.py` (passa a delegar)
- Test: `dk/tests/validate_cobertura.py`

**Interfaces:**
- Produces: `core.cobertura.matriz(raiz) -> dict` com `regras_sem_requisito`, `requisitos_sem_regra`, `requisitos_sem_entregavel`, `totais`

A função `espinha.cobertura` continua existindo com a mesma assinatura, mas delega —
uma implementação só. Duas implementações da mesma conta é o defeito que esta auditoria
mediu no Kit anterior.

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""A cobertura cruza os registros entre si e com o entregável."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import cobertura, espinha, padrao, registry  # noqa: E402

errors = []

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)

    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001', 'enunciado': 'não expira sozinho'},
        {'id': 'RN-002', 'enunciado': 'gestor revoga'},
        {'id': 'RN-003', 'enunciado': 'órfã sem requisito'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'convênio permanece ativo', 'deriva_de': 'RN-001'},
        {'id': 'REQ-002', 'titulo': 'revogação manual', 'deriva_de': 'RN-002'},
        {'id': 'REQ-003', 'titulo': 'sem âncora', 'deriva_de': 'RN-999'},
        {'id': 'REQ-004', 'titulo': 'sem campo de origem'},
    ])

    m = cobertura.matriz(raiz)

    if m['regras_sem_requisito'] != ['RN-003']:
        errors.append(f"regras sem requisito: {m['regras_sem_requisito']}")
    if set(m['requisitos_sem_regra']) != {'REQ-003', 'REQ-004'}:
        errors.append(f"requisitos sem regra: {m['requisitos_sem_regra']}")
    if m['totais']['regras'] != 3 or m['totais']['requisitos'] != 4:
        errors.append(f"totais errados: {m['totais']}")
    if len(m['requisitos_sem_entregavel']) != 4:
        errors.append('sem entregável, todos os requisitos estão descobertos')

    destino = raiz / padrao.destino('requisitos')
    destino.mkdir(parents=True, exist_ok=True)
    (destino / 'requisitos-2026-09-04.html').write_text(
        '<p>REQ-001 e REQ-002 estão cobertos.</p>', encoding='utf-8')

    m2 = cobertura.matriz(raiz)
    if set(m2['requisitos_sem_entregavel']) != {'REQ-003', 'REQ-004'}:
        errors.append(f"após o entregável: {m2['requisitos_sem_entregavel']}")

    antigo = espinha.cobertura(
        [{'id': 'REQ-001', 'deriva_de': 'RN-001'}],
        [{'id': 'RN-001'}, {'id': 'RN-002'}])
    if antigo['regras_sem_requisito'] != ['RN-002']:
        errors.append('espinha.cobertura mudou de comportamento ao delegar')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_cobertura.py`
Expected: FAIL com `ImportError: cannot import name 'cobertura'`

- [ ] **Step 3: Implementar `core/cobertura.py`**

```python
#!/usr/bin/env python3
"""Cobertura: o que existe de um lado e não tem par do outro.

Três cruzamentos. Regra sem requisito é escopo que ninguém vai construir.
Requisito sem regra é escopo que ninguém pediu. Requisito sem entregável é
trabalho que o cliente não vai ver."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

from core import padrao, registry


def regras_sem_requisito(lista_requisitos: List[dict],
                         lista_regras: List[dict]) -> List[str]:
    cobertas = {q.get('deriva_de') for q in lista_requisitos}
    return [r['id'] for r in lista_regras if r['id'] not in cobertas]


def _texto_dos_entregaveis(raiz: Path) -> str:
    partes = []
    for chave in ('requisitos', 'visao', 'ata'):
        pasta = raiz / padrao.destino(chave)
        if not pasta.is_dir():
            continue
        for arq in sorted(pasta.iterdir()):
            if arq.suffix.lower() in ('.html', '.md'):
                partes.append(arq.read_text(encoding='utf-8', errors='replace'))
    return '\n'.join(partes)


def matriz(raiz: Path) -> Dict:
    raiz = Path(raiz)
    regras = registry.carregar(raiz, 'regras')
    requisitos = registry.carregar(raiz, 'requisitos')
    ids_regras = {r['id'] for r in regras}

    sem_regra = [q['id'] for q in requisitos
                 if q.get('deriva_de') not in ids_regras]

    texto = _texto_dos_entregaveis(raiz)
    sem_entregavel = [q['id'] for q in requisitos if q['id'] not in texto]

    return {
        'regras_sem_requisito': regras_sem_requisito(requisitos, regras),
        'requisitos_sem_regra': sem_regra,
        'requisitos_sem_entregavel': sem_entregavel,
        'totais': {
            'regras': len(regras),
            'requisitos': len(requisitos),
        },
    }
```

- [ ] **Step 4: Fazer `espinha.cobertura` delegar**

Substitua a função em `core/espinha.py`:

```python
def cobertura(lista_requisitos: List[Dict], lista_regras: List[Dict]) -> Dict:
    """Toda regra precisa de pelo menos um requisito. O que faltar é furo.

    A conta vive em `core.cobertura`; aqui é só a porta que a espinha usa.
    Duas implementações da mesma conta divergem — foi o que a auditoria mediu."""
    from core import cobertura as _cobertura
    faltando = _cobertura.regras_sem_requisito(lista_requisitos, lista_regras)
    return {
        'total_regras': len(lista_regras),
        'total_requisitos': len(lista_requisitos),
        'regras_sem_requisito': faltando,
    }
```

- [ ] **Step 5: Rodar os dois testes**

Run: `python3 tests/validate_cobertura.py && python3 tests/validate_espinha_unidades.py`
Expected: ambos PASS

- [ ] **Step 6: Commit**

```bash
git add core/cobertura.py core/espinha.py tests/validate_cobertura.py
git commit -m "feat: matriz de cobertura com uma implementacao so da conta"
```

---

### Task 2: Os seis tipos de inconsistência

**Files:**
- Create: `dk/core/consistencia.py`
- Test: `dk/tests/validate_consistencia.py`

**Interfaces:**
- Produces: `core.consistencia.TIPOS`, `core.consistencia.analisar(regras, requisitos) -> list[dict]`

Quatro tipos são decididos por código. O tipo 4 é parcial — o código acha a menção
sem definição, a skill julga se é integração real. O tipo 1, conflito semântico, é da
skill: o código marca o par como candidato e **diz** que não decidiu.

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""Os seis tipos de inconsistência, portados do community.

O que é determinístico o código decide. O que exige leitura, ele marca como
candidato e declara que não decidiu."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import consistencia  # noqa: E402

errors = []

if len(consistencia.TIPOS) != 6:
    errors.append(f'esperados 6 tipos, há {len(consistencia.TIPOS)}')
for nome in ('CONFLITO', 'DUPLICATA', 'ORFAO', 'REFERENCIA-INDEFINIDA',
             'NF-SEM-CRITERIO', 'REGRA-CIRCULAR'):
    if nome not in consistencia.TIPOS:
        errors.append(f'tipo {nome} ausente')

REGRAS = [
    {'id': 'RN-001', 'enunciado': 'o gestor revoga o convênio'},
    {'id': 'RN-002', 'enunciado': 'depende de RN-003 estar aprovada',
     'depende': ['RN-003']},
    {'id': 'RN-003', 'enunciado': 'depende de RN-002 estar aprovada',
     'depende': ['RN-002']},
]

REQUISITOS = [
    {'id': 'REQ-001', 'titulo': 'o gestor deve poder revogar o convênio',
     'deriva_de': 'RN-001'},
    {'id': 'REQ-002', 'titulo': 'o gestor deve poder revogar convênios',
     'deriva_de': 'RN-001'},
    {'id': 'REQ-003', 'titulo': 'sem âncora nenhuma', 'deriva_de': 'RN-404'},
    {'id': 'REQ-004', 'titulo': 'a interface deve ser rápida e intuitiva',
     'deriva_de': 'RN-001'},
    {'id': 'REQ-005', 'titulo': 'sincronizar com o Portal Transparência',
     'deriva_de': 'RN-001'},
]

achados = consistencia.analisar(REGRAS, REQUISITOS)
tipos = {a['tipo'] for a in achados}

for esperado in ('DUPLICATA', 'ORFAO', 'NF-SEM-CRITERIO', 'REGRA-CIRCULAR'):
    if esperado not in tipos:
        errors.append(f'{esperado} não foi detectado')

dup = [a for a in achados if a['tipo'] == 'DUPLICATA']
if dup and set(dup[0]['itens']) != {'REQ-001', 'REQ-002'}:
    errors.append(f"duplicata apontou o par errado: {dup[0]['itens']}")

orfao = [a for a in achados if a['tipo'] == 'ORFAO']
if orfao and orfao[0]['itens'] != ['REQ-003']:
    errors.append(f"órfão errado: {orfao[0]['itens']}")

nf = [a for a in achados if a['tipo'] == 'NF-SEM-CRITERIO']
if nf and nf[0]['itens'] != ['REQ-004']:
    errors.append(f"NF sem critério errado: {nf[0]['itens']}")

circ = [a for a in achados if a['tipo'] == 'REGRA-CIRCULAR']
if circ and set(circ[0]['itens']) != {'RN-002', 'RN-003'}:
    errors.append(f"ciclo errado: {circ[0]['itens']}")

for a in achados:
    if not a.get('evidencia'):
        errors.append(f'achado sem evidência: {a}')
    if a.get('urgencia') not in ('BLOQUEIA-AVANCO', 'RESOLVE-ANTES-DO-DESIGN',
                                'PODE-POSTERGAR'):
        errors.append(f"urgência inválida em {a['tipo']}: {a.get('urgencia')}")
    if 'decidido_por' not in a:
        errors.append(f"{a['tipo']} não diz quem decidiu")

conflitos = [a for a in achados if a['tipo'] == 'CONFLITO']
for a in conflitos:
    if a['decidido_por'] != 'skill':
        errors.append('conflito semântico não pode ser decidido por código')

limpo = consistencia.analisar(
    [{'id': 'RN-001', 'enunciado': 'x'}],
    [{'id': 'REQ-001', 'titulo': 'resposta em até 2 segundos',
      'deriva_de': 'RN-001'}])
if limpo:
    errors.append(f'conjunto sadio não deveria ter achado: {limpo}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_consistencia.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/consistencia.py`**

```python
#!/usr/bin/env python3
"""Os seis tipos de inconsistência entre requisitos, portados do community.

A divisão de trabalho é explícita em cada achado, no campo `decidido_por`:

    codigo  a verificação é determinística e o achado é conclusão
    skill   o código marca o candidato e a decisão exige leitura

Fingir determinismo onde não há é pior que não ter a checagem: produz achado
falso com cara de fato."""
from __future__ import annotations
import re
from typing import Dict, List

TIPOS = {
    'CONFLITO': 'dois requisitos que não podem ser verdadeiros ao mesmo tempo',
    'DUPLICATA': 'mesma necessidade expressa de formas diferentes',
    'ORFAO': 'requisito sem âncora rastreável',
    'REFERENCIA-INDEFINIDA': 'menciona entidade não definida em lugar nenhum',
    'NF-SEM-CRITERIO': 'requisito não-funcional sem critério mensurável',
    'REGRA-CIRCULAR': 'regra A depende de B, que depende de A',
}

_VAGOS = ('rápido', 'rapida', 'rápida', 'intuitiv', 'amigável', 'amigavel',
          'fácil', 'facil', 'simples de usar', 'performático', 'performatico',
          'escalável', 'escalavel', 'robusto', 'moderno', 'leve')

_MENSURAVEL = re.compile(
    r'\d+\s*(s|seg|segundo|ms|milissegundo|min|minuto|h|hora|%|kb|mb|gb|'
    r'usuário|usuario|requisi|transaç|transac)', re.I)

_PARADA = set('de da do das dos e o a os as um uma para com por em no na nos '
              'nas que se ao aos à às deve poder pode ser estar the'.split())


def _tokens(texto: str) -> set:
    return {t for t in re.findall(r'[a-zà-ú]{3,}', texto.lower())
            if t not in _PARADA}


def _similaridade(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _achado(tipo: str, itens: List[str], evidencia: str, urgencia: str,
            decidido_por: str) -> Dict:
    return {
        'tipo': tipo,
        'descricao': TIPOS[tipo],
        'itens': itens,
        'evidencia': evidencia,
        'urgencia': urgencia,
        'decidido_por': decidido_por,
    }


def analisar(regras: List[dict], requisitos: List[dict]) -> List[Dict]:
    achados = []
    ids_regras = {r['id'] for r in regras}

    # Tipo 3 — ÓRFÃO
    for q in requisitos:
        origem = q.get('deriva_de')
        if not origem or origem not in ids_regras:
            achados.append(_achado(
                'ORFAO', [q['id']],
                f"{q['id']} aponta para {origem!r}, que não existe em regras",
                'RESOLVE-ANTES-DO-DESIGN', 'codigo'))

    # Tipo 2 — DUPLICATA
    for i in range(len(requisitos)):
        for j in range(i + 1, len(requisitos)):
            a, b = requisitos[i], requisitos[j]
            s = _similaridade(a.get('titulo', ''), b.get('titulo', ''))
            if s >= 0.6:
                achados.append(_achado(
                    'DUPLICATA', [a['id'], b['id']],
                    f"similaridade {s:.0%} entre {a['id']} e {b['id']}: "
                    f"{a.get('titulo', '')[:40]!r} × {b.get('titulo', '')[:40]!r}",
                    'RESOLVE-ANTES-DO-DESIGN', 'codigo'))

    # Tipo 5 — NF-SEM-CRITÉRIO
    for q in requisitos:
        titulo = q.get('titulo', '')
        baixo = titulo.lower()
        vagos = [v for v in _VAGOS if v in baixo]
        if vagos and not _MENSURAVEL.search(titulo):
            achados.append(_achado(
                'NF-SEM-CRITERIO', [q['id']],
                f"{q['id']} usa {', '.join(sorted(set(vagos)))} sem número "
                f"nem unidade: {titulo[:60]!r}",
                'RESOLVE-ANTES-DO-DESIGN', 'codigo'))

    # Tipo 6 — REGRA-CIRCULAR
    grafo = {r['id']: list(r.get('depende') or []) for r in regras}
    vistos = set()
    for inicio in grafo:
        if inicio in vistos:
            continue
        caminho = []

        def desce(no):
            if no in caminho:
                ciclo = caminho[caminho.index(no):]
                achados.append(_achado(
                    'REGRA-CIRCULAR', sorted(set(ciclo)),
                    'ciclo de dependência: ' + ' → '.join(ciclo + [no]),
                    'BLOQUEIA-AVANCO', 'codigo'))
                return True
            if no not in grafo:
                return False
            caminho.append(no)
            for prox in grafo[no]:
                if desce(prox):
                    caminho.pop()
                    return True
            caminho.pop()
            vistos.add(no)
            return False

        desce(inicio)

    # Tipo 4 — REFERÊNCIA-INDEFINIDA (parcial: o código acha, a skill julga)
    definidos = ' '.join(
        [r.get('enunciado', '') for r in regras]
        + [q.get('titulo', '') for q in requisitos])
    for q in requisitos:
        for nome in re.findall(r'\b(?:Portal|Sistema|Módulo|Modulo|API)\s+'
                               r'([A-ZÀ-Ú][\wÀ-ú]+)', q.get('titulo', '')):
            if definidos.count(nome) <= 1:
                achados.append(_achado(
                    'REFERENCIA-INDEFINIDA', [q['id']],
                    f"{q['id']} menciona {nome!r}, que aparece uma vez só em "
                    'todo o registro — pode ser integração não especificada',
                    'PODE-POSTERGAR', 'skill'))

    # Tipo 1 — CONFLITO: candidato, nunca conclusão
    for i in range(len(requisitos)):
        for j in range(i + 1, len(requisitos)):
            a, b = requisitos[i], requisitos[j]
            s = _similaridade(a.get('titulo', ''), b.get('titulo', ''))
            if 0.3 <= s < 0.6 and a.get('deriva_de') != b.get('deriva_de'):
                achados.append(_achado(
                    'CONFLITO', [a['id'], b['id']],
                    f"{a['id']} e {b['id']} falam do mesmo assunto "
                    f"({s:.0%}) e vêm de regras diferentes — o código não "
                    'decide se há conflito; a skill lê e julga',
                    'PODE-POSTERGAR', 'skill'))

    return achados
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_consistencia.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/consistencia.py tests/validate_consistencia.py
git commit -m "feat: seis tipos de inconsistencia, com a divisao codigo x skill explicita"
```

---

### Task 3: Lacunas contra checklist

**Files:**
- Create: `dk/templates/checklist-discovery.json`
- Create: `dk/core/lacunas.py`
- Test: `dk/tests/validate_lacunas.py`

**Interfaces:**
- Produces: `core.lacunas.carregar_checklist() -> list[dict]`, `core.lacunas.analisar(raiz) -> list[dict]` com `status` em COBERTO/PARCIAL/AUSENTE e `prioridade` em CRITICA/IMPORTANTE/DESEJAVEL

- [ ] **Step 1: Criar o checklist como dado**

```json
{
  "versao": 1,
  "nota": "Checklist de discovery. Lacuna só existe com âncora aqui: 'seria bom saber' não vira achado. Editável sem tocar em código.",
  "itens": [
    {"id": "CL-01", "tema": "Contexto de negócio",
     "pergunta": "Quais os objetivos estratégicos, KPIs e desafios do cliente?",
     "prioridade": "CRITICA",
     "sinais": ["objetivo", "kpi", "meta", "indicador", "estratég"]},
    {"id": "CL-02", "tema": "Público-alvo",
     "pergunta": "Quais os segmentos, personas ou perfis de usuário?",
     "prioridade": "CRITICA",
     "sinais": ["usuário", "usuario", "persona", "perfil", "público", "publico", "segmento"]},
    {"id": "CL-03", "tema": "Escopo",
     "pergunta": "O que está dentro e o que está fora do escopo?",
     "prioridade": "CRITICA",
     "sinais": ["escopo", "fora de escopo", "não contempla", "nao contempla"]},
    {"id": "CL-04", "tema": "Restrições",
     "pergunta": "Quais as restrições de prazo, orçamento, tecnologia ou legais?",
     "prioridade": "IMPORTANTE",
     "sinais": ["restri", "prazo", "orçamento", "orcamento", "limita", "legal", "lgpd"]},
    {"id": "CL-05", "tema": "Integrações",
     "pergunta": "Com que sistemas o produto precisa conversar?",
     "prioridade": "IMPORTANTE",
     "sinais": ["integra", "api", "sistema externo", "portal", "sincroniz"]},
    {"id": "CL-06", "tema": "Dados",
     "pergunta": "Que dados existem, de onde vêm e há migração?",
     "prioridade": "IMPORTANTE",
     "sinais": ["dado", "migra", "base", "cadastro", "importa"]},
    {"id": "CL-07", "tema": "Permissões",
     "pergunta": "Quem pode fazer o quê? Há perfis de acesso?",
     "prioridade": "IMPORTANTE",
     "sinais": ["permiss", "perfil de acesso", "papel", "gestor", "administrador", "autoriza"]},
    {"id": "CL-08", "tema": "Estado atual",
     "pergunta": "Existe solução em uso hoje? O que ela faz e o que falha?",
     "prioridade": "DESEJAVEL",
     "sinais": ["hoje", "atualmente", "sistema atual", "legado", "planilha"]}
  ]
}
```

- [ ] **Step 2: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""Lacuna só existe com âncora no checklist, e vem com prioridade."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import lacunas, padrao, registry  # noqa: E402

errors = []

checklist = lacunas.carregar_checklist()
if len(checklist) < 5:
    errors.append(f'checklist com {len(checklist)} itens é curto demais')
for item in checklist:
    for campo in ('id', 'tema', 'pergunta', 'prioridade', 'sinais'):
        if campo not in item:
            errors.append(f'{item.get("id")}: sem campo {campo}')
    if item.get('prioridade') not in ('CRITICA', 'IMPORTANTE', 'DESEJAVEL'):
        errors.append(f'{item.get("id")}: prioridade inválida')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [])
    registry.gravar(raiz, 'requisitos', [])

    achados = lacunas.analisar(raiz)
    if len(achados) != len(checklist):
        errors.append(f'projeto vazio: {len(achados)} lacunas para '
                      f'{len(checklist)} itens de checklist')
    if any(a['status'] != 'AUSENTE' for a in achados):
        errors.append('projeto vazio deveria ter tudo AUSENTE')
    for a in achados:
        if not a.get('evidencia'):
            errors.append(f'lacuna sem evidência: {a}')
        if not a.get('id', '').startswith('L-'):
            errors.append(f'lacuna sem id no padrão L-XX: {a.get("id")}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [
        {'id': 'RN-001',
         'enunciado': 'o gestor com perfil de acesso revoga; permissão exigida'},
    ])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001',
         'titulo': 'o objetivo é reduzir o indicador de convênios vencidos',
         'deriva_de': 'RN-001'},
    ])
    achados = lacunas.analisar(raiz)
    por_id = {a['item']: a for a in achados}
    if por_id.get('CL-01', {}).get('status') == 'AUSENTE':
        errors.append('CL-01 tem sinal de objetivo/indicador; não é AUSENTE')
    if por_id.get('CL-07', {}).get('status') == 'AUSENTE':
        errors.append('CL-07 tem sinal de permissão; não é AUSENTE')
    if por_id.get('CL-06', {}).get('status') != 'AUSENTE':
        errors.append('CL-06 não tem sinal nenhum; deveria ser AUSENTE')

    criticas = [a for a in achados if a['prioridade'] == 'CRITICA'
                and a['status'] == 'AUSENTE']
    if not criticas:
        errors.append('deveria restar ao menos uma lacuna crítica ausente')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 3: Rodar e confirmar que falha**

Run: `python3 tests/validate_lacunas.py`
Expected: FAIL com `ImportError`

- [ ] **Step 4: Implementar `core/lacunas.py`**

```python
#!/usr/bin/env python3
"""Lacunas: o que o checklist prevê e o registro não tem.

A regra que o community fixou e aqui vira código: lacuna só existe com âncora no
checklist. "Seria bom saber" não entra. Por isso o checklist é dado versionado —
mudar o que se cobra é editar JSON, não Python.

O status é conservador: PARCIAL quando há sinal fraco, AUSENTE quando não há
nenhum. COBERTO exige sinal em mais de um registro, porque uma menção solta não
é entendimento."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from core import registry

CHECKLIST = Path(__file__).resolve().parents[1] / 'templates' / 'checklist-discovery.json'


def carregar_checklist() -> List[dict]:
    return json.loads(CHECKLIST.read_text(encoding='utf-8'))['itens']


def _corpus(raiz: Path) -> List[str]:
    partes = []
    for nome in ('regras', 'requisitos'):
        for item in registry.carregar(raiz, nome):
            partes.append(' '.join(str(v) for v in item.values()))
    return partes


def analisar(raiz: Path) -> List[Dict]:
    raiz = Path(raiz)
    partes = _corpus(raiz)
    texto = ' '.join(partes).lower()

    achados = []
    for i, item in enumerate(carregar_checklist(), start=1):
        ocorrencias = [s for s in item['sinais'] if s.lower() in texto]
        registros_com_sinal = sum(
            1 for p in partes if any(s.lower() in p.lower() for s in item['sinais']))

        if not ocorrencias:
            status = 'AUSENTE'
            evidencia = ('nenhum registro menciona: '
                         + ', '.join(item['sinais'][:4]))
        elif registros_com_sinal >= 2:
            status = 'COBERTO'
            evidencia = (f'{registros_com_sinal} registros mencionam '
                         + ', '.join(sorted(set(ocorrencias))[:3]))
        else:
            status = 'PARCIAL'
            evidencia = ('menção isolada a '
                         + ', '.join(sorted(set(ocorrencias))[:3])
                         + ' — uma menção não é entendimento')

        achados.append({
            'id': f'L-{i:02d}',
            'item': item['id'],
            'tema': item['tema'],
            'pergunta': item['pergunta'],
            'status': status,
            'prioridade': item['prioridade'],
            'evidencia': evidencia,
        })
    return achados
```

- [ ] **Step 5: Rodar e confirmar que passa**

Run: `python3 tests/validate_lacunas.py`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add templates/checklist-discovery.json core/lacunas.py tests/validate_lacunas.py
git commit -m "feat: lacunas ancoradas em checklist versionado como dado"
```

---

### Task 4: `dk entender` na CLI

**Files:**
- Modify: `dk/bin/dk`
- Test: `dk/tests/validate_entender_cli.py`

**Interfaces:**
- Produces: `dk entender --projeto <raiz> [--json]` — só leitura, não escreve

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O entender roda os três, num relatório só, e não escreve nada."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import padrao, registry  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    registry.gravar(raiz, 'regras', [{'id': 'RN-001', 'enunciado': 'o gestor revoga'}])
    registry.gravar(raiz, 'requisitos', [
        {'id': 'REQ-001', 'titulo': 'a tela deve ser rápida', 'deriva_de': 'RN-001'},
        {'id': 'REQ-002', 'titulo': 'sem âncora', 'deriva_de': 'RN-404'},
    ])

    antes = sorted(p.name for p in raiz.rglob('*') if p.is_file())
    r = dk('entender', '--projeto', str(raiz))
    if r.returncode != 0:
        errors.append(f'entender falhou: {r.stdout}{r.stderr}')
    depois = sorted(p.name for p in raiz.rglob('*') if p.is_file())
    if antes != depois:
        errors.append('entender escreveu no projeto; deveria ser só leitura')

    for esperado in ('ORFAO', 'NF-SEM-CRITERIO', 'AUSENTE', 'cobertura'):
        if esperado not in r.stdout:
            errors.append(f'{esperado!r} ausente do relatório')

    j = dk('entender', '--projeto', str(raiz), '--json')
    dados = json.loads(j.stdout)
    for chave in ('cobertura', 'consistencia', 'lacunas'):
        if chave not in dados:
            errors.append(f'--json sem a chave {chave}')
    if not dados['consistencia']:
        errors.append('nenhuma inconsistência detectada num conjunto que tem duas')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_entender_cli.py`
Expected: FAIL — `invalid choice: 'entender'`

- [ ] **Step 3: Acrescentar o subcomando**

```python
def cmd_entender(args) -> int:
    projeto = Path(args.projeto).resolve()
    cob = cobertura.matriz(projeto)
    inc = consistencia.analisar(registry.carregar(projeto, 'regras'),
                                registry.carregar(projeto, 'requisitos'))
    lac = lacunas.analisar(projeto)

    if args.json:
        print(json.dumps({'cobertura': cob, 'consistencia': inc,
                          'lacunas': lac}, ensure_ascii=False, indent=2))
        return 0

    print(f"cobertura: {cob['totais']['regras']} regras · "
          f"{cob['totais']['requisitos']} requisitos")
    for rotulo, chave in (('regra sem requisito', 'regras_sem_requisito'),
                          ('requisito sem regra', 'requisitos_sem_regra'),
                          ('requisito fora do entregável',
                           'requisitos_sem_entregavel')):
        if cob[chave]:
            print(f"  {rotulo}: {', '.join(cob[chave])}")

    if inc:
        print(f'\nconsistência: {len(inc)} achado(s)')
        for a in inc:
            quem = 'código decidiu' if a['decidido_por'] == 'codigo' \
                else 'candidato — a skill decide'
            print(f"  {a['tipo']} [{a['urgencia']}] ({quem})")
            print(f"    {a['evidencia']}")

    abertas = [a for a in lac if a['status'] != 'COBERTO']
    if abertas:
        print(f'\nlacunas: {len(abertas)} de {len(lac)} itens do checklist')
        for a in sorted(abertas, key=lambda x: x['prioridade']):
            print(f"  {a['id']} {a['tema']} [{a['status']}/{a['prioridade']}]")
            print(f"    {a['pergunta']}")
            print(f"    {a['evidencia']}")

    criticas = [a for a in lac
                if a['prioridade'] == 'CRITICA' and a['status'] == 'AUSENTE']
    bloqueios = [a for a in inc if a['urgencia'] == 'BLOQUEIA-AVANCO']
    print(f'\n{len(criticas)} lacuna(s) crítica(s) · '
          f'{len(bloqueios)} bloqueio(s) de avanço')
    return 0
```

E no `main()`:

```python
    ent2 = sub.add_parser('entender', help='cobertura, consistência e lacunas')
    ent2.add_argument('--projeto', required=True)
    ent2.add_argument('--json', action='store_true')
    ent2.set_defaults(func=cmd_entender)
```

Acrescente `cobertura`, `consistencia` e `lacunas` ao import de `core`.

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_entender_cli.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add bin/dk tests/validate_entender_cli.py
git commit -m "feat: dk entender com cobertura, consistencia e lacunas num relatorio"
```

---

### Task 5: Porta, skills e agente da etapa `entender`

**Files:**
- Create: `dk/skills/dk-entender/SKILL.md`
- Create: `dk/skills/dk-entender-lacunas/SKILL.md`
- Create: `dk/skills/dk-entender-consistencia/SKILL.md`
- Create: `dk/skills/dk-entender-csd/SKILL.md`
- Create: `dk/agents/dk-entender.md`

A `dk-entender-csd` porta a Matriz Certezas, Suposições e Dúvidas do Kit: é a skill que
impede opinião ser tratada como fato, e é o par humano da detecção automática.

- [ ] **Step 1 a 5:** criar os cinco arquivos no formato das etapas anteriores — porta sem
  portão, skills com o portão `Use quando a etapa entender do DK estiver ativa`,
  `forma-da-saida` declarada, referência ao contrato de resposta, e o agente com a seção
  `## Skills desta etapa` enumerando as três.

- [ ] **Step 6: Rodar a bateria e commitar**

```bash
python3 verificar.py
git add skills agents
git commit -m "feat: porta, skills e agente da etapa entender"
```

---

### Task 6: E2E — o furo é detectado

**Files:**
- Test: `dk/tests/validate_ciclo_entender.py`

O teste monta um projeto com um furo real — regra levantada sem requisito derivado — e
exige que o `dk entender` o encontre. É o outro lado do teste da espinha: aquele prova que
o requisito não duplica; este prova que o que falta aparece.

- [ ] **Step 1: Escrever o teste**

```python
#!/usr/bin/env python3
"""O furo é detectado: regra sem requisito, requisito sem entregável,
lacuna crítica em aberto."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import padrao, registry  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


with tempfile.TemporaryDirectory() as d:
    projeto = Path(d) / 'projeto'
    for pasta in padrao.PASTAS:
        (projeto / pasta).mkdir(parents=True, exist_ok=True)
    (projeto / '0-apoio' / 'reunioes').mkdir(parents=True, exist_ok=True)
    insumo = projeto / '0-apoio' / 'reunioes' / '2026-08-14-convenios.md'
    insumo.write_text(
        'Reunião 14/08 — Convênios\n'
        'Fulana (gestora): o convênio não expira sozinho, quem tira do ar é o gestor.\n'
        'Beltrano: e quando o prazo vence?\n',
        encoding='utf-8')

    r = dk('levantar', '--projeto', str(projeto), '--insumo', str(insumo), '--apply')
    if r.returncode != 0:
        errors.append(f'levantar falhou: {r.stdout}{r.stderr}')

    # o furo: uma regra é acrescentada sem requisito derivado
    regras = registry.carregar(projeto, 'regras')
    regras.append({'id': 'RN-099',
                   'enunciado': 'convênio revogado não pode ser reativado',
                   'fonte': 'ata 14/08', 'citacao': 'não pode voltar'})
    registry.gravar(projeto, 'regras', regras)

    saida = dk('entender', '--projeto', str(projeto), '--json')
    if saida.returncode != 0:
        errors.append(f'entender falhou: {saida.stdout}{saida.stderr}')
    dados = json.loads(saida.stdout)

    if 'RN-099' not in dados['cobertura']['regras_sem_requisito']:
        errors.append('o furo não foi detectado: RN-099 tem requisito?')

    if not dados['cobertura']['requisitos_sem_entregavel']:
        errors.append('sem entregável gerado, os requisitos deveriam aparecer '
                      'como fora do entregável')

    criticas = [a for a in dados['lacunas']
                if a['prioridade'] == 'CRITICA' and a['status'] == 'AUSENTE']
    if not criticas:
        errors.append('uma reunião de três falas não cobre o checklist inteiro; '
                      'deveria haver lacuna crítica')

    for a in dados['consistencia']:
        if a['decidido_por'] not in ('codigo', 'skill'):
            errors.append(f"achado sem dono de decisão: {a}")

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar, acrescentar ao portão e commitar**

```bash
python3 tests/validate_ciclo_entender.py
python3 verificar.py --release
git add tests/validate_ciclo_entender.py tests/validate_release_gate.py
git commit -m "test: o furo aparece — regra sem requisito, lacuna critica em aberto"
```

---

## Cobertura da spec

Este plano entrega a etapa `entender` do pipeline (seção 4.2) e a parte de 5.0 que aloca as
skills de cobertura, lacuna e léxico do Kit.

## Depois deste plano

1. Entregáveis de comunicação: manual de uso, e-mail de entrega, apresentação, slide, guia
2. `modules/design-system/` — cruzamento DLS × Kit, com as regras 7 a 17
3. Etapas `prototipar` e `handoff`
4. Os demais módulos: git-workflow, liferay-migration, similar-analysis, lean-inception
5. Congelamento das duas bases antigas, com inspeção prévia dos sete clones
