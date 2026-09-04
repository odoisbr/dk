#!/usr/bin/env python3
"""Deck 16:9 autocontido, portado do `criar-slide` do Design Community.

Dez tipos de slide, cada um com campos obrigatórios e um limite seguro. A altura
é fixa em 720px: passar do limite **não dá erro**, o conteúdo vaza sobre o rodapé.
Por isso o overflow é avisado e não bloqueia — quem escreve decide se quebra em
mais slides.

Uma identidade, não uma por documento. O `sea-gerar-apresentacao` do community
detectava "DNA visual" do conteúdo e montava uma paleta por apresentação; isso não
foi portado. A marca é `core.marca`, e é uma só — inferir identidade por documento
cria tantas fontes de verdade quantos forem os documentos."""
from __future__ import annotations
import html as _html
import re
from typing import Dict, List

from core import marca

LARGURA, ALTURA = 1280, 720

# tipo → (campos obrigatórios, campo contado no limite, limite seguro)
TIPOS: Dict[str, tuple] = {
    'capa': (('titulo',), None, 0),
    'secao': (('titulo',), None, 0),
    'bullets': (('titulo', 'bullets'), 'bullets', 6),
    'destaque': (('titulo', 'q'), 'tags', 5),
    'tabela': (('titulo', 'colunas', 'linhas'), 'linhas', 6),
    'comparacao': (('titulo', 'esquerda', 'direita'), None, 0),
    'metricas': (('titulo', 'metricas'), 'metricas', 4),
    'fluxo': (('titulo', 'etapas'), 'etapas', 8),
    'imagem': (('src',), None, 0),
    'split': (('titulo', 'src', 'bullets'), 'bullets', 5),
    'encerramento': ((), None, 0),
}

LIMITES = {t: (campo, lim) for t, (_, campo, lim) in TIPOS.items() if campo}

_NEGRITO = re.compile(r'\*\*(.+?)\*\*')
_ITALICO = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)')


def _t(texto) -> str:
    """Escapa e aplica a marcação inline que o modelo aceita: negrito, itálico
    e quebra de linha."""
    saida = _html.escape(str(texto or ''), quote=False)
    saida = _NEGRITO.sub(r'<strong>\1</strong>', saida)
    saida = _ITALICO.sub(r'<em>\1</em>', saida)
    return saida.replace('\\n', '<br>').replace('\n', '<br>')


def validar(slides: List[dict]) -> List[Dict]:
    achados = []
    for i, s in enumerate(slides, start=1):
        tipo = s.get('tipo')
        if not tipo:
            achados.append({'id': 'DECK-SEM-TIPO', 'slide': i,
                            'titulo': 'slide sem tipo',
                            'evidencia': f'slide {i} não declara `tipo`',
                            'impacto': 'alto'})
            continue
        if tipo not in TIPOS:
            achados.append({'id': 'DECK-TIPO-DESCONHECIDO', 'slide': i,
                            'titulo': f'tipo {tipo!r} não existe',
                            'evidencia': 'tipos: ' + ', '.join(sorted(TIPOS)),
                            'impacto': 'alto'})
            continue
        obrigatorios, campo, limite = TIPOS[tipo]
        faltando = [c for c in obrigatorios if not s.get(c)]
        if faltando:
            achados.append({'id': 'DECK-CAMPO', 'slide': i,
                            'titulo': f'{tipo} sem campo obrigatório',
                            'evidencia': f'slide {i} ({tipo}): faltam '
                                         + ', '.join(faltando),
                            'impacto': 'alto'})
        if campo and limite and len(s.get(campo) or []) > limite:
            achados.append({
                'id': 'DECK-OVERFLOW', 'slide': i,
                'titulo': f'{tipo} passa do limite seguro',
                'evidencia': f'slide {i} ({tipo}): {len(s[campo])} itens em '
                             f'{campo}, limite seguro é {limite} — a altura é '
                             'fixa, o excedente vaza sobre o rodapé',
                'impacto': 'medio'})
    return achados


def _corpo(s: dict) -> str:
    tipo = s['tipo']
    kicker = f'<p class="kicker">{_t(s["kicker"])}</p>' if s.get('kicker') else ''
    titulo = f'<h2>{_t(s["titulo"])}</h2>' if s.get('titulo') else ''
    nota = f'<p class="nota">{_t(s["nota"])}</p>' if s.get('nota') else ''

    if tipo == 'capa':
        return (f'<div class="capa">{kicker}<h1>{_t(s.get("titulo"))}</h1>'
                f'<p class="sub">{_t(s.get("sub"))}</p>'
                f'<p class="data">{_t(s.get("data"))}</p></div>')
    if tipo == 'encerramento':
        return (f'<div class="capa fim"><h1>{_t(s.get("titulo") or "Obrigado!")}'
                f'</h1><p class="sub">{_t(s.get("sub"))}</p></div>')
    if tipo == 'secao':
        return (f'<div class="secao">{kicker}<h1>{_t(s.get("titulo"))}</h1>'
                f'<p class="sub">{_t(s.get("sub"))}</p></div>')
    if tipo == 'bullets':
        itens = ''.join(f'<li>{_t(b)}</li>' for b in s['bullets'])
        return f'{kicker}{titulo}<ul>{itens}</ul>{nota}'
    if tipo == 'destaque':
        tags = ''.join(f'<span class="tag">{_t(x)}</span>'
                       for x in (s.get('tags') or []))
        return (f'{kicker}{titulo}<p class="q">{_t(s["q"])}</p>'
                f'<p class="sub">{_t(s.get("sub"))}</p>'
                f'<div class="tags">{tags}</div>{nota}')
    if tipo == 'tabela':
        th = ''.join(f'<th>{_t(c)}</th>' for c in s['colunas'])
        tr = ''.join('<tr>' + ''.join(f'<td>{_t(c)}</td>' for c in linha)
                     + '</tr>' for linha in s['linhas'])
        return (f'{kicker}{titulo}<table><thead><tr>{th}</tr></thead>'
                f'<tbody>{tr}</tbody></table>{nota}')
    if tipo == 'comparacao':
        def lado(d):
            itens = ''.join(f'<li>{_t(x)}</li>' for x in (d.get('itens') or []))
            return (f'<div class="lado"><h3>{_t(d.get("titulo"))}</h3>'
                    f'<ul>{itens}</ul></div>')
        return (f'{kicker}{titulo}<div class="comp">{lado(s["esquerda"])}'
                f'{lado(s["direita"])}</div>{nota}')
    if tipo == 'metricas':
        cards = ''.join(f'<div class="m"><span class="v">{_t(m.get("valor"))}'
                        f'</span><span class="r">{_t(m.get("rotulo"))}</span></div>'
                        for m in s['metricas'])
        return f'{kicker}{titulo}<div class="metricas">{cards}</div>{nota}'
    if tipo == 'fluxo':
        etapas = ''.join(f'<div class="et">{_t(e)}</div>' for e in s['etapas'])
        por = int(s.get('por_linha') or 4)
        return (f'{kicker}{titulo}<div class="fluxo" '
                f'style="grid-template-columns:repeat({por},1fr)">{etapas}</div>{nota}')
    if tipo == 'imagem':
        return (f'<figure class="cheia"><img src="{_html.escape(s["src"])}" alt="">'
                f'<figcaption>{_t(s.get("legenda"))}</figcaption></figure>')
    if tipo == 'split':
        itens = ''.join(f'<li>{_t(b)}</li>' for b in s['bullets'])
        ordem = 'esquerda' if s.get('lado', 'esquerda') == 'esquerda' else 'direita'
        return (f'{kicker}{titulo}<div class="split {ordem}">'
                f'<img src="{_html.escape(s["src"])}" alt="">'
                f'<ul>{itens}</ul></div>{nota}')
    return f'{kicker}{titulo}{nota}'


def _css() -> str:
    c = marca.CORES
    return f"""
{marca.font_faces()}
*{{box-sizing:border-box}}
body{{margin:0;background:{c['tint_1']};font-family:{marca.PILHA_CORPO};
  color:{c['body']}}}
.slide{{width:{LARGURA}px;height:{ALTURA}px;background:#fff;margin:0 auto 22px;
  padding:64px 72px 58px;position:relative;overflow:hidden;
  box-shadow:0 1px 4px rgba(17,36,40,.14)}}
.slide h1{{font-family:{marca.PILHA_TITULO};font-size:56px;line-height:1.05;
  color:{c['ink']};margin:0 0 14px}}
.slide h2{{font-family:{marca.PILHA_TITULO};font-size:40px;line-height:1.1;
  color:{c['blue_text']};margin:0 0 26px}}
.slide h3{{font-family:{marca.PILHA_TITULO};font-size:24px;color:{c['ink']};
  margin:0 0 12px}}
.kicker{{font-family:{marca.PILHA_TITULO};font-size:16px;letter-spacing:.14em;
  text-transform:uppercase;color:{c['blue']};margin:0 0 10px}}
.sub{{font-size:24px;color:{c['muted']};margin:0 0 8px}}
.data{{font-size:18px;color:{c['muted']};margin:26px 0 0}}
.capa{{height:100%;display:flex;flex-direction:column;justify-content:center;
  border-left:10px solid {c['blue']};padding-left:40px}}
.capa.fim h1{{color:{c['blue_text']}}}
.secao{{height:100%;display:flex;flex-direction:column;justify-content:center;
  background:{c['tint_2']};margin:-64px -72px;padding:0 72px}}
ul{{margin:0;padding:0;list-style:none}}
li{{font-size:26px;line-height:1.4;margin:0 0 18px;padding-left:30px;position:relative}}
li::before{{content:"";position:absolute;left:0;top:.62em;width:14px;height:3px;
  background:{c['blue']}}}
.q{{font-size:44px;line-height:1.18;color:{c['ink']};font-weight:700;margin:0 0 16px}}
.tags{{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}}
.tag{{background:{c['tint_2']};color:{c['blue_text']};font-size:18px;
  padding:6px 14px;border-radius:3px}}
table{{border-collapse:collapse;width:100%;font-size:22px}}
th{{background:{c['blue']};color:#fff;text-align:left;padding:12px 16px;
  font-family:{marca.PILHA_TITULO};font-weight:700}}
td{{border:1px solid {c['cell_border']};padding:12px 16px}}
tbody tr:nth-child(even){{background:{c['tint_1']}}}
.comp{{display:grid;grid-template-columns:1fr 1fr;gap:44px}}
.comp .lado{{border-top:4px solid {c['blue']};padding-top:18px}}
.comp li{{font-size:22px;margin-bottom:12px}}
.metricas{{display:flex;gap:26px;margin-top:14px}}
.metricas .m{{flex:1;background:{c['tint_1']};border-left:6px solid {c['blue']};
  padding:26px 22px}}
.metricas .v{{display:block;font-family:{marca.PILHA_TITULO};font-size:64px;
  line-height:1;color:{c['ink']}}}
.metricas .r{{display:block;font-size:19px;color:{c['muted']};margin-top:10px}}
.fluxo{{display:grid;gap:16px;margin-top:10px}}
.fluxo .et{{background:{c['tint_1']};border-top:4px solid {c['blue']};
  padding:22px 18px;font-size:21px;line-height:1.35}}
.split{{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}}
.split.direita img{{order:2}}
.split img,.cheia img{{max-width:100%;max-height:460px;object-fit:contain}}
.cheia{{margin:0;height:100%;display:flex;flex-direction:column;
  justify-content:center;align-items:center}}
figcaption{{font-size:18px;color:{c['muted']};margin-top:14px}}
.nota{{position:absolute;left:72px;bottom:52px;font-size:16px;color:{c['muted']};
  margin:0}}
.rodape{{position:absolute;left:72px;right:72px;bottom:26px;display:flex;
  justify-content:space-between;align-items:center;font-size:14px;
  color:{c['muted']};border-top:1px solid {c['rule']};padding-top:10px}}
.serie{{position:absolute;top:30px;right:72px;font-size:14px;color:{c['muted']};
  letter-spacing:.1em;text-transform:uppercase}}
@media print{{
  body{{background:#fff}}
  .slide{{margin:0;box-shadow:none;page-break-after:always}}
  @page{{size:{LARGURA}px {ALTURA}px;margin:0}}
}}
"""


def montar(meta: dict, slides: List[dict]) -> str:
    serie = _t(meta.get('serie') or meta.get('cliente') or '')
    partes = []
    for i, s in enumerate(slides, start=1):
        capa = s.get('tipo') in ('capa', 'encerramento', 'secao', 'imagem')
        rodape = '' if capa else (
            f'<div class="rodape"><span>{_t(meta.get("titulo"))}</span>'
            f'<span>{i}</span></div>')
        topo = '' if capa or not serie else f'<div class="serie">{serie}</div>'
        partes.append(f'<section class="slide" data-tipo="{_html.escape(s.get("tipo", ""))}">'
                      f'{topo}{_corpo(s)}{rodape}</section>')
    return (
        '<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        f'<title>{_t(meta.get("titulo"))}</title>\n'
        f'<style>{_css()}</style>\n</head>\n<body>\n'
        + '\n'.join(partes) + '\n</body>\n</html>\n')
