<!--
Template de MR para MUDANÇA QUEBRA-COMPATIBILIDADE.
Use quando renomeia/move/remove conceito, reorganiza pasta, ou muda contrato externo.
Resultado esperado: bump MAJOR na(s) pasta(s) afetada(s) — exige ADR e 2 aprovações.
Regras: governance/gitlab-workflow.md + governance/versioning-policy.md.
-->

## O que muda

<!-- Em 1 parágrafo, o que esta MR muda no significado/estrutura existente -->

## Por que essa mudança quebra

<!-- Explique especificamente o que deixa de funcionar/valer com esta mudança -->

## Quem é afetado

<!-- Quais consumidores internos/externos do conteúdo precisam reagir -->

- 
- 

## Como migrar

<!-- Passo a passo claro: o que quem usava o antigo precisa fazer agora -->

1. 
2. 
3. 

## Período de transição

- **Marco de depreciação:** YYYY-MM-DD (quando o antigo entra em `deprecated`)
- **Marco de remoção:** YYYY-MM-DD (quando o antigo é arquivado/removido)
- **Stub de redirecionamento:** sim/não (se sim, por quanto tempo)

> Ver [content-lifecycle.md](../../governance/content-lifecycle.md) para regras de transição.

## ADR vinculada

<!-- OBRIGATÓRIO: link para a decisão registrada em docs/decisions/ -->

ADR: `docs/decisions/YYYY-MM-DD-titulo-da-decisao.md`

## Versionamento (preenchido pelo curador-dac)

| Pasta | Versão anterior | Nova versão | Tipo de bump |
| --- | --- | --- | --- |
|  |  |  | **major** |

> Entrada correspondente adicionada em [`[Unreleased]` do CHANGELOG.md](../../CHANGELOG.md) sob `### Changed`, `### Removed` ou `### Deprecated`.

## Como revisar

1. Leia a ADR vinculada e concorde com a motivação.
2. Verifique se o caminho de migração é executável.
3. Confirme que o período de transição é razoável para os afetados.
4. Valide que todos os pontos de referência ao conceito antigo foram atualizados ou mantidos como stub.

## Checklist do autor

- [ ] ADR criada em `docs/decisions/`
- [ ] Período de transição declarado
- [ ] Stubs de redirecionamento em conteúdo deprecated, se aplicável
- [ ] Todos os links internos que apontavam para o caminho antigo foram atualizados
- [ ] CHANGELOG.md atualizado com seção apropriada (`Changed` / `Removed` / `Deprecated`)
- [ ] Tabela de versionamento no README.md reflete bump major
- [ ] Linha "Versão atual" do README da pasta atualizada
- [ ] Comunicação prévia feita com os afetados

## Aprovadores obrigatórios

> Esta MR é **breaking-change** e exige **2 aprovações**: Angelo Pimentel **E** Cecília Dib. Ver [OWNERS.md §3](../../governance/OWNERS.md#3-regras-de-aprovação).

/assign_reviewer @angelo.pimentel
/assign_reviewer @cecilia.dib
/label ~"type:refactor" ~"breaking-change" ~"needs-adr"

## Issues relacionadas

<!-- Closes #N | Refs #N -->
