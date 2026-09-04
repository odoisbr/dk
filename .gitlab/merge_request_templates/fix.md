<!--
Template de MR para CORREÇÃO.
Use para typo, link quebrado, erro de descrição, ajuste cosmético.
Resultado esperado: bump PATCH na(s) pasta(s) afetada(s).
Regras: governance/gitlab-workflow.md + governance/git-templates.md.
-->

## O que estava errado

<!-- 1 a 2 frases descrevendo o erro encontrado -->

## O que foi corrigido

<!-- O que muda concretamente -->

- 
- 

## Como o erro foi descoberto

<!-- Reportado por X, encontrado em revisão, auditoria, etc. — útil para identificar padrões -->

## Versionamento (preenchido pelo curador-dac)

| Pasta | Versão anterior | Nova versão | Tipo de bump |
| --- | --- | --- | --- |
|  |  |  | patch |

> Entrada correspondente adicionada em [`[Unreleased]` do CHANGELOG.md](../../CHANGELOG.md) sob `### Fixed`.

## Como revisar

1. Confirme que o erro existia antes (ver linha original).
2. Confirme que a correção resolve sem efeitos colaterais.
3. Verifique se há outros lugares no repo com o mesmo erro.

## Checklist do autor

- [ ] Mudança é apenas correção (não adiciona feature)
- [ ] Não muda significado do conteúdo (apenas conserta)
- [ ] CHANGELOG.md atualizado em `[Unreleased]` → `Fixed`
- [ ] Tabela de versionamento no README.md atualizada (patch bump)
- [ ] Linha "Versão atual" do README da pasta atualizada

## Aprovadores obrigatórios

> Esta MR exige aprovação de Angelo Pimentel OU Cecília Dib. Ver [OWNERS.md](../../governance/OWNERS.md).

/assign_reviewer @angelo.pimentel
/assign_reviewer @cecilia.dib
/label ~"type:fix"

## Issues relacionadas

<!-- Closes #N | Refs #N -->
