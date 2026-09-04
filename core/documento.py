#!/usr/bin/env python3
"""Markdown → HTML canônico com a identidade da SEA.

Autocontido por decisão: fontes embutidas, zero requisição de rede. O entregável
vai para o cliente por e-mail, anexo ou pasta compartilhada, e precisa abrir igual
em qualquer lugar.

O conversor cobre o subconjunto de Markdown que os entregáveis usam — cabeçalho,
parágrafo, lista, tabela, negrito, itálico, código. O que ele não entende ele
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
        crua = linhas[i].strip()

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
                itens.append(_inline(re.sub(r'^[-*]\s+', '', linhas[i].strip())))
                i += 1
            saida.append('<ul>' + ''.join(f'<li>{x}</li>' for x in itens) + '</ul>')
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
