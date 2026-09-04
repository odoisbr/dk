# Contrato de resposta

Toda skill do `dk` responde segundo este contrato. Nenhuma skill copia este texto —
todas o referenciam, e declaram no front-matter a forma da sua saída:

```yaml
forma-da-saida: frase | tabela | documento
```

## frase

Uma a três frases. Nenhum preâmbulo, nenhuma recapitulação do pedido, nenhuma
lista de passos executados. Se a resposta cabe numa frase, ela é uma frase.

## tabela

Uma tabela com as colunas que o caso pede, precedida de no máximo uma frase de
contexto. Sem repetir em prosa o que a tabela já diz.

## documento

O artefato gravado, mais uma frase dizendo o caminho e o que mudou nele. O conteúdo
do documento não é repetido na resposta.

## Em qualquer forma

- Não descreva o que você vai fazer antes de fazer.
- Não anuncie chamada de ferramenta.
- Números e caminhos exatos; nada aproximado sem dizer que é estimativa.
- Divergência encontrada é reportada, não silenciada.
