---
name: dk-prototipar-ajuste
description: Executa um ajuste pontual no protótipo dentro de um changeset - declara o alvo, simula o diff, aplica só no que foi declarado. Use quando a etapa prototipar do DK estiver ativa e o pedido for mudar algo que já existe: espaçamento, cor, estado, variante, texto de uma tela ou componente.
argument-hint: "[o ajuste pedido]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
forma-da-saida: frase
---

# dk-prototipar-ajuste

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## A regra que existe por causa de um problema real

O time relatou: *"é solicitado um ajuste, mas ele faz o ajuste e faz mais coisas que
fogem do padrão inicial; se perde, mexe no que não tem que mexer, acaba quebrando o
que já foi construído."*

Por isso:

1. **Declare o alvo antes.** Abra o changeset com `--alvo` para cada caminho que muda.
2. **Mexa só nele.** O envelope de escrita recusa qualquer caminho fora do `affected` —
   não é disciplina, é exceção em tempo de execução.
3. **Se descobrir que precisa de mais, pare e abra outro changeset.** Não estique o
   `affected` do que já está aberto. Um changeset que cresce durante a execução é
   exatamente o comportamento que se quer impedir.
4. **Não conserte de passagem.** Violação de padrão que você encontrou e ninguém pediu
   para corrigir vira achado reportado, não commit silencioso.

## Procedimento

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/dk" prototipar --projeto <raiz> --verificar
"${CLAUDE_PLUGIN_ROOT}/bin/dk" prototipar --projeto <raiz> --changeset CS-00N \
  --titulo "<o pedido, em uma frase>" \
  --origem "<quem pediu, quando, onde>" \
  --alvo <caminho> [--alvo <caminho>...]
```

Depois, para cada arquivo do alvo: leia antes de escrever, simule, confira o diff, aplique.
Ao fim, rode `--verificar` de novo: o ajuste não pode ter introduzido violação nova.

## Regras

- Token e contrato de componente são a fonte. Se o ajuste pede mudança de cor, ela vai
  no token, não no CSS gerado.
- Diff maior que o pedido é sinal de que o alvo foi mal declarado — refaça o changeset.

## Resposta

Uma frase com o changeset, os arquivos escritos e o resultado do `--verificar` depois.
Se algo ficou fora, diga o que e por quê.
