# DK — Entregáveis de comunicação · Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portar do Design Community os cinco entregáveis que falam com o cliente — manual de uso, e-mail de entrega e os três de apresentação — fechando a camada que o Kit nunca teve.

**Architecture:** Manual e e-mail entram no pipeline de documento que já existe: contrato em `core/entregaveis` mais skill. Os três de apresentação exigem uma forma de saída nova — `core/deck`, um renderizador 16:9 autocontido com os dez tipos de slide especificados pelo `criar-slide`.

**Spec:** `docs/superpowers/specs/2026-09-03-dk-consolidacao-design.md`

## Global Constraints

Valem as dos planos anteriores, e mais estas:

- **Uma identidade, não uma por documento.** O `sea-gerar-apresentacao` do community
  detecta "DNA visual" do conteúdo e monta uma paleta por documento. **Isso não é
  portado.** A marca é `core/marca.py`, e é uma só — inferir identidade por documento
  cria tantas fontes de verdade quantos forem os documentos.
- Os tokens de slide do community divergem dos do documento em quatro valores
  (`#0494bd` contra `#017A9B`, entre outros). Prevalece `core/marca.py`. Divergência de
  quatro hexadecimais não justifica uma segunda paleta.
- **Credencial nunca é inventada.** O e-mail de entrega tem bloco de acesso; sem dado
  fornecido, o bloco não existe. É regra do contrato, cobrada por validador.
- O deck é autocontido como o documento: fontes embutidas, zero requisição de rede.

## Escopo

| Entregável | Origem | Forma | Onde entra |
|---|---|---|---|
| Manual de uso | `sea-manual-uso` | documento | pipeline existente |
| E-mail de entrega | `sea-email-entrega` | texto pronto para envio | pipeline existente |
| Slide / deck | `criar-slide` | deck 16:9 | `core/deck.py` |
| Guia prático | `criar-guia-de-skill` | deck 16:9 | `core/deck.py` |
| Apresentação de documento | `sea-gerar-apresentacao` | deck 16:9 | `core/deck.py`, sem detecção de DNA |

---

### Task 1: Contratos de manual e e-mail

**Files:**
- Modify: `dk/core/entregaveis.py`
- Test: `dk/tests/validate_entregaveis.py`

O manual traz capa mais dez seções numeradas. O e-mail traz oito partes obrigatórias,
com duas regras que o validador cobra: assunto no padrão `(Entrega) …` e nenhum bloco
de acesso com credencial inventada.

- [ ] **Step 1: Acrescentar os contratos**

```python
    'manual': {
        'titulo': 'Manual de Uso',
        'secoes': [
            'Sumário', 'Introdução', 'O que o sistema faz',
            'O que o sistema NÃO faz', 'Perfis de acesso e responsabilidades',
            'Funcionalidades por perfil', 'Cenários de exceção',
            'Funcionalidades futuras', 'Orientações em caso de problemas',
            'Encerramento',
        ],
        'proibidas': [],
    },
    'email': {
        'titulo': 'E-mail de Entrega',
        'secoes': [
            'Assunto', 'Abertura', 'Resumo', 'Status do ambiente',
            'Itens da entrega', 'Encerramento',
        ],
        'proibidas': [],
    },
```

- [ ] **Step 2: Acrescentar as regras próprias do e-mail em `validar`**

```python
    if tipo == 'email':
        assunto = ''
        for linha in corpo_md.splitlines():
            if 'assunto' in linha.lower() and ':' in linha:
                assunto = linha.split(':', 1)[1].strip()
                break
        if assunto and not assunto.startswith('(Entrega)'):
            achados.append({
                'id': 'EMA-ASSUNTO',
                'titulo': 'assunto fora do padrão',
                'evidencia': f'{assunto[:60]!r} — o padrão é "(Entrega) <projeto>"',
                'impacto': 'medio',
            })
        placeholders = re.findall(
            r'(?:Usuário|Usuario|Senha|Password)\s*:\s*([^\n]*)', corpo_md)
        suspeitos = [p.strip() for p in placeholders
                     if p.strip() and not p.strip().startswith(('<', '[', '{'))]
        if suspeitos:
            achados.append({
                'id': 'EMA-CREDENCIAL',
                'titulo': 'bloco de acesso com credencial preenchida',
                'evidencia': 'credencial nunca é inventada nem transcrita para o '
                             'e-mail; deixe o campo como marcador ou remova o bloco',
                'impacto': 'alto',
            })
```

- [ ] **Step 3: Testes e commit**

---

### Task 2: Renderizador de deck 16:9

**Files:**
- Create: `dk/core/deck.py`
- Test: `dk/tests/validate_deck.py`

**Interfaces:**
- Produces: `core.deck.TIPOS`, `core.deck.LIMITES`, `core.deck.validar(slides) -> list[dict]`,
  `core.deck.montar(meta, slides) -> str`

Dez tipos, com os campos e limites que o `criar-slide` especifica. A altura do slide é
fixa: passar do limite não dá erro, o conteúdo **vaza** — então o overflow é avisado,
como o original fazia.

- [ ] **Step 1: Escrever o teste**

```python
#!/usr/bin/env python3
"""O deck 16:9: dez tipos, limite avisado, autocontido."""
from __future__ import annotations
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import deck, marca  # noqa: E402

errors = []

for tipo in ('capa', 'bullets', 'destaque', 'tabela', 'comparacao', 'metricas',
             'fluxo', 'imagem', 'split', 'secao', 'encerramento'):
    if tipo not in deck.TIPOS:
        errors.append(f'tipo de slide ausente: {tipo}')

SLIDES = [
    {'tipo': 'capa', 'titulo': 'Credenciamento', 'sub': 'SESC-DF',
     'kicker': 'Entrega', 'data': '04/09/2026'},
    {'tipo': 'bullets', 'titulo': 'O que entra',
     'bullets': ['Renovação de credencial', 'Mudança de tipo', 'Meus dados']},
    {'tipo': 'metricas', 'titulo': 'Números',
     'metricas': [{'valor': '86', 'rotulo': 'requisitos'},
                  {'valor': '18', 'rotulo': 'regras'}]},
    {'tipo': 'tabela', 'titulo': 'Perfis', 'colunas': ['Perfil', 'Pode'],
     'linhas': [['GEREL', 'aprovar'], ['Titular', 'solicitar']]},
    {'tipo': 'encerramento', 'titulo': 'Obrigado!'},
]

if deck.validar(SLIDES):
    errors.append(f'deck válido não deveria ter achado: {deck.validar(SLIDES)}')

sem_tipo = deck.validar([{'titulo': 'x'}])
if 'DECK-SEM-TIPO' not in {a['id'] for a in sem_tipo}:
    errors.append('slide sem tipo deveria reprovar')

desconhecido = deck.validar([{'tipo': 'carrossel', 'titulo': 'x'}])
if 'DECK-TIPO-DESCONHECIDO' not in {a['id'] for a in desconhecido}:
    errors.append('tipo inexistente deveria reprovar')

faltando = deck.validar([{'tipo': 'bullets', 'titulo': 'x'}])
if 'DECK-CAMPO' not in {a['id'] for a in faltando}:
    errors.append('bullets sem a lista deveria reprovar')

cheio = deck.validar([{'tipo': 'bullets', 'titulo': 'x',
                       'bullets': [f'item {i}' for i in range(12)]}])
ach = [a for a in cheio if a['id'] == 'DECK-OVERFLOW']
if not ach:
    errors.append('12 bullets passam do limite e o aviso não veio')
elif ach[0]['impacto'] != 'medio':
    errors.append('overflow avisa, não bloqueia')

html = deck.montar({'titulo': 'Credenciamento', 'cliente': 'SESC-DF'}, SLIDES)
if html.count('class="slide"') != len(SLIDES):
    errors.append(f'{html.count("class=\\"slide\\"")} slides para {len(SLIDES)}')
if '@font-face' not in html:
    errors.append('deck sem fontes embutidas')
if re.search(r'(?:src|href)\s*=\s*"https?://', html):
    errors.append('deck faz requisição externa')
if marca.CORES['blue'] not in html:
    errors.append('a marca não foi aplicada')
if '1280' not in html or '720' not in html:
    errors.append('o slide não declara a proporção 16:9')
if 'Credenciamento' not in html or 'SESC-DF' not in html:
    errors.append('capa sem título ou cliente')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2 a 4:** implementar `core/deck.py`, rodar, commitar.

---

### Task 3: `dk entregar --tipo apresentacao`

**Files:**
- Modify: `dk/bin/dk`
- Test: `dk/tests/validate_entregar_deck.py`

O corpo do deck vem de um JSON com `meta` e `slides`, não de Markdown — é a única
forma de saída do DK que não parte de prosa. A CLI detecta pela extensão do `--corpo`.

- [ ] **Step 1 a 4:** subcomando, teste, commit.

---

### Task 4: As cinco skills

**Files:**
- Create: `dk/skills/dk-entregar-manual/SKILL.md`
- Create: `dk/skills/dk-entregar-email/SKILL.md`
- Create: `dk/skills/dk-entregar-apresentacao/SKILL.md`
- Modify: `dk/agents/dk-entregar.md` (enumerar as novas)

Guia prático e slide compartilham a skill de apresentação: os três produzem deck, e a
diferença é o conteúdo, não o mecanismo. Três skills em vez de cinco, sem perder
capacidade — é a consolidação que a auditoria pede feita na origem.

---

### Task 5: E2E dos entregáveis de comunicação

**Files:**
- Test: `dk/tests/validate_ciclo_comunicacao.py`

Gera manual, e-mail e deck a partir de um projeto, e cobra: contrato respeitado,
autocontido, e credencial nunca preenchida.

---

## Depois deste plano

1. `modules/design-system/` — o resto do cruzamento DLS × Kit
2. Os quatro módulos: git-workflow, liferay-migration, similar-analysis, lean-inception
3. Congelamento das duas bases antigas, com inspeção prévia dos sete clones
