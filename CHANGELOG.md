# Changelog

## 1.0.0 — 04/09/2026

Primeira versão estável. O `dk` substitui o `sea-design-kit` como plugin de
processo de design da casa. Repositório novo, construído do zero a partir da
auditoria do Kit e do Design Community; nada foi copiado sem passar por teste.

### O que o plugin conduz

Sete etapas, cada uma com uma porta, um agente que enumera suas skills e um
comando determinístico na CLI:

| Etapa | Comando | Entrega |
|---|---|---|
| audit | `dk audit` | mapa do projeto, conformidade e `llms.txt` gerado |
| levantar | `dk levantar` | ata, regras de negócio e requisitos a partir do insumo da reunião |
| entender | `dk entender` | cobertura, consistência, lacunas, Lean Inception e similares |
| entregar | `dk entregar` | documento, apresentação, e-mail e manual formatados |
| prototipar | `dk prototipar` | changeset com alvo declarado, componentes e tokens |
| handoff | `dk handoff` | gate de prontidão, matriz de rastreabilidade e pacote |
| git | `dk git` | git local, projeto no GitLab, commit e merge request |

### Invariantes que o código sustenta

- Nenhum artefato é gravado sem que sua fonte tenha sido lida.
- Toda escrita declara escopo, simula e só então aplica; `--apply` é explícito.
- Escrita fora do escopo declarado levanta exceção e derruba a operação inteira.
- Requisito que já existe é atualizado por `origem_chave`, nunca duplicado.
- Todo achado declara `decidido_por`: `codigo` quando concluiu, `skill` quando
  apenas apontou candidato.
- Projeto vazio devolve "por começar" em vez de aprovar por ausência de dado.
- O registro canônico do projeto manda: `business-rules.json`,
  `requirements.json`, `sources.json`, `evidence.json`, `traceability.json`,
  `lean-inception.json`. O DK se adapta ao projeto, não o contrário.

### Custo de contexto

Oito portas sem portão de etapa, 2.325 B de catálogo fixo. O Kit anterior
carregava 49.678 B de `description` em toda sessão, porque 191 das 275 skills
não declaravam etapa.

### Verificação

50 validadores e 37 itens de portão de release, todos verdes. O ciclo foi
provado contra projeto real — 174 arquivos, 86 requisitos, 104 relações de
rastreabilidade —, inclusive o caminho de escrita, em cópia, sem criar registro
paralelo e sem colidir id.

### Fora desta versão

- Migração Liferay. As 50 skills `sea-liferay-*` do Kit não foram portadas.
- Publicação em remoto: o repositório ainda não tem `origin`.
