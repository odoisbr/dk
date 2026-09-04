---
name: dk-prototipar-padrao
description: Verifica o protótipo contra as regras do padrão - cópia vendorizada de design system, rota de vitrine, framework CSS concorrente, API exclusiva do Bootstrap, variável de tema com valor cru e build desatualizado. Use quando a etapa prototipar do DK estiver ativa e a pergunta for se o protótipo está dentro do padrão.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-prototipar-padrao

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As regras verificadas

| Regra | O que reprova |
|---|---|
| 7 | cópia vendorizada do design system dentro do protótipo |
| 8 | protótipo sem rota de vitrine |
| 12 | framework CSS concorrente (Bootstrap, Tailwind, Bulma…) |
| 13 | API exclusiva do Bootstrap 5 (`data-bs-*`) |
| 14 | variável de tema recebendo valor cru em vez de `var(--token-…)` |
| 15 | saída compilada mais velha que a fonte SCSS — o build não rodou |

A regra 14 é a que mais escapa numa revisão humana: o resultado visual fica idêntico e a
ligação com o design system se perde em silêncio. É o começo do "foge do padrão".

## Procedimento

1. Rode `bin/dk prototipar --projeto <raiz> --verificar`.
2. Para cada achado, abra **só** o arquivo citado e confirme.
3. Proponha a correção pelo modelo canônico: valor cru vira token; framework concorrente
   sai; build desatualizado roda.

## Regras

- Correção de padrão é mudança: abre changeset próprio, com o alvo declarado.
- Não corrija de passagem dentro de um changeset que foi aberto para outra coisa.

## Resposta

Tabela com regra, arquivo, evidência e correção proposta. Uma frase com quantos achados
de impacto alto restam.
