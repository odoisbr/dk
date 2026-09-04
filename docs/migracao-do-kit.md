# Do `sea-design-kit` para o `dk`

## O que muda para quem usa

O ponto de entrada continua sendo uma frase. Onde antes se acionava uma skill
pelo apelido, agora se fala com a porta da etapa, e ela despacha:

| Você quer | Antes | Agora |
|---|---|---|
| auditar o projeto | `sea-audit-*` | `dk` ou `bin/dk audit --projeto <raiz>` |
| transformar reunião em requisito | `sea-ata-*`, `sea-req-*` | `bin/dk levantar` |
| saber o que falta | `sea-ux-*`, `sea-gap-*` | `bin/dk entender` |
| gerar documento para o cliente | `sea-doc-*` | `bin/dk entregar` |
| mexer no protótipo | `sea-prototype-*` | `bin/dk prototipar` |
| passar para desenvolvimento | `sea-handoff-*` | `bin/dk handoff` |
| commit e merge request | 50 skills `sea-git-*` e `sea-gitlab-*` | `bin/dk git` |

## Por que 275 skills viraram 30

A auditoria mostrou que a maior parte das skills do Kit era **passo de um
fluxo**, não capacidade: o fluxo de git tinha 50 delas, o de similares 35. Passo
não precisa de skill própria — precisa de procedimento dentro da skill da
capacidade. O que virou skill no `dk` é o que alguém pediria pelo nome.

As 191 skills sem portão de etapa também custavam contexto em toda sessão,
mesmo quando o trabalho não tinha nada a ver com elas. No `dk`, só as oito
portas ficam no catálogo fixo.

## O que o `dk` ganhou e o Kit não tinha

- Adaptador de registro: lê o esquema canônico que os projetos reais já usam, em
  vez de exigir arquivos próprios.
- Envelope de escrita com escopo declarado: ajuste pedido em um lugar não sai
  escrevendo em outro.
- Portão de prontidão que mede o estado do projeto, sem aprovação manual.
- Camada de entregável do Design Community: ata, documento padrão, apresentação,
  e-mail, manual.
- Contrato de componente com espelhamento em quatro camadas e tokens DTCG.
- Lean Inception cobrada contra o registro do projeto.
- Portão de release com 37 itens — o Kit foi publicado sem ciclo provado ponta a
  ponta, e é esse erro que o portão existe para não repetir.

## O que ficou de fora

**Migração Liferay.** As skills `sea-liferay-*`, `sea-avaliar-viabilidade-liferay`
e `sea-decompor-proposta-liferay` não foram portadas. Enquanto não forem, o
`sea-design-kit` segue disponível para esse caso específico.

**O `seakit` não foi tocado.** O que é dele continua nele, do jeito que funciona
hoje. O `dk` não aponta para o `seakit` nem depende dele.

## Convivência

O `dk` é repositório próprio, com nome próprio. Instalar um não desinstala o
outro, e os dois podem coexistir enquanto a equipe migra projeto a projeto. O
`dk` não lê nem escreve nada do Kit.
