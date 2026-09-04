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

    desc = scan.descartados(raiz)
    if not any('node_modules' in motivo for motivo in desc):
        errors.append(f'descartados() não nomeia o que ignorou: {desc}')


# Regressão: num projeto de credenciamento, o padrão `*credential*` engoliu sete
# specs de requisito. Documento de texto nunca é segredo por nome.
with tempfile.TemporaryDirectory() as d:
    raiz = Path(d)
    (raiz / 'specs').mkdir()
    for nome in ('credential-categories.md', 'f01_renew-credential.md',
                 'secrets-da-reuniao.md', 'notas-sobre-credenciais.txt'):
        (raiz / 'specs' / nome).write_text('conteúdo\n', encoding='utf-8')
    (raiz / 'credentials.json').write_text('{}', encoding='utf-8')
    (raiz / 'chave.pem').write_text('-----BEGIN\n', encoding='utf-8')

    caminhos = {e['caminho'] for e in scan.varrer(raiz)}
    for documento in ('specs/credential-categories.md',
                      'specs/f01_renew-credential.md',
                      'specs/secrets-da-reuniao.md',
                      'specs/notas-sobre-credenciais.txt'):
        if documento not in caminhos:
            errors.append(f'MATERIAL PERDIDO: {documento} foi descartado como segredo')
    for segredo in ('credentials.json', 'chave.pem'):
        if segredo in caminhos:
            errors.append(f'SEGREDO VAZADO: {segredo} entrou na varredura')

    motivos = scan.descartados(raiz)
    if not any('credentials.json' in m for m in motivos):
        errors.append('o descarte de segredo precisa nomear o arquivo, '
                      'ou falso positivo fica invisível')

fonte = (RAIZ / 'core' / 'scan.py').read_text(encoding='utf-8')
for proibida in ('read_text', 'read_bytes'):
    if proibida in fonte:
        errors.append(f'core/scan.py usa {proibida} — MAP ANTES DE LER violado')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
