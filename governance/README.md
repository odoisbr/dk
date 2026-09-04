<div align="center">
  <img src="../assets/logo-community.png" alt="Sea Tecnologia · Design Community Knowledge Hub" width="520">
</div>

# Governance

Regras editoriais e de manutenção do repositório. Esta área define quem aprova, como versionar, como publicar e como manter o conteúdo saudável com o passar do tempo.

A governança do hub é executada manualmente pelos owners e automaticamente pelo agente [`curador-dac`](../AGENT.md). O guia humano completo está em [GUIA.md](../GUIA.md).

## Arquivos desta área

- [OWNERS.md](OWNERS.md) — **aprovadores únicos: Angelo Pimentel e Cecília Dib**.
- [versioning-policy.md](versioning-policy.md) — semver por pasta.
- [delivery-checklist.md](delivery-checklist.md) — checklist obrigatório de entrega de design.
- [gitlab-workflow.md](gitlab-workflow.md) — branches, commits, MR, labels e CI no GitLab.
- [gitlab-setup.md](gitlab-setup.md) — passo a passo de configuração do GitLab (branch protection, approval rules, roles).
- [git-templates.md](git-templates.md) — templates de commit, MR e squash commit; explica o `.gitmessage` e a pasta `.gitlab/merge_request_templates/`.
- [review-process.md](review-process.md) — fluxo de revisão e aprovação.
- [naming-conventions.md](naming-conventions.md) — nomenclatura de pastas, arquivos, branches e tokens.
- [input-contract.md](input-contract.md) — **contrato de entrada das skills** (draft): dependência por capacidade, não por arquivo fixo; procedência universal; degradação graciosa.
- [content-lifecycle.md](content-lifecycle.md) — estados `draft → review → published → archived`.

## Aqui entram

- Ownership por área.
- Fluxo de revisão e aprovação.
- Convenções editoriais.
- Regras de branch, commit e MR no GitLab.
- Regras de versionamento e arquivamento.

## Como propor mudança nesta área

Mudanças em `governance/` exigem:

1. ADR registrado em `docs/decisions/` explicando o porquê.
2. MR com pelo menos **2 aprovações**, sendo uma do owner de `governance/`.
3. Bump da `version` no frontmatter do arquivo alterado.

Detalhes em [review-process.md](review-process.md).
