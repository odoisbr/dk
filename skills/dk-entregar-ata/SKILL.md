---
name: dk-entregar-ata
description: Monta a ata de reunião no padrão SEA - sete seções obrigatórias, decisões separadas de pendências, encaminhamentos com responsável e prazo - e gera o documento formatado com a identidade visual da casa. Use quando a etapa entregar do DK estiver ativa e o entregável pedido for a ata.
argument-hint: "[caminho da ata estruturada ou do registro]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: documento
---

# dk-entregar-ata

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As sete seções

1. **Identificação** — tabela: projeto, cliente, data e horário num campo só, modalidade,
   objetivo. Campo sem dado no insumo é `Não informado na transcrição`, nunca inventado.
2. **Participantes** — tabela: nome, papel e organização de cada presente **confirmado**.
   Quem foi apenas citado vai em nota, não na tabela.
3. **Resumo Executivo** — um parágrafo. Não repete o detalhamento dos Tópicos.
4. **Tópicos Discutidos** — organizados **por assunto**, nunca em ordem cronológica.
5. **Principais Decisões** — tabela: decisão, contexto, impacto.
6. **Encaminhamentos e Ações** — tabela: ação, responsável, prazo. **Sem coluna de status.**
7. **Pontos em Aberto / Pendências** — o que ficou em aberto, cada um com responsável.

Seção que não se aplica é registrada como não aplicável, não omitida.

## Regras que o validador cobra

- Decisão, pendência e encaminhamento **nunca se misturam**. O que foi fechado vai só em
  Decisões e não reaparece como pendência.
- Cada fato aparece **uma vez só** no documento.
- A ata é registro final: sem coluna de status nos encaminhamentos.
- Nada de `[verificar]` ou `[A CONFIRMAR]` no documento fechado — resolva com o usuário e
  remova antes de gerar.
- Nada é inventado: decisão, responsável, prazo e número saem do insumo.

## Procedimento

1. Leia `registry/regras.json` e a ata anterior, se houver.
2. Monte o corpo em Markdown com as sete seções.
3. Rode `"${CLAUDE_PLUGIN_ROOT}/bin/dk" entregar --projeto <raiz> --tipo ata --corpo <arquivo.md>` em simulação.
   O comando reprova o que viola o contrato, citando a regra.
4. Corrija o que ele apontar e aplique com `--apply`.

## Resposta

O caminho do documento e uma frase com quantas decisões e pendências ele registra.
