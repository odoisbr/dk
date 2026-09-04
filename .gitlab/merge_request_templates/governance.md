<!--
Template de MR para MUDANÇA EM GOVERNANCE.
Use quando mexe em: governance/, AGENT.md, GUIA.md, CHANGELOG.md, .gitlab/, OWNERS.md.
Exige ADR + 2 aprovações.
Regras: governance/review-process.md + governance/gitlab-workflow.md.
-->

## Regra que muda

<!-- Identifique exatamente que regra/documento de governança esta MR altera -->

- Arquivo: 
- Seção: 
- Mudança em 1 frase: 

## Motivação

<!-- Por que essa mudança é necessária agora — incidente, gap, decisão de time -->

## Impacto

<!-- Como essa mudança afeta o fluxo de contribuição daqui pra frente -->

| Quem é afetado | Como |
| --- | --- |
| Autores | |
| Aprovadores (Angelo, Cecília) | |
| Agente curador-dac | |
| Pipeline / CI | |

## ADR vinculada

<!-- OBRIGATÓRIO para mudanças em governance/ -->

ADR: `docs/decisions/YYYY-MM-DD-titulo-da-decisao.md`

## Sincronização com outras camadas

Marque o que esta MR também atualiza para manter governance coerente:

- [ ] [OWNERS.md](../../governance/OWNERS.md) atualizado se a regra muda aprovadores
- [ ] [.gitlab/CODEOWNERS](../../.gitlab/CODEOWNERS) atualizado se a regra muda reviewers
- [ ] [AGENT.md](../../AGENT.md) atualizado se a regra muda o comportamento do curador
- [ ] [gitlab-setup.md](../../governance/gitlab-setup.md) atualizado se a regra muda configuração no GitLab
- [ ] [GUIA.md](../../GUIA.md) atualizado se a regra afeta o fluxo do designer
- [ ] Configuração no GitLab self-hosted reaplicada (separado, fora do MR)

## Versionamento (preenchido pelo curador-dac)

| Pasta | Versão anterior | Nova versão | Tipo de bump |
| --- | --- | --- | --- |
| governance/ |  |  | minor ou major |

> Entrada correspondente adicionada em [`[Unreleased]` do CHANGELOG.md](../../CHANGELOG.md) sob `### Changed` (ou `### Added` se nova regra).

## Como revisar

1. Leia a ADR vinculada.
2. Confirme que as outras camadas estão sincronizadas (CODEOWNERS, AGENT, setup, GUIA).
3. Verifique se a regra não conflita com outras seções de governance/.
4. Avalie o impacto operacional na dupla Angelo+Cecília.

## Aprovadores obrigatórios

> Mudança em `governance/` exige **2 aprovações**: Angelo Pimentel **E** Cecília Dib. Ver [OWNERS.md §3](../../governance/OWNERS.md#3-regras-de-aprovação).

/assign_reviewer @angelo.pimentel
/assign_reviewer @cecilia.dib
/label ~"area:governance" ~"needs-adr"

## Issues relacionadas

<!-- Closes #N | Refs #N -->
