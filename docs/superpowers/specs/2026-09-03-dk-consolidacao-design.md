# DK — consolidação do Design Kit e do Design Community em um plugin único

Data: 2026-09-03
Status: spec aprovada em desenho, aguardando plano de implementação
Origem: auditoria de 2026-09-03 (`apontamentos/AUDITORIA-CONSOLIDADA.md`,
`apontamentos/MATRIZ-DE-EVIDENCIAS.md`, 37 achados medidos)

---

## 1. Contexto

O `sea-design-kit` v0.9.0 tem 275 skills, 8 agentes orquestradores, 22 scripts
determinísticos, 68 schemas e 27 regras de validação. A auditoria mostrou que a
qualidade interna é alta — índice íntegro, descrições bem diferenciadas, nenhuma skill
órfã, hooks que respeitam a sessão — e que os problemas estão em entrega, contrato e
governança, não em conteúdo.

O `design-ai-community`, ancestral descontinuado, guarda capacidades que nunca chegaram ao
Kit: a camada de entregável formatado que vai para o cliente, um módulo de design system
completo (`sea-dls`) e 11 políticas de governança que o Kit não tem.

Três dores relatadas pelo time de design, cada uma com causa medida:

| Dor relatada | Causa medida |
|---|---|
| Requisitos existentes em documentos do projeto são ignorados e nunca atualizados, gerando furos | DK-104 — 62 skills escrevem em `decisions.json`, apenas 3 tocam em pendência: o Kit grava e não relê |
| No protótipo, pede-se um ajuste e ele faz além, foge do padrão e quebra o que já existe | DK-109 — `sea_prototype_tools.py` é um dos dois scripts sem escrita atômica; DK-003 — `dry-run` tem zero ocorrências no repositório |
| Prolixo: responde em parágrafos o que uma frase resolveria | DK-503 — a seção "Resposta final da Skill" está replicada 53×, 46× e 37×; 48% do corpo das skills é texto duplicado |

E uma quarta, de origem: **o Kit foi disponibilizado sem garantir o ciclo ponta a ponta.**

## 2. Objetivo

Consolidar, em **um plugin único e autônomo chamado `dk`**, tudo que agrega valor no
`sea-design-kit` e no `design-ai-community`, espelhando o processo real de design:

```
reunião → ata → regras de negócio → requisitos → entendimento da demanda
        → levantamento → entregáveis → protótipo → handoff
```

### Não-objetivos

- **Não mexer no `seakit`.** Nenhum arquivo dele é alterado, e o `dk` não depende dele.
- Não manter compatibilidade retroativa com `sea-design-kit`: o `dk` é repositório novo.
- Não criar dependência obrigatória nova.
- Não remover capacidade para reduzir números.

## 3. Decisões tomadas

| # | Decisão | Quem decidiu |
|---|---|---|
| D1 | O `dk` é um compilado autônomo com as melhores partes dos dois; o que está nele é dele, sem ligação com o `seakit` | usuário |
| D2 | O `dk` ganha a camada de entregável inteira, inclusive as que também existem no `seakit` | usuário |
| D3 | O `sea-dls` entra por cruzamento com o que o Kit já tem de melhor, para evitar retrabalho | usuário |
| D4 | Repositório novo | usuário |
| D5 | Sequência: espinha E2E provada primeiro, famílias depois. Estrutura: organizada por etapa do processo | usuário |
| D6 | As 50 skills `sea-git-*` e `sea-gitlab-*` entram como módulo próprio gated, fora da espinha | arquitetura |
| D7 | HTML canônico é a fonte do entregável; PDF é derivado opcional | arquitetura |
| D8 | `sea-design-kit` e `design-ai-community` são congelados no corte | arquitetura |

D8 é condição de D4: repositório novo sem congelar os dois antigos produz três bases vivas,
que é exatamente o que a auditoria proíbe. Congelado significa README apontando para o `dk`
e nenhum commit novo — o histórico permanece.

## 4. Arquitetura

### 4.1 Repositório e identidade

Repositório novo chamado **`dk`**. Por não ser o `sea-design-kit` renomeado, não há alias,
symlink, package alias nem migration layer a manter — o problema de identidade que a
auditoria tratou como decisão de compatibilidade desaparece por construção.

```
dk/
├── .claude-plugin/plugin.json     name: dk
├── llms.txt                       roteador de conhecimento
├── llms-full.txt                  contrato expandido + NON-NEGOTIABLE INVARIANTS
├── CLAUDE.md                      curto; referencia llms-full, não repete
├── bin/dk                         CLI determinística
├── core/
│   ├── scan/                      repository intelligence
│   ├── contracts/                 schemas, fonte única
│   └── validate/                  as regras, fonte única
├── skills/                        plano — exigência do formato de plugin
├── agents/                        um orquestrador por etapa
├── modules/
│   ├── design-system/             DLS mesclado com a família de tokens e Figma do Kit
│   └── git-workflow/              as 50 skills de git/gitlab, gated
├── governance/                    11 políticas recuperadas do ancestral
├── templates/
├── tests/
└── .gitlab/                       CODEOWNERS + template de MR
```

O formato de plugin exige `skills/` plano. A etapa não vira diretório: vira **prefixo de
nome** (`dk-levantar-*`, `dk-entregar-*`) mais o **portão na descrição**. É o mesmo
mecanismo que o Kit já usa com sucesso em `sea-liferay-*` e `sea-prototype-*` — aplicado
desde o nascimento, e não como correção posterior.

### 4.2 Pipeline e portas

```
dk audit          auditoria do projeto atual · gera o llms.txt do projeto
   ↓
dk levantar       reunião → ata → regras de negócio → requisitos
   ↓
dk entender       entendimento da demanda, lacunas, léxico, cobertura
   ↓
dk entregar       documento formatado que vai para o cliente
   ↓
dk prototipar     protótipo, tokens, componentes
   ↓
dk handoff        passagem para desenvolvimento
```

**Somente as seis portas ficam sem portão no catálogo.** Todas as demais skills declaram
`Use quando a etapa ⟨X⟩ do DK estiver ativa`. Custo estimado de catálogo fixo: ~1,5 KB,
contra 49.678 B (~12.420 tokens) do Kit hoje.

**Orçamento declarado: a soma das `description` sem portão não passa de 2.048 B.** É esse o
número que o teste de catálogo da seção 8 verifica. Passar do orçamento reprova o push.

`dk audit` é a primeira etapa por necessidade, não por gosto: é ela que lê o que já existe
no projeto — requisitos, documentos, decisões — e produz o estado que as etapas seguintes
são **obrigadas** a consultar. É o mecanismo que fecha a dor nº 1.

### 4.3 Regra de enumeração

**Cada agente de etapa enumera as skills da sua etapa.** Nenhuma skill depende do catálogo
para ser encontrada.

Esta regra existe porque a auditoria mediu (DK-506) que seis dos oito orquestradores do Kit
nomeiam uma única skill — o de Git nomeia 1 das 37, o de Liferay 1 das 46. É por isso que
as 191 skills sem portão do Kit **precisam** ficar sempre carregadas: sem enumeração, o
portão apagaria capacidade. No `dk`, enumeração e portão nascem juntos.

### 4.4 Invariantes executáveis

Invariante sem verificador é intenção. Foi assim que o Kit chegou a citar `dry-run` em zero
arquivos enquanto 78 falavam em sobrescrever.

| Invariante | Impede | Verificador |
|---|---|---|
| **LER-ANTES-DE-ESCREVER** | requisito existente ignorado e nunca atualizado | a skill declara `lê:` no front-matter; o validador reprova gravação de artefato cuja fonte não foi lida na sessão; hook PostToolUse compara o escrito com o registry |
| **ESCOPO DECLARADO** | o protótipo mexer no que não foi pedido | a operação declara o alvo antes de tocar; diff fora do alvo reprova |
| **DRY-RUN É O PADRÃO** | quebrar o que já foi construído | toda operação de escrita simula primeiro; `--apply` é explícito |
| **ESCRITA ATÔMICA** | arquivo truncado por interrupção | temp file no mesmo diretório + `os.replace`, sem exceção; teste que interrompe a escrita no meio |
| **CONTRATO DE RESPOSTA ÚNICO** | prolixidade | uma seção referenciada, nunca copiada; cada skill declara a forma da saída: frase, tabela ou documento |
| **MAP ANTES DE LER** | custo de contexto | nenhuma operação lê o repositório inteiro |
| **UMA INFORMAÇÃO, UMA FONTE** | versão divergente em quatro lugares | teste que reprova quando duas fontes discordam |

Os três primeiros são as três dores do time, viradas em código que reprova.

## 5. Escopo da consolidação

### 5.0 Destino das 275 skills do Kit

Nenhuma é descartada. A auditoria mediu que não há skill órfã (DK-507), duplicada (DK-504)
nem ambígua (DK-501) — não existe corte gratuito a fazer. Cada família ganha etapa ou
módulo:

| Origem no Kit | Qtd | Destino no `dk` |
|---|---:|---|
| `sea-transcricao-*`, `sea-triagem-demanda` | 4 | etapa `levantar` |
| `sea-ux-*` de intake, regras, requisitos, léxico | ~20 | etapa `levantar` |
| `sea-ux-*` de cobertura, lacuna, CSD, persona, jornada, escopo | ~45 | etapa `entender` |
| `sea-ux-*` de entregável, DoD/DoR, história, tarefa | ~17 | etapa `entregar` |
| `sea-prototype-*` | 38 | etapa `prototipar` |
| `sea-sync-*` | 8 | `modules/design-system/` |
| `sea-ux-handoff`, `sea-prototype-handoff` | 2 | etapa `handoff` |
| `sea-git-*`, `sea-gitlab-*` | 50 | `modules/git-workflow/` |
| `sea-liferay-*`, `sea-avaliar-viabilidade-liferay`, `sea-decompor-proposta-liferay` | 50 | `modules/liferay-migration/` |
| `sea-similar-*` | 35 | `modules/similar-analysis/` |
| `sea-lean-*` | 4 | `modules/lean-inception/` |
| `dk`, `sea-project-bootstrap`, `sea-dashboard-project-init`, `sea-task-fragmenter` | 4 | núcleo e etapa `audit` |

A distribuição exata das 82 `sea-ux-*` entre `levantar`, `entender` e `entregar` é trabalho
do plano de implementação, feito família a família com a tabela de-para. Os números acima
são a alocação proposta, não uma contagem final.

Módulo, aqui, tem o mesmo significado que já tem no Kit: manifesto próprio, orquestrador
próprio e skills gated. O Kit já opera assim com oito módulos declarados em `modules/`.

### 5.0.1 As 27 regras de validação

As 27 regras de `scripts/sea_project_tools.py` portam integralmente para `core/validate/`
como base — incluindo as regras 25 e 26, de cruzamento entre pendência e decisão, que foram
entregues em 02/09 e são o único cruzamento entre registros que existe hoje (DK-103). Sobre
essa base entram as regras novas dos invariantes da seção 4.4, uma por invariante.

### 5.1 Camada de entregável — entra inteira, do community

| Skill | Tamanho | Entrega |
|---|---|---|
| `sea-ata-reuniao` | 10.678 B | transcrição bruta → ata estruturada |
| `sea-ata` | 9.874 B | ata → documento final |
| `sea-documento-requisitos` | 7.846 B | requisitos classificados → Documento de Requisitos formal |
| `criar-documento-padrao` | 9.128 B | qualquer documento no padrão institucional |
| `sea-manual-uso` | 13.088 B | manual de uso do sistema entregue |
| `sea-email-entrega` | 6.130 B | e-mail formal de entrega |
| `sea-gerar-apresentacao` | 13.204 B | documento → apresentação |
| `criar-slide` | 6.509 B | slide no padrão |
| `criar-guia-de-skill` | 3.399 B | guia prático em slides |

Todas entram gated atrás de `dk entregar`.

**Sobre a duplicação com o `seakit`** (consequência aceita de D2): o portão a neutraliza. As
cópias do `dk` não competem no catálogo genérico — quem pedir "documento padrão" solto
continua caindo no `seakit`; quem estiver dentro do fluxo do `dk` cai na do `dk`. As três
skills homônimas (`criar-documento-padrao`, `criar-slide`, `criar-guia-de-skill`) diferem
hoje entre community e seakit em 2 linhas cada — a versão do `dk` parte da do community e
segue própria a partir do corte.

### 5.2 Motor de renderização (D7)

As skills do community renderizam com **pandoc, chromium e docx**. O Kit tem
`scripts/sea_navegavel.py`, 1.203 linhas, que gera documento navegável com visual SEA e
Mermaid pré-renderizado em SVG nativo — e cujo cabeçalho declara que faz isso justamente
para não precisar do Chromium.

Pipeline único do `dk`:

```
conteúdo (registry + markdown)
   → HTML canônico com marca SEA   (reusa sea_navegavel.py + sea_brand.py + templates/brand)
   → PDF                            (derivado, opcional, degrada anunciado)
```

O PDF só é exigido quando o entregável de fato vai para o cliente. O renderizador de PDF é
detectado; se ausente, o `dk` entrega o HTML e **diz** que não gerou PDF. Mantém
`dependencies_required: []` e segue o mesmo padrão já decidido para o `ast-grep`.

Consequência de custo: o passo de saída das nove skills precisa ser reescrito para este
pipeline. É porte, não cópia, e está contado no plano.

### 5.3 Design system — cruzamento DLS × Kit (D3)

O Kit é **mais largo**: 8 skills de round-trip com Figma (`sea-sync-*`), 8 de token
semântico e tema (`sea-prototype-token-*`), 7 de componente (`sea-prototype-component-*`,
incluindo acessibilidade, estados e variantes).

O `sea-dls` é **mais fundo**: 52 arquivos, 12 skills internas, 6 schemas versionados
(`component`, `token`, `changeset`, `flow`, `page`, `manifest`), um pacote Python com CLI,
um agente guardião e 3 hooks de validação.

Sobreposições, resolvidas pelo lado mais maduro:

| Capacidade | DLS | Kit | Fica com |
|---|---|---|---|
| analisar impacto | `analisar-impacto` | `sea-sync-analisar-impacto` | Kit |
| sincronizar / reconciliar | `sincronizar`, `reconciliar` | `sea-sync-roundtrip`, `sea-sync-conciliar-conflito` | Kit |
| extrair componentes | `extrair-componentes` | `sea-prototype-component-discovery` | Kit |
| criar componente | `criar-componente` | `sea-prototype-component-generator` | Kit |
| tokens | `token.schema.json` | 8 skills `sea-prototype-token-*` | Kit |
| validar | `validar` + 6 schemas | `sea-sync-auditar-ds` | **DLS** |

Entra do DLS o que o Kit não tem: os **6 schemas**, o **modelo de changeset** (no Kit é
apenas um guia em `docs/guia-v2-changeset.md`), os **validadores schema-driven**, o agente
**`design-state-guardian`** com seus 3 hooks, `criar-lib`, `criar-vitrine`, `extrair-dna`,
`extrair-icones`, e o **`manifest.yaml` como fonte única de configuração** — política que
responde diretamente à dor de "não atualiza os arquivos".

Resultado: módulo `modules/design-system/` com o Figma e os tokens do Kit, e o contrato, o
ciclo de vida e a validação do DLS.

### 5.4 Git e GitLab (D6)

As 37 skills `sea-git-*` e 13 `sea-gitlab-*` entram como `modules/git-workflow/`, gated,
fora da espinha. O `sea-gitlab-*` ganha o orquestrador que hoje não tem (DK-510); a família
inteira passa a ser alcançada por enumeração, não por catálogo.

### 5.5 Fora de escopo, com motivo

| Item | Motivo |
|---|---|
| `criar-desafio-cargo` | arte de recrutamento; não é processo de design |
| `analise-gitlab`, `sea-crawler-liferay` | já cobertos por `sea-gitlab-*` e `sea-liferay-*` |
| `archive` | sem função identificável |
| `sea-constituicao` | governança de agente; decisão à parte |

## 6. A fatia E2E

O primeiro entregável do `dk` não é uma família de skills. É uma **fatia vertical que fecha
o ciclo**:

```
insumo bruto de reunião → ata → regras de negócio → requisitos → entendimento
                        → Documento de Requisitos formatado
```

Com um teste automatizado que roda do início ao fim e afirma:

1. o artefato foi gerado;
2. o registry foi atualizado — não apenas o arquivo;
3. rodar de novo com o mesmo insumo **não duplica** nada (idempotência);
4. rodar com o insumo **alterado atualiza o requisito existente**, em vez de criar um novo
   ao lado.

A asserção 4 é o teste de regressão da dor nº 1. **Enquanto ela não passar, não existe
`dk`**, e nenhuma outra família entra. As demais entram uma por vez, cada uma atrás da
espinha já provada.

O teste roda sobre projeto de fixture versionado no próprio `dk`, sem depender de projeto de
cliente.

## 7. Governança e versionamento

Recuperados do ancestral, que já estão em disco em `design-ai-community/governance/`:

```
naming-conventions.md   versioning-policy.md   review-process.md
content-lifecycle.md    delivery-checklist.md  input-contract.md
OWNERS.md               gitlab-workflow.md     gitlab-setup.md
git-templates.md        README.md
```

Mais o `.gitlab/` com `CODEOWNERS` e `merge_request_templates`, que hoje existe só no
community. O `naming-conventions.md`, de 14/05, cobre a política de depreciação de nome de
skill que trava um pedido desde 04/08.

Versão em **fonte única gerada** a partir de `plugin.json`, com teste que reprova
divergência. O erro DK-002 não se repete por construção.

## 8. Testes e validação

| Camada | O que prova |
|---|---|
| E2E da espinha | as quatro asserções da seção 6 |
| Invariantes | um teste por invariante da seção 4.4 |
| Portão | nenhuma skill fora do portão da sua etapa |
| Enumeração | toda skill de uma etapa é alcançável a partir do agente da etapa |
| Versão | todas as fontes idênticas |
| Atomicidade | escrita interrompida no meio não corrompe o arquivo |
| Catálogo | soma das descriptions abaixo do orçamento declarado |

Todos rodam no `pre-push` com `core.hooksPath` ativo, e a ativação é verificada — não
depende de `git config` manual, que é o modo como o Kit chegou a ter a validação desligada
em todos os clones (DK-107).

## 9. Portão de release

```
[ ] teste E2E da espinha verde
[ ] core.hooksPath ativo e verificável
[ ] toda operação de escrita com dry-run e atômica
[ ] versão idêntica em todas as fontes
[ ] catálogo fixo medido, antes e depois
[ ] llms.txt e llms-full.txt
[ ] nenhuma skill fora do portão da sua etapa
[ ] governança recuperada e ativa
[ ] as duas bases antigas congeladas
```

O primeiro item impede repetir o erro de origem: **o `dk` não é publicado sem o ciclo
provado ponta a ponta.**

## 10. Migração e congelamento

1. O `dk` é construído em repositório novo, sem tocar nos dois antigos.
2. Cada capacidade portada é registrada em tabela de-para no próprio `dk`.
3. No corte, `sea-design-kit` e `design-ai-community` recebem README apontando para o `dk` e
   param de receber commits. O histórico permanece; nada é apagado.
4. Os clones obsoletos da linhagem — sete cópias em cinco versões (DK-106) — são
   inspecionados antes de qualquer arquivamento. O ancestral `sea-uiux-marketplace` tem 733
   arquivos não commitados que precisam ser olhados antes.

## 11. Riscos

| Risco | Mitigação |
|---|---|
| Repositório novo virar a terceira base viva | D8: congelamento é condição, não opção |
| Porte das 9 skills de entregável ser maior que o previsto | o passo de saída é reescrito uma vez, no pipeline comum da 5.2 |
| Cruzamento do DLS gerar retrabalho | a tabela da 5.3 decide cada sobreposição antes de começar |
| Espinha E2E atrasar a paridade | é deliberado: paridade sem ciclo provado foi o erro de origem |
| Perder capacidade ao aplicar o portão | enumeração antes do portão (4.3), com teste de alcançabilidade |
| Apagar clone com trabalho não salvo | inspeção obrigatória antes de arquivar (10.4) |

## 12. Rastreabilidade

| Decisão desta spec | Achado que a motiva |
|---|---|
| Portão em todas as skills, portas ungated | DK-004, DK-502 |
| Enumeração antes do portão | DK-506, DK-510 |
| Contrato de resposta único | DK-503 |
| LER-ANTES-DE-ESCREVER | DK-104 |
| ESCOPO DECLARADO + DRY-RUN | DK-003, DK-109 |
| ESCRITA ATÔMICA | DK-109 |
| Versão em fonte única | DK-002 |
| Governança recuperada | DK-110, DK-111 |
| `core.hooksPath` verificado | DK-107 |
| Congelar as bases antigas | DK-001, DK-106 |
| Camada de entregável | DK-009, ISSUE-018 |
| Sem dependência obrigatória nova | avaliação open source, teste de valor §24 |
