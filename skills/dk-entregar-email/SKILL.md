---
name: dk-entregar-email
description: Escreve o e-mail formal de entrega ao cliente no estilo institucional da casa - assunto padronizado, resumo dos blocos entregues, status do ambiente, itens numerados com o ganho prático de cada um, e encerramento convidando à validação. Use quando a etapa entregar do DK estiver ativa e o entregável pedido for o e-mail de entrega.
argument-hint: "[projeto ou módulo entregue]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: documento
---

# dk-entregar-email

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As oito partes

1. **Assunto** — `(Entrega) <nome do projeto ou módulo>`. O validador cobra o padrão.
2. **Abertura** — "Prezados," mais a frase que formaliza a entrega.
3. **Resumo** — parágrafo curto, seguido de 3 a 6 itens com os grandes blocos.
4. **Status do ambiente** — homologação (para testar) ou produção (para usar). Sem isso o
   cliente não sabe se pode operar.
5. **Itens da entrega** — numerados `1.1`, `1.2`. Cada um: o que foi implementado, o
   contexto anterior quando fizer sentido, e o **ganho prático**.
6. **Encerramento** — convite a validar, esclarecer ou pedir ajuste.
7. **Dados de acesso** — só se fornecidos, e **sempre como marcador**.
8. **Fechamento** — "Em caso de dúvidas, estou à disposição." · "Atenciosamente," · nome.

## Regras que o validador cobra

- **Credencial nunca é transcrita.** Usuário e senha em corpo de e-mail é vazamento por
  desenho. O bloco existe com marcador — `Usuário: <informar>` — e quem envia preenche por
  canal seguro. Campo preenchido **bloqueia** a geração.
- Assunto fora do padrão `(Entrega) …` reprova.

## Regras de escrita

- **Não inventar** funcionalidade nem regra que não esteja no registro.
- Sem linguagem promocional. Descrição concreta do que foi entregue.
- Lista crua vira texto executivo agrupado em blocos coerentes, sem perder precisão.
- Entregue o e-mail **pronto para envio**, sem comentário extra em volta.

## Resposta

O caminho do arquivo e uma frase com quantos itens a entrega cobre e qual o ambiente.
