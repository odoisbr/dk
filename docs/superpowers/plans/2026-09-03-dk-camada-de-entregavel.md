# DK — Camada de entregável · Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fechar o furo mais claro do Kit — o documento formatado que vai para o cliente. O `dk` passa a produzir ata e documento de requisitos com a identidade visual da SEA, a partir do registro que a espinha já grava, com as regras editoriais viradas em validador.

**Architecture:** `core/padrao` define a estrutura canônica de projeto e os 12 entregáveis, portados do Kit. `core/marca` guarda os tokens da identidade — que, verificado, são os **mesmos** nas duas linhagens. `core/documento` converte Markdown em HTML canônico com a marca. O PDF é derivado opcional, com degradação anunciada. `core/entregaveis` carrega o contrato de cada tipo — as 7 seções obrigatórias da ata e suas regras editoriais — e reprova o que não cumpre.

**Tech Stack:** Python 3.9+ (stdlib apenas). PDF via renderizador detectado em runtime; ausência degrada anunciada.

**Spec:** `docs/superpowers/specs/2026-09-03-dk-consolidacao-design.md`
**Planos anteriores:** fundação e espinha · audit e repository intelligence

## Global Constraints

Valem todas as dos planos anteriores, e mais estas:

- **Nenhuma dependência obrigatória nova.** O community renderiza com pandoc, Chrome e PyMuPDF; no `dk` o HTML é canônico e não precisa de nenhum dos três. PDF só quando o renderizador existir, e a ausência é dita.
- **Tokens da marca não são inventados.** Eles vêm de `sea_brand.py`, e o teste compara com os valores reais.
- **Regra editorial que a skill enuncia, o validador cobra.** Regra escrita em prosa que ninguém verifica foi como o Kit chegou a ter `dry-run` citado zero vezes.

## Descoberta que orienta o porte

As duas linhagens **já compartilham a identidade visual**. Os tokens do `criar-documento-padrao`
do community e o `CORES` do `sea_brand.py` do Kit são a mesma paleta:

```
#009CC5 azul (preenchimento)   #019CC5 azul (texto)   #112428 tinta
#434343 corpo                  #666666 secundário     #BFBFBF régua
#D9D9D9 borda de célula
Fontes: Lato (corpo) · PT Sans Narrow (título)
```

A fusão não força nada: `core/marca.py` é a fonte única desses tokens, e tanto o HTML quanto o
PDF os consomem.

## Escopo

Entram neste plano os entregáveis que fecham o ciclo da espinha: **ata**, **documento de
requisitos** e **documento padrão** genérico. Ficam para o plano 4 os entregáveis de comunicação —
`sea-manual-uso`, `sea-email-entrega`, `sea-gerar-apresentacao`, `criar-slide`,
`criar-guia-de-skill` — porque dependem do mesmo pipeline e não do registro da espinha; entram
depois que o pipeline estiver provado.

Das 27 regras do Kit, entram as que a estrutura de projeto permite verificar: 1 (pastas
obrigatórias), 2 (nome canônico dos entregáveis), 4 (insumo × entregável) e 6 (bloco de validação).
As regras 7 a 17 são de protótipo e CSS, e entram com o módulo de protótipo.

---

### Task 1: Padrão de projeto e as regras estruturais

**Files:**
- Create: `dk/core/padrao.py`
- Test: `dk/tests/validate_padrao.py`

**Interfaces:**
- Produces: `core.padrao.PASTAS`, `core.padrao.ENTREGAVEIS`, `core.padrao.destino(chave) -> str`, `core.padrao.verificar(raiz) -> list[dict]`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""A estrutura canônica do projeto de design, e as regras que a cobram."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import padrao  # noqa: E402

errors = []

for pasta in ('0-apoio', '1-levantamento', '2-design', '3-entregaveis', 'registry'):
    if pasta not in padrao.PASTAS:
        errors.append(f'{pasta} deveria ser pasta canônica')

if len(padrao.ENTREGAVEIS) != 12:
    errors.append(f'esperados 12 entregáveis, há {len(padrao.ENTREGAVEIS)}')
for chave in ('briefing', 'visao', 'requisitos', 'ata', 'prototipo', 'handoff'):
    if chave not in padrao.ENTREGAVEIS:
        errors.append(f'entregável {chave} ausente')

if padrao.destino('ata') != '1-levantamento/atas':
    errors.append(f"destino da ata errado: {padrao.destino('ata')}")
if padrao.destino('requisitos') != '1-levantamento/requisitos':
    errors.append(f"destino de requisitos errado: {padrao.destino('requisitos')}")

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    achados = padrao.verificar(raiz)
    ids = {a['regra'] for a in achados}
    if 1 not in ids:
        errors.append('projeto vazio deveria reprovar a regra 1')
    for a in achados:
        if not a.get('evidencia'):
            errors.append(f'achado sem evidência: {a}')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    (raiz / '1-levantamento' / 'atas' / 'ata-2026-08-14.md').parent.mkdir(
        parents=True, exist_ok=True)
    (raiz / '1-levantamento' / 'atas' / 'ata-2026-08-14.md').write_text(
        '## 1. Identificação\n', encoding='utf-8')
    achados = padrao.verificar(raiz)
    if 1 in {a['regra'] for a in achados}:
        errors.append('projeto com todas as pastas não deveria reprovar a regra 1')

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    (raiz / '1-levantamento' / 'atas').mkdir(parents=True, exist_ok=True)
    (raiz / '1-levantamento' / 'atas' / 'Ata Reuniao FINAL v2.md').write_text(
        'x\n', encoding='utf-8')
    achados = padrao.verificar(raiz)
    if 3 not in {a['regra'] for a in achados}:
        errors.append('nome fora da convenção deveria reprovar a regra 3')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_padrao.py`
Expected: FAIL com `ImportError: cannot import name 'padrao'`

- [ ] **Step 3: Implementar `core/padrao.py`**

```python
#!/usr/bin/env python3
"""Estrutura canônica do projeto de design, portada do padrão do Kit.

`sea-design-template@2`: apoio recebe o que vem de fora, levantamento guarda o
markdown da fase, design guarda protótipo e styleguide, entregáveis guarda só o
PDF consolidado — saída gerada, nunca editada à mão.

As regras aqui são as que a estrutura permite verificar. As de protótipo e CSS
entram com o módulo de protótipo, onde há o que verificar."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

PASTAS = (
    '0-apoio',
    '1-levantamento',
    '1-levantamento/pesquisa',
    '1-levantamento/visao',
    '1-levantamento/requisitos',
    '1-levantamento/qualidade',
    '1-levantamento/atas',
    '1-levantamento/briefing',
    '1-levantamento/fluxos',
    '2-design',
    '3-entregaveis',
    'registry',
)

# chave → (pasta de destino, obrigatório no núcleo)
ENTREGAVEIS: Dict[str, tuple] = {
    'briefing': ('1-levantamento/briefing', True),
    'visao': ('1-levantamento/visao', True),
    'visao-produto': ('1-levantamento/visao', False),
    'escopo-comentado': ('1-levantamento/visao', True),
    'requisitos': ('1-levantamento/requisitos', True),
    'fluxos': ('1-levantamento/fluxos', True),
    'mc': ('1-levantamento/qualidade', True),
    'ata': ('1-levantamento/atas', True),
    'pendencias': ('registry', True),
    'historico': ('registry', True),
    'prototipo': ('2-design', True),
    'handoff': ('2-design', True),
}

# minúsculas, hífen, sem espaço e sem versão solta no nome
_CONVENCAO = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+$')
_EXCECOES = {'README.md', 'GUIA.md', 'CHANGELOG.md'}


def destino(chave: str) -> str:
    return ENTREGAVEIS[chave][0]


def verificar(raiz: Path) -> List[dict]:
    """Devolve os achados. Lista vazia é projeto em conformidade estrutural."""
    raiz = Path(raiz)
    achados = []

    faltando = [p for p in PASTAS if not (raiz / p).is_dir()]
    if faltando:
        achados.append({
            'regra': 1,
            'titulo': 'Pastas obrigatórias presentes',
            'evidencia': 'ausentes: ' + ', '.join(faltando),
            'impacto': 'alto',
        })

    for chave, (pasta, obrigatorio) in sorted(ENTREGAVEIS.items()):
        alvo = raiz / pasta
        if not obrigatorio or not alvo.is_dir():
            continue
        if not any(alvo.iterdir()):
            achados.append({
                'regra': 2,
                'titulo': 'Nome canônico dos entregáveis',
                'evidencia': f'{pasta}/ vazia — entregável "{chave}" sem arquivo',
                'impacto': 'medio',
            })

    for p in sorted(raiz.rglob('*.md')):
        if any(parte.startswith('.') for parte in p.relative_to(raiz).parts):
            continue
        if p.name in _EXCECOES:
            continue
        if not _CONVENCAO.match(p.name):
            achados.append({
                'regra': 3,
                'titulo': 'Convenção de nomes',
                'evidencia': f'{p.relative_to(raiz)}: fora do padrão '
                             'minúsculas-com-hífen',
                'impacto': 'baixo',
            })

    apoio = raiz / '0-apoio' / 'reunioes'
    atas = raiz / '1-levantamento' / 'atas'
    if apoio.is_dir() and atas.is_dir():
        insumos = list(apoio.glob('*.md')) + list(apoio.glob('*.txt'))
        if insumos and not any(atas.iterdir()):
            achados.append({
                'regra': 4,
                'titulo': 'Insumo × entregável',
                'evidencia': f'{len(insumos)} insumo(s) em 0-apoio/reunioes/ '
                             'sem ata correspondente em 1-levantamento/atas/',
                'impacto': 'alto',
            })

    for chave in ('visao', 'requisitos'):
        pasta = raiz / destino(chave)
        if not pasta.is_dir():
            continue
        for doc in pasta.glob('*.md'):
            texto = doc.read_text(encoding='utf-8', errors='replace')
            if 'Validação e Aprovação' not in texto:
                achados.append({
                    'regra': 6,
                    'titulo': 'Bloco "Validação e Aprovação" em Visão e Requisitos',
                    'evidencia': f'{doc.relative_to(raiz)}: bloco ausente',
                    'impacto': 'medio',
                })

    return achados
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_padrao.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/padrao.py tests/validate_padrao.py
git commit -m "feat: padrao de projeto e regras estruturais verificaveis"
```

---

### Task 2: Tokens da marca

**Files:**
- Create: `dk/core/marca.py`
- Create: `dk/templates/marca/` (fontes e logo, copiados do Kit)
- Test: `dk/tests/validate_marca.py`

**Interfaces:**
- Produces: `core.marca.CORES`, `core.marca.PILHA_CORPO`, `core.marca.PILHA_TITULO`, `core.marca.PILHA_MONO`, `core.marca.font_faces() -> str`, `core.marca.logo_svg() -> str`

- [ ] **Step 1: Copiar os ativos**

```bash
mkdir -p templates/marca/fonts
cp /Users/sea/SEA/plugins/sea-design-kit/templates/brand/fonts/*.ttf templates/marca/fonts/
cp /Users/sea/SEA/plugins/sea-design-kit/templates/brand/sea-logo-branco.svg templates/marca/
cp /Users/sea/SEA/plugins/sea-design-kit/templates/brand/sea-logo.png templates/marca/
```

- [ ] **Step 2: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""Os tokens da marca são os reais, não inventados.

Os valores abaixo foram lidos do sea_brand.py do Kit e dos tokens declarados na
skill criar-documento-padrao do community — as duas linhagens já concordavam."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import marca  # noqa: E402

errors = []

ESPERADAS = {
    'blue': '#009CC5', 'blue_text': '#019CC5', 'ink': '#112428',
    'body': '#434343', 'muted': '#666666', 'rule': '#BFBFBF',
    'cell_border': '#D9D9D9',
}
for chave, valor in ESPERADAS.items():
    if marca.CORES.get(chave) != valor:
        errors.append(f'CORES[{chave!r}] = {marca.CORES.get(chave)!r}, '
                      f'esperado {valor!r}')

if 'Lato' not in marca.PILHA_CORPO:
    errors.append('a pilha de corpo deveria começar em Lato')
if 'PT Sans Narrow' not in marca.PILHA_TITULO:
    errors.append('a pilha de título deveria começar em PT Sans Narrow')

faces = marca.font_faces()
if '@font-face' not in faces:
    errors.append('font_faces() não emite @font-face')
if 'base64' not in faces:
    errors.append('as fontes precisam ir embutidas: o HTML é autocontido')

logo = marca.logo_svg()
if '<svg' not in logo:
    errors.append('logo_svg() não devolveu SVG')

for ativo in ('templates/marca/fonts/Lato-Regular.ttf',
              'templates/marca/fonts/Lato-Bold.ttf',
              'templates/marca/fonts/PTSansNarrow-Bold.ttf',
              'templates/marca/sea-logo-branco.svg'):
    if not (RAIZ / ativo).exists():
        errors.append(f'{ativo} ausente')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 3: Rodar e confirmar que falha**

Run: `python3 tests/validate_marca.py`
Expected: FAIL com `ImportError`

- [ ] **Step 4: Implementar `core/marca.py`**

```python
#!/usr/bin/env python3
"""Identidade visual da SEA: fonte única dos tokens.

Verificado na auditoria: o `sea_brand.py` do Kit e os tokens da skill de documento
padrão do community declaram a mesma paleta e as mesmas fontes. Aqui elas existem
uma vez, e tanto o HTML quanto o PDF consomem daqui.

As fontes vão embutidas em base64 porque o entregável precisa ser autocontido:
um HTML que depende de fonte externa quebra quando sai do computador de quem gerou."""
from __future__ import annotations
import base64
from functools import lru_cache
from pathlib import Path

MARCA = Path(__file__).resolve().parents[1] / 'templates' / 'marca'

CORES = {
    'blue': '#009CC5',
    'blue_text': '#019CC5',
    'blue_dark': '#017A9B',
    'ink': '#112428',
    'body': '#434343',
    'muted': '#666666',
    'rule': '#BFBFBF',
    'cell_border': '#D9D9D9',
    'tint_1': '#F4FAFC',
    'tint_2': '#E3F1F6',
}

FACES = (
    ('Lato', 400, 'Lato-Regular.ttf'),
    ('Lato', 700, 'Lato-Bold.ttf'),
    ('PT Sans Narrow', 700, 'PTSansNarrow-Bold.ttf'),
)

PILHA_CORPO = ('"Lato", -apple-system, BlinkMacSystemFont, "Segoe UI", '
               'Roboto, Arial, sans-serif')
PILHA_TITULO = '"PT Sans Narrow", "Lato", "Arial Narrow", Arial, sans-serif'
PILHA_MONO = ('ui-monospace, SFMono-Regular, Menlo, Consolas, '
              '"Liberation Mono", monospace')


@lru_cache(maxsize=1)
def font_faces() -> str:
    blocos = []
    for familia, peso, arquivo in FACES:
        caminho = MARCA / 'fonts' / arquivo
        if not caminho.exists():
            continue
        dados = base64.b64encode(caminho.read_bytes()).decode('ascii')
        blocos.append(
            '@font-face{'
            f'font-family:"{familia}";font-weight:{peso};font-style:normal;'
            f'font-display:swap;'
            f'src:url(data:font/ttf;base64,{dados}) format("truetype");'
            '}')
    return '\n'.join(blocos)


@lru_cache(maxsize=2)
def logo_svg(branca: bool = True) -> str:
    caminho = MARCA / ('sea-logo-branco.svg' if branca else 'sea-logo.svg')
    if not caminho.exists():
        caminho = MARCA / 'sea-logo-branco.svg'
    return caminho.read_text(encoding='utf-8') if caminho.exists() else ''
```

- [ ] **Step 5: Rodar e confirmar que passa**

Run: `python3 tests/validate_marca.py`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add core/marca.py templates/marca tests/validate_marca.py
git commit -m "feat: tokens da marca SEA como fonte unica, com fontes embutidas"
```

---

### Task 3: Documento HTML canônico

**Files:**
- Create: `dk/core/documento.py`
- Test: `dk/tests/validate_documento.py`

**Interfaces:**
- Produces: `core.documento.markdown_para_html(texto) -> str`, `core.documento.montar(titulo, subtitulo, corpo_md, meta) -> str`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O HTML canônico: autocontido, com a marca, e com tabela de verdade."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import documento, marca  # noqa: E402

errors = []

CORPO = """## 1. Identificação

| Campo | Valor |
|---|---|
| Projeto | Convênios |
| Cliente | Sesc-DF |

## 2. Participantes

Texto com **negrito** e `código`.

- item um
- item dois
"""

html = documento.montar('Ata de Reunião', 'Convênios — Sesc-DF', CORPO,
                        {'cliente': 'Sesc-DF', 'data': '14/08/2026'})

if '<!doctype html>' not in html.lower():
    errors.append('sem doctype')
if 'Ata de Reunião' not in html:
    errors.append('título ausente')
if 'Convênios — Sesc-DF' not in html:
    errors.append('subtítulo ausente')
if marca.CORES['blue_text'] not in html:
    errors.append('a cor de título da marca não foi aplicada')
if '@font-face' not in html:
    errors.append('as fontes não foram embutidas')
if 'http://' in html or 'https://' in html:
    errors.append('o documento tem referência externa; deveria ser autocontido')

if '<table' not in html:
    errors.append('a tabela markdown não virou <table>')
if '<th' not in html:
    errors.append('a tabela sem cabeçalho')
if html.count('<td') < 4:
    errors.append('células de menos na tabela')
if '<strong>negrito</strong>' not in html:
    errors.append('negrito não convertido')
if '<code>código</code>' not in html:
    errors.append('código inline não convertido')
if '<ul>' not in html or html.count('<li>') != 2:
    errors.append('lista não convertida')
if '<h2' not in html:
    errors.append('cabeçalho de seção não convertido')

if '&' in CORPO:
    errors.append('fixture inválida')
escapado = documento.markdown_para_html('a < b & c')
if '&lt;' not in escapado or '&amp;' not in escapado:
    errors.append('HTML não escapado — risco de quebrar o documento')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_documento.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/documento.py`**

O conversor cobre o subconjunto de Markdown que os entregáveis usam: cabeçalho,
parágrafo, lista, tabela, negrito, itálico e código. O que ele não entende, ele
escapa e mostra como texto — nunca inventa marcação.

```python
#!/usr/bin/env python3
"""Markdown → HTML canônico com a identidade da SEA.

Autocontido por decisão: fontes embutidas, zero referência externa. O entregável
vai para o cliente por e-mail, anexo ou pasta compartilhada, e precisa abrir igual
em qualquer lugar.

O conversor cobre o subconjunto que os entregáveis usam. O que ele não entende ele
escapa e mostra como texto, em vez de inventar marcação."""
from __future__ import annotations
import html as _html
import re
from typing import List

from core import marca

_NEGRITO = re.compile(r'\*\*(.+?)\*\*')
_ITALICO = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)')
_CODIGO = re.compile(r'`([^`]+)`')


def _inline(texto: str) -> str:
    saida = _html.escape(texto, quote=False)
    saida = _CODIGO.sub(r'<code>\1</code>', saida)
    saida = _NEGRITO.sub(r'<strong>\1</strong>', saida)
    saida = _ITALICO.sub(r'<em>\1</em>', saida)
    return saida


def _linha_tabela(linha: str) -> List[str]:
    return [c.strip() for c in linha.strip().strip('|').split('|')]


def _separador(linha: str) -> bool:
    return bool(re.match(r'^\|?[\s:|-]+\|[\s:|-]*$', linha.strip())) \
        and '-' in linha


def markdown_para_html(texto: str) -> str:
    linhas = texto.splitlines()
    saida = []
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        crua = linha.strip()

        if not crua:
            i += 1
            continue

        m = re.match(r'^(#{1,4})\s+(.*)$', crua)
        if m:
            nivel = len(m.group(1))
            saida.append(f'<h{nivel}>{_inline(m.group(2))}</h{nivel}>')
            i += 1
            continue

        if crua.startswith('|') and i + 1 < len(linhas) \
                and _separador(linhas[i + 1]):
            cabecalho = _linha_tabela(crua)
            i += 2
            corpo = []
            while i < len(linhas) and linhas[i].strip().startswith('|'):
                corpo.append(_linha_tabela(linhas[i]))
                i += 1
            th = ''.join(f'<th>{_inline(c)}</th>' for c in cabecalho)
            trs = ''.join(
                '<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in linha_c)
                + '</tr>' for linha_c in corpo)
            saida.append(f'<table><thead><tr>{th}</tr></thead>'
                         f'<tbody>{trs}</tbody></table>')
            continue

        if re.match(r'^[-*]\s+', crua):
            itens = []
            while i < len(linhas) and re.match(r'^[-*]\s+', linhas[i].strip()):
                itens.append(_inline(re.sub(r'^[-*]\s+', '',
                                            linhas[i].strip())))
                i += 1
            saida.append('<ul>' + ''.join(f'<li>{x}</li>' for x in itens)
                         + '</ul>')
            continue

        paragrafo = []
        while i < len(linhas) and linhas[i].strip() \
                and not linhas[i].strip().startswith(('#', '|', '-', '*')):
            paragrafo.append(linhas[i].strip())
            i += 1
        if paragrafo:
            saida.append('<p>' + _inline(' '.join(paragrafo)) + '</p>')
        else:
            saida.append('<p>' + _inline(crua) + '</p>')
            i += 1

    return '\n'.join(saida)


def _css() -> str:
    c = marca.CORES
    return f"""
{marca.font_faces()}
*{{box-sizing:border-box}}
body{{margin:0;background:#fff;color:{c['body']};
  font-family:{marca.PILHA_CORPO};font-size:11pt;line-height:1.55}}
.folha{{max-width:19cm;margin:0 auto;padding:2.5cm 2cm}}
.capa{{border-bottom:3px solid {c['blue']};padding-bottom:18px;margin-bottom:28px}}
.capa h1{{font-family:{marca.PILHA_TITULO};font-size:24pt;line-height:1.1;
  color:{c['ink']};margin:0 0 6px}}
.capa .sub{{color:{c['muted']};font-size:12pt;margin:0}}
.capa dl{{display:grid;grid-template-columns:auto 1fr;gap:2px 14px;
  margin:16px 0 0;font-size:10pt;color:{c['muted']}}}
.capa dt{{font-weight:700}}
.capa dd{{margin:0}}
h1,h2,h3,h4{{font-family:{marca.PILHA_TITULO};color:{c['blue_text']};
  margin:26px 0 10px;line-height:1.2}}
h1{{font-size:24pt;border-bottom:1px solid {c['rule']};padding-bottom:6px}}
h2{{font-size:18pt}}
h3{{font-size:13pt;font-family:{marca.PILHA_CORPO};font-weight:700;
  color:{c['body']}}}
p{{margin:0 0 10px;text-align:justify}}
ul{{margin:0 0 12px;padding-left:20px}}
li{{margin:0 0 4px}}
code{{font-family:{marca.PILHA_MONO};font-size:9.5pt;
  background:{c['tint_1']};padding:1px 4px;border-radius:2px}}
table{{border-collapse:collapse;width:100%;margin:0 0 16px;font-size:10pt}}
th{{background:{c['blue']};color:#fff;text-align:left;
  font-family:{marca.PILHA_TITULO};font-weight:700;padding:7px 10px}}
td{{border:1px solid {c['cell_border']};padding:7px 10px;vertical-align:top}}
tbody tr:nth-child(even){{background:{c['tint_1']}}}
@media print{{.folha{{padding:0}}}}
"""


def montar(titulo: str, subtitulo: str, corpo_md: str, meta: dict) -> str:
    campos = ''.join(
        f'<dt>{_html.escape(str(k))}</dt><dd>{_html.escape(str(v))}</dd>'
        for k, v in (meta or {}).items())
    return (
        '<!doctype html>\n<html lang="pt-BR">\n<head>\n'
        '<meta charset="utf-8">\n'
        f'<title>{_html.escape(titulo)}</title>\n'
        f'<style>{_css()}</style>\n</head>\n<body>\n<div class="folha">\n'
        '<header class="capa">\n'
        f'<h1>{_html.escape(titulo)}</h1>\n'
        f'<p class="sub">{_html.escape(subtitulo)}</p>\n'
        f'<dl>{campos}</dl>\n'
        '</header>\n'
        f'{markdown_para_html(corpo_md)}\n'
        '</div>\n</body>\n</html>\n'
    )
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_documento.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/documento.py tests/validate_documento.py
git commit -m "feat: documento HTML canonico autocontido com a marca"
```

---

### Task 4: Contrato dos entregáveis

**Files:**
- Create: `dk/core/entregaveis.py`
- Test: `dk/tests/validate_entregaveis.py`

**Interfaces:**
- Produces: `core.entregaveis.CONTRATOS`, `core.entregaveis.validar(tipo, corpo_md) -> list[dict]`

As regras editoriais da ata, que a skill do community enunciava em prosa, viram
validador: 7 seções obrigatórias, sem coluna de status nos encaminhamentos,
sem marcador `[verificar]`/`[A CONFIRMAR]` sobrando, e nada de seção proibida.

- [ ] **Step 1: Escrever o teste que falha**

```python
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

parcial = COMPLETA.replace('## 7. Pontos em Aberto / Pendências', '## 7. Outra coisa')
ids = {a['id'] for a in entregaveis.validar('ata', parcial)}
if 'ATA-SECAO' not in ids:
    errors.append('seção faltando não foi detectada')

com_status = COMPLETA + '\n| Ação | Responsável | Prazo | Status |\n|---|---|---|---|\n'
ids = {a['id'] for a in entregaveis.validar('ata', com_status)}
if 'ATA-STATUS' not in ids:
    errors.append('coluna de status nos encaminhamentos não foi detectada')

com_marcador = COMPLETA + '\nFulana [verificar] disse que sim.\n'
ids = {a['id'] for a in entregaveis.validar('ata', com_marcador)}
if 'ATA-MARCADOR' not in ids:
    errors.append('marcador pendente não foi detectado')

com_proibida = COMPLETA + '\n## Próximos Passos\n\nx\n'
ids = {a['id'] for a in entregaveis.validar('ata', com_proibida)}
if 'ATA-PROIBIDA' not in ids:
    errors.append('seção proibida não foi detectada')

for a in entregaveis.validar('ata', parcial):
    if not a.get('evidencia'):
        errors.append(f'achado sem evidência: {a}')

vazio = entregaveis.validar('requisitos', '## 1. Contexto e objetivo\n')
if not any(a['id'] == 'REQ-EPICO' for a in vazio):
    errors.append('documento de requisitos sem épico deveria reprovar')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_entregaveis.py`
Expected: FAIL com `ImportError`

- [ ] **Step 3: Implementar `core/entregaveis.py`**

```python
#!/usr/bin/env python3
"""Contrato de cada entregável, cobrado por código.

A skill de ata do community enunciava estas regras em prosa — "sem coluna de
status", "decisão não é pendência", "a ata só fecha sem marcadores". Prosa que
ninguém verifica é intenção. Aqui elas reprovam."""
from __future__ import annotations
import re
from typing import Dict, List

CONTRATOS: Dict[str, dict] = {
    'ata': {
        'titulo': 'Ata de Reunião',
        'secoes': [
            'Identificação',
            'Participantes',
            'Resumo Executivo',
            'Tópicos Discutidos',
            'Principais Decisões',
            'Encaminhamentos e Ações',
            'Pontos em Aberto / Pendências',
        ],
        'proibidas': ['Próximos Passos', 'Observações Complementares'],
    },
    'requisitos': {
        'titulo': 'Documento de Requisitos de Design',
        'secoes': [
            'Contexto e objetivo',
            'Estrutura funcional',
            'Critérios de sucesso',
            'Priorização',
            'Dependências e premissas',
            'Validação e Aprovação',
        ],
        'proibidas': [],
    },
}

_MARCADORES = ('[verificar]', '[A CONFIRMAR]')


def _tem_secao(corpo: str, nome: str) -> bool:
    alvo = nome.lower()
    for linha in corpo.splitlines():
        if linha.startswith('#') and alvo in linha.lower():
            return True
    return False


def validar(tipo: str, corpo_md: str) -> List[dict]:
    contrato = CONTRATOS.get(tipo)
    if not contrato:
        return [{'id': 'TIPO-DESCONHECIDO',
                 'titulo': f'não há contrato para {tipo!r}',
                 'evidencia': f'tipos conhecidos: {", ".join(sorted(CONTRATOS))}',
                 'impacto': 'alto'}]

    achados = []

    for nome in contrato['secoes']:
        if not _tem_secao(corpo_md, nome):
            achados.append({
                'id': f'{tipo[:3].upper()}-SECAO',
                'titulo': f'seção obrigatória ausente: {nome}',
                'evidencia': f'nenhum cabeçalho contém "{nome}"',
                'impacto': 'alto',
            })

    for nome in contrato['proibidas']:
        if _tem_secao(corpo_md, nome):
            achados.append({
                'id': f'{tipo[:3].upper()}-PROIBIDA',
                'titulo': f'seção que não entra por padrão: {nome}',
                'evidencia': f'cabeçalho "{nome}" presente',
                'impacto': 'medio',
            })

    for marcador in _MARCADORES:
        if marcador in corpo_md:
            achados.append({
                'id': f'{tipo[:3].upper()}-MARCADOR',
                'titulo': f'marcador pendente no documento: {marcador}',
                'evidencia': f'{corpo_md.count(marcador)} ocorrência(s) de '
                             f'{marcador} — o documento só fecha sem marcador',
                'impacto': 'alto',
            })

    if tipo == 'ata':
        for linha in corpo_md.splitlines():
            if not linha.strip().startswith('|'):
                continue
            celulas = [c.strip().lower()
                       for c in linha.strip().strip('|').split('|')]
            if 'ação' in celulas and 'status' in celulas:
                achados.append({
                    'id': 'ATA-STATUS',
                    'titulo': 'encaminhamentos com coluna de status',
                    'evidencia': f'linha: {linha.strip()[:70]} — a ata é registro '
                                 'final; a tabela é Ação · Responsável · Prazo',
                    'impacto': 'medio',
                })
                break

    if tipo == 'requisitos' and not re.search(r'^#+.*\bE-\d', corpo_md, re.M):
        achados.append({
            'id': 'REQ-EPICO',
            'titulo': 'nenhum épico identificado',
            'evidencia': 'não há cabeçalho no padrão "Épico E-01"',
            'impacto': 'alto',
        })

    return achados
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_entregaveis.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/entregaveis.py tests/validate_entregaveis.py
git commit -m "feat: contrato dos entregaveis cobrado por validador"
```

---

### Task 5: `dk entregar` na CLI, com PDF opcional

**Files:**
- Modify: `dk/bin/dk`
- Test: `dk/tests/validate_entregar_cli.py`

**Interfaces:**
- Produces: `dk entregar --projeto <raiz> --tipo <ata|requisitos> --corpo <arquivo.md> [--pdf] [--apply]`

- [ ] **Step 1: Escrever o teste que falha**

```python
#!/usr/bin/env python3
"""O entregar valida o contrato antes de gerar, simula por padrão, e diz
quando não consegue gerar PDF."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import entregaveis, padrao  # noqa: E402

errors = []


def dk(*args):
    return subprocess.run([sys.executable, str(RAIZ / 'bin' / 'dk'), *args],
                          capture_output=True, text=True)


CORPO = '\n'.join(f'## {i}. {nome}\n\nconteúdo da seção.\n'
                  for i, nome in enumerate(
                      entregaveis.CONTRATOS['ata']['secoes'], start=1))

with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    for pasta in padrao.PASTAS:
        (raiz / pasta).mkdir(parents=True, exist_ok=True)
    corpo = raiz / '0-apoio' / 'corpo-ata.md'
    corpo.write_text(CORPO, encoding='utf-8')

    seco = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
              '--corpo', str(corpo))
    if seco.returncode != 0:
        errors.append(f'entregar falhou: {seco.stdout}{seco.stderr}')
    destino = raiz / padrao.destino('ata')
    if list(destino.glob('*.html')):
        errors.append('a simulação gravou o entregável')
    if 'cria' not in seco.stdout:
        errors.append('a simulação não mostrou o plano')

    ap = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
            '--corpo', str(corpo), '--apply')
    if ap.returncode != 0:
        errors.append(f'entregar --apply falhou: {ap.stdout}{ap.stderr}')
    gerados = list(destino.glob('*.html'))
    if not gerados:
        errors.append('--apply não gravou o HTML')
    else:
        html = gerados[0].read_text(encoding='utf-8')
        if '@font-face' not in html:
            errors.append('o entregável não é autocontido')
        if 'Identificação' not in html:
            errors.append('o corpo não entrou no documento')

    quebrado = raiz / '0-apoio' / 'corpo-quebrado.md'
    quebrado.write_text('## 1. Identificação\n', encoding='utf-8')
    r = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
           '--corpo', str(quebrado))
    if r.returncode == 0:
        errors.append('corpo fora do contrato deveria reprovar')
    if 'SECAO' not in r.stdout + r.stderr:
        errors.append('a reprovação não citou a regra violada')

    pdf = dk('entregar', '--projeto', str(raiz), '--tipo', 'ata',
             '--corpo', str(corpo), '--pdf', '--apply')
    saida = pdf.stdout + pdf.stderr
    gerou = list(destino.glob('*.pdf'))
    if not gerou and 'PDF' not in saida:
        errors.append('sem renderizador, a ausência do PDF precisa ser anunciada')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar e confirmar que falha**

Run: `python3 tests/validate_entregar_cli.py`
Expected: FAIL — `invalid choice: 'entregar'`

- [ ] **Step 3: Acrescentar o subcomando**

```python
def _renderizador_pdf():
    """Devolve o executável de PDF disponível, ou string vazia.

    Ausência não é erro: o HTML é o entregável canônico. O PDF é conveniência,
    e quando não dá para gerar, o dk diz — não falha em silêncio nem finge."""
    from shutil import which
    for candidato in ('chromium', 'chromium-browser', 'google-chrome',
                      'google-chrome-stable',
                      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        caminho = which(candidato) if '/' not in candidato else (
            candidato if Path(candidato).exists() else None)
        if caminho:
            return caminho
    return ''


def cmd_entregar(args) -> int:
    projeto = Path(args.projeto).resolve()
    corpo_md = Path(args.corpo).read_text(encoding='utf-8')

    achados = entregaveis.validar(args.tipo, corpo_md)
    bloqueios = [a for a in achados if a['impacto'] == 'alto']
    for a in achados:
        print(f"{a['id']}: {a['titulo']} — {a['evidencia']}")
    if bloqueios:
        print(f'{len(bloqueios)} bloqueio(s) — o entregável não foi gerado.')
        return 1

    contrato = entregaveis.CONTRATOS[args.tipo]
    meta = {'Projeto': projeto.name, 'Gerado em': _hoje()}
    html = documento.montar(contrato['titulo'], projeto.name, corpo_md, meta)

    pasta = padrao.destino(args.tipo)
    nome = f'{args.tipo}-{_hoje_iso()}.html'
    alvo = projeto / pasta / nome

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

    if args.pdf:
        renderizador = _renderizador_pdf()
        if not renderizador:
            print('PDF não gerado: nenhum renderizador encontrado. '
                  'O HTML é o entregável canônico e está completo.')
        else:
            destino_pdf = alvo.with_suffix('.pdf')
            r = subprocess.run(
                [renderizador, '--headless', '--disable-gpu',
                 f'--print-to-pdf={destino_pdf}', '--no-pdf-header-footer',
                 alvo.as_uri()],
                capture_output=True, text=True)
            if destino_pdf.exists():
                print(f'gravado: {destino_pdf.relative_to(projeto)}')
            else:
                print(f'PDF não gerado: o renderizador falhou '
                      f'({r.returncode}). O HTML está completo.')
    return 0
```

Acrescente os imports (`documento`, `entregaveis`, `padrao`, `subprocess`, `datetime`),
os auxiliares `_hoje()` e `_hoje_iso()`, e o parser:

```python
    ent = sub.add_parser('entregar', help='gera entregável formatado')
    ent.add_argument('--projeto', required=True)
    ent.add_argument('--tipo', required=True, choices=sorted(entregaveis.CONTRATOS))
    ent.add_argument('--corpo', required=True)
    ent.add_argument('--pdf', action='store_true',
                     help='tenta gerar PDF; ausência de renderizador é anunciada')
    ent.add_argument('--apply', action='store_true')
    ent.set_defaults(func=cmd_entregar)
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python3 tests/validate_entregar_cli.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add bin/dk tests/validate_entregar_cli.py
git commit -m "feat: dk entregar com contrato cobrado e PDF opcional anunciado"
```

---

### Task 6: Porta, skills e agente da etapa `entregar`

**Files:**
- Create: `dk/skills/dk-entregar/SKILL.md`
- Create: `dk/skills/dk-entregar-ata/SKILL.md`
- Create: `dk/skills/dk-entregar-requisitos/SKILL.md`
- Create: `dk/agents/dk-entregar.md`

- [ ] **Step 1 a 4:** criar os quatro arquivos seguindo o mesmo formato das etapas
  anteriores — porta sem portão, skills com o portão `Use quando a etapa entregar do
  DK estiver ativa`, `forma-da-saida` declarada, referência ao contrato de resposta, e o
  agente com a seção `## Skills desta etapa` enumerando as duas.

- [ ] **Step 5: Rodar a bateria**

Run: `python3 verificar.py`
Expected: tudo verde, com `validate_enumeracao` e `validate_portao_e_orcamento` cobrindo
as skills novas

- [ ] **Step 6: Commit**

```bash
git add skills/dk-entregar skills/dk-entregar-ata skills/dk-entregar-requisitos agents/dk-entregar.md
git commit -m "feat: porta, skills e agente da etapa entregar"
```

---

### Task 7: E2E — do insumo de reunião ao entregável formatado

**Files:**
- Test: `dk/tests/validate_ciclo_entregavel.py`

- [ ] **Step 1: Escrever o teste**

```python
#!/usr/bin/env python3
"""O ciclo completo: insumo → registro → entregável formatado e válido.

Fecha o arco que a espinha abriu. O que a espinha grava em registro é o que
alimenta o documento que vai para o cliente."""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import entregaveis, padrao, registry  # noqa: E402

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

    regras = registry.carregar(projeto, 'regras')
    if not regras:
        errors.append('a espinha não gravou regra')

    linhas = ['## 1. Identificação', '',
              '| Campo | Valor |', '|---|---|',
              '| Projeto | Convênios |', '| Data e horário | 14/08/2026, 10:00 às 11:00 |',
              '', '## 2. Participantes', '',
              '| Nome | Papel |', '|---|---|', '| Fulana | gestora |', '',
              '## 3. Resumo Executivo', '', 'Alinhamento sobre revogação de convênio.', '',
              '## 4. Tópicos Discutidos', '', '### Expiração', '', 'Contexto discutido.', '',
              '## 5. Principais Decisões', '']
    linhas += ['| Decisão | Contexto | Impacto |', '|---|---|---|']
    for reg in regras:
        linhas.append(f"| {reg['enunciado']} | {reg['fonte']} | a definir |")
    linhas += ['', '## 6. Encaminhamentos e Ações', '',
               '| Ação | Responsável | Prazo |', '|---|---|---|',
               '| Validar regra | Fulana | 20/08 |', '',
               '## 7. Pontos em Aberto / Pendências', '',
               'Nenhuma pendência registrada.', '']
    corpo = projeto / '0-apoio' / 'corpo-ata.md'
    corpo.write_text('\n'.join(linhas), encoding='utf-8')

    if entregaveis.validar('ata', corpo.read_text(encoding='utf-8')):
        errors.append('o corpo montado deveria passar no contrato da ata')

    e = dk('entregar', '--projeto', str(projeto), '--tipo', 'ata',
           '--corpo', str(corpo), '--apply')
    if e.returncode != 0:
        errors.append(f'entregar falhou: {e.stdout}{e.stderr}')

    gerados = list((projeto / padrao.destino('ata')).glob('*.html'))
    if not gerados:
        errors.append('nenhum entregável gerado')
    else:
        html = gerados[0].read_text(encoding='utf-8')
        for esperado in ('Ata de Reunião', 'Fulana', '@font-face', '<table'):
            if esperado not in html:
                errors.append(f'{esperado!r} ausente do entregável')
        for reg in regras:
            if reg['enunciado'][:30] not in html:
                errors.append('a regra do registro não chegou ao entregável')
                break

    achados = padrao.verificar(projeto)
    if 4 in {a['regra'] for a in achados}:
        errors.append('há insumo e ata; a regra 4 não deveria reprovar')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
```

- [ ] **Step 2: Rodar**

Run: `python3 tests/validate_ciclo_entregavel.py`
Expected: PASS

- [ ] **Step 3: Acrescentar ao portão de release**

```python
    ('ciclo do entregável', 'tests/validate_ciclo_entregavel.py'),
    ('contrato dos entregáveis', 'tests/validate_entregaveis.py'),
    ('padrão de projeto', 'tests/validate_padrao.py'),
```

- [ ] **Step 4: Conferir**

Run: `python3 verificar.py --release`
Expected: `portão de release aberto`, agora com 16 itens

- [ ] **Step 5: Commit**

```bash
git add tests/validate_ciclo_entregavel.py tests/validate_release_gate.py
git commit -m "test: ciclo do insumo ao entregavel formatado"
```

---

## Cobertura da spec

Este plano entrega a seção 5.1 parcial (ata, requisitos e documento padrão), a 5.2 inteira
(pipeline de renderização, com a decisão D7 implementada), e a parte das 27 regras que a
estrutura de projeto permite verificar.

## Depois deste plano

1. Entregáveis de comunicação: manual de uso, e-mail de entrega, apresentação, slide, guia
2. Etapa `entender` — cobertura, lacuna e léxico, portadas do Kit
3. `modules/design-system/` — cruzamento DLS × Kit, com as regras 7 a 17
4. Os demais módulos: git-workflow, liferay-migration, similar-analysis, lean-inception
5. Congelamento das duas bases antigas, com inspeção prévia dos sete clones
