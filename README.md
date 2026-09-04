# dk

Processo de design ponta a ponta, da reunião com o cliente ao handoff para
desenvolvimento. Plugin de Claude Code, autônomo, sem dependência obrigatória —
Python 3.9 e biblioteca padrão.

Substitui o `sea-design-kit`. O de-para está em
[docs/migracao-do-kit.md](docs/migracao-do-kit.md).

## Instalação

```
/plugin marketplace add /caminho/para/dk
/plugin install dk@dk
```

Para instalar a partir deste repositório, clone e aponte para a branch `dk`:

```bash
git clone git@gitlab.seatecnologia.com.br:design/sea-design-kit.git dk
cd dk && git checkout dk
```

Depois `/plugin marketplace add <caminho do clone>` e `/plugin install dk@dk`.

## As sete etapas

Cada etapa tem uma porta (a skill que o Claude encontra sozinho), um agente que
enumera as skills dela e um comando determinístico na CLI.

| Etapa | Comando | O que entrega |
|---|---|---|
| audit | `dk audit --projeto <raiz>` | mapa do projeto, conformidade e `llms.txt` gerado |
| levantar | `dk levantar --projeto <raiz> --insumo <ata>` | regras de negócio e requisitos a partir da reunião |
| entender | `dk entender --projeto <raiz>` | cobertura, consistência, lacunas, Lean Inception e similares |
| entregar | `dk entregar --projeto <raiz> --tipo <t>` | documento, apresentação, e-mail e manual formatados |
| prototipar | `dk prototipar --projeto <raiz>` | changeset com alvo declarado, componentes e tokens |
| handoff | `dk handoff --projeto <raiz>` | portão de prontidão, matriz de rastreabilidade e pacote |
| git | `dk git --projeto <raiz>` | git local, projeto no GitLab, commit e merge request |

Instalado, a CLI vive em `${CLAUDE_PLUGIN_ROOT}/bin/dk`, e é assim que as skills
a chamam — o diretório de trabalho é sempre o projeto do cliente, não o plugin.
Trabalhando dentro deste repositório, `bin/dk` resolve igual.

Na conversa, nada disso precisa ser decorado: diga o que quer, e a porta `dk`
escolhe a etapa.

## O que ele garante

- **Nada é gravado sem `--apply`.** O padrão é simular e imprimir o que mudaria.
- **Escrita fora do escopo declarado derruba a operação.** Um ajuste pedido em um
  lugar não sai mexendo em outro — é o envelope de escrita, com exceção.
- **Nenhum artefato é gravado sem que sua fonte tenha sido lida.**
- **Requisito que já existe é atualizado, nunca duplicado.** A identidade é a
  origem, não o texto.
- **Todo achado declara quem concluiu**: `codigo` quando o código concluiu,
  `skill` quando ele apenas apontou um candidato para julgamento humano.
- **Projeto vazio devolve "por começar"**, não um relatório verde. Zero contra
  zero não é aprovação.

## O registro do projeto manda

O `dk` lê e escreve o esquema que os projetos da casa já usam —
`business-rules.json`, `requirements.json`, `sources.json`, `evidence.json`,
`traceability.json`, `lean-inception.json` — em `registry/`. Ele não cria um
registro paralelo ao que o projeto tem.

## Custo de contexto

Oito portas ficam no catálogo fixo, somando 2.325 B de `description`. As outras
22 skills declaram a etapa a que pertencem e só são consideradas dentro dela.

## Verificação

```bash
python3 verificar.py                      # 50 validadores
python3 tests/validate_release_gate.py    # 37 itens do portão de release
```

O portão de release existe porque o Kit anterior foi publicado sem ciclo provado
ponta a ponta. Nada é publicado com um item aberto.

## Documentação

- [`llms.txt`](llms.txt) — roteador de conhecimento
- [`llms-full.txt`](llms-full.txt) — contrato completo e invariantes
- [`docs/contrato-de-resposta.md`](docs/contrato-de-resposta.md) — como as skills respondem
- [`CHANGELOG.md`](CHANGELOG.md) — o que entrou em cada versão
- [`governance/`](governance/) — políticas
