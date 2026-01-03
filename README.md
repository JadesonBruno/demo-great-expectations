# 🎯 Demo Great Expectations

Demonstração prática de validação de dados usando **Great Expectations** — framework open-source para garantir qualidade de dados em pipelines de produção.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Arquitetura do Great Expectations](#arquitetura-do-great-expectations)
- [Fluxo de Validação (10 Passos)](#fluxo-de-validação-10-passos)
- [Como Executar](#como-executar)
- [Visualizando os Resultados](#visualizando-os-resultados)
- [Integração com Orquestradores](#integração-com-orquestradores)
- [Próximos Passos](#próximos-passos)
- [Suporte e Contato](#suporte-e-contato)

---

## 📖 Sobre o Projeto

Este projeto demonstra como implementar validação de dados robusta e production-ready usando Great Expectations (versão 1.6.4+). O exemplo valida um dataset CSV simples com regras de qualidade personalizadas, gerando relatórios HTML interativos automaticamente.

### ✨ Funcionalidades

- ✅ Validação automática de dados com 7 expectations (regras de qualidade)
- ✅ Geração de relatórios HTML (Data Docs) após cada validação
- ✅ Configuração persistente (checkpoints, expectations suites)
- ✅ Pronto para integração com orquestradores (Airflow, Prefect)
- ✅ Auditabilidade e rastreamento de execuções

---

## 🛠️ Requisitos

- **Python**: 3.12
- **Poetry**: Gerenciador de dependências
- **Great Expectations**: >=1.6.4, <2.0.0

---

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/demo-great-expectations.git
cd demo-great-expectations

# Instale as dependências com Poetry
poetry install

# Ative o ambiente virtual
poetry shell
```

---

## 📁 Estrutura do Projeto

```
demo-great-expectations/
├── data/
│   └── dataset.csv              # Dataset de exemplo (10 registros)
├── gx/                          # Configurações do Great Expectations (versionadas)
│   ├── great_expectations.yml   # Config principal do contexto
│   ├── checkpoints/
│   │   └── checkpoint.yml       # Checkpoint persistido
│   ├── expectations/
│   │   └── expectation.json     # Expectation Suite persistida
│   └── uncommitted/             # Resultados (não versionados - .gitignore)
│       ├── data_docs/           # Data Docs HTML gerados
│       └── validations/         # JSONs dos resultados
├── src/
│   └── data_quality.py          # Script principal de validação
├── pyproject.toml               # Dependências do projeto
└── README.md                    # Esta documentação
```

---

## 🏗️ Arquitetura do Great Expectations

O Great Expectations segue uma arquitetura modular e declarativa:

```
┌─────────────────────────────────────────────────────────────┐
│                    DataContext (contexto)                   │
│  Gerenciador central: configurações, stores, checkpoints    │
└───────────────────┬─────────────────────────────────────────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
┏━━━━━━━━━┓   ┏━━━━━━━━━┓   ┏━━━━━━━━━┓
┃ Sources ┃   ┃ Suites  ┃   ┃Checkpoints┃
┗━━━━━━━━━┛   ┗━━━━━━━━━┛   ┗━━━━━━━━━┛
      │             │             │
      ▼             ▼             ▼
[Datasources] [Expectations] [Validations]
   [Assets]      [Rules]      [Actions]
  [Batches]
```

---

## 🔄 Fluxo de Validação (10 Passos)

### 1️⃣ **Criar um Contexto (DataContext)**

**O que é:** O "gerenciador central" do Great Expectations — armazena configurações, datasources, suites, checkpoints, resultados.

**Tipos:**
- `mode="file"` → Persiste tudo em `great_expectations/` (produção)
- `mode="ephemeral"` → Temporário, não salva arquivos (testes/notebooks)

**Código:**
```python
context = gx.get_context(mode="file")
```

---

### 2️⃣ **Criar um Datasource**

**O que é:** Representa a **origem dos dados** (Pandas DataFrame, SQL, Spark, S3, etc.)

**Por que precisa:** Define como o GE se conecta aos dados e gera batches.

**Código:**
```python
data_source = context.data_sources.add_pandas(name="pandas")
```

---

### 3️⃣ **Criar um Data Asset**

**O que é:** Um "ponteiro lógico" para um conjunto de dados dentro do datasource (ex.: uma tabela, um arquivo CSV, um DataFrame).

**Por que precisa:** Organiza e nomeia os dados que você quer validar.

**Código:**
```python
data_asset = data_source.add_dataframe_asset(name="pd_dataframe_asset")
```

---

### 4️⃣ **Criar um Batch Definition**

**O que é:** Define **como** criar um batch (lote) de dados a partir do Data Asset.

**Tipos:**
- `add_batch_definition_whole_dataframe` → Valida o DataFrame inteiro
- `add_batch_definition_daily` → Divide por data (útil para séries temporais)

**Por que precisa:** Permite parametrizar quais dados validar (ex.: passar `batch_parameters={"dataframe": df}` em runtime).

**Código:**
```python
batch_definition = data_asset.add_batch_definition_whole_dataframe("batch_definition")
```

---

### 5️⃣ **Criar a Expectation Suite (com as expectativas)**

**O que é:** Um conjunto nomeado de **regras de validação** (expectations) que você quer aplicar aos dados.

**Exemplos de expectations:**
- `ExpectColumnToExist` → Coluna deve existir
- `ExpectColumnValuesToNotBeNull` → Sem valores nulos
- `ExpectColumnValuesToBeBetween` → Valores em um range

**Por que precisa:** Define **o que** você espera dos dados.

**Código:**
```python
suite = context.suites.add(
    gx.core.expectation_suite.ExpectationSuite(name="expectation")
)
suite.add_expectation(
    gx.expectations.ExpectColumnToExist(column="id")
)
```

**Expectations configuradas neste projeto:**
1. ✅ `ExpectColumnToExist` — Coluna "id" deve existir
2. ✅ `ExpectTableColumnCountToBeBetween` — Entre 1-3 colunas
3. ✅ `ExpectTableRowCountToBeBetween` — Entre 1-100 linhas
4. ✅ `ExpectColumnValuesToNotBeNull` — Coluna "id" sem valores nulos
5. ✅ `ExpectColumnValuesToBeBetween` — Valores "id" entre 1-10
6. ✅ `ExpectColumnValuesToBeUnique` — Valores "id" únicos
7. ✅ `ExpectColumnUniqueValueCountToBeBetween` — 1-10 valores únicos em "id"

---

### 6️⃣ **Criar o Validation Definition**

**O que é:** Liga um **Batch Definition** (dados) a uma **Expectation Suite** (regras).

**Por que precisa:** Define **qual batch validar** com **quais expectations**.

**Código:**
```python
validation_definition = context.validation_definitions.add(
    gx.core.validation_definition.ValidationDefinition(
        name="validation_definition",
        data=batch_definition,  # ← quais dados
        suite=suite,            # ← quais regras
    )
)
```

⚠️ **Nota:** Não confundir com `Validator` (objeto de runtime usado em notebooks).

---

### 7️⃣ **Criar configurações para Data Docs (site HTML)**

**O que é:** Configura onde/como gerar os relatórios HTML de validação.

**Por que precisa:** Para visualizar resultados em um navegador (auditoria, compartilhamento).

**Código:**
```python
site_config = {
    "class_name": "SiteBuilder",
    "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
    "store_backend": {
        "class_name": "TupleFilesystemStoreBackend",
        "base_directory": "uncommitted/data_docs/local_site/",
    },
}
context.add_data_docs_site(site_name="my_data_docs_site", site_config=site_config)
```

---

### 8️⃣ **Actions (Ações do Checkpoint)**

**O que são:** Tarefas automáticas que o Checkpoint executa **depois** de cada validação.

**Exemplos comuns:**
- `StoreValidationResultAction` → Salva o JSON do resultado em `great_expectations/uncommitted/validations/`
- `UpdateDataDocsAction` → Reconstrói os Data Docs HTML com os novos resultados
- `SlackNotificationAction` → Envia notificação Slack em caso de falha/sucesso

**Por que usar:** Automatiza persistência, geração de relatórios e integrações sem código manual.

**Código:**
```python
actions = [
    gx.checkpoint.actions.UpdateDataDocsAction(
        name="update_my_site",
        site_names=["my_data_docs_site"],
    )
]
```

---

### 9️⃣ **Checkpoint**

**O que é:** Um "job" configurável que:
1. Executa uma ou mais **Validation Definitions** (valida dados com expectations)
2. Executa **Actions** (salva resultados, gera docs, notifica)

**Por que usar:** Para orquestração e automação — Airflow/Prefect/CI chamam checkpoints.

**Código:**
```python
checkpoint = context.checkpoints.add(
    gx.checkpoint.checkpoint.Checkpoint(
        name="checkpoint",
        validation_definitions=[validation_definition],  # ← o que validar
        actions=actions,                                # ← o que fazer depois
    )
)
```

---

### 🔟 **Checkpoint Result**

**O que é:** O **resultado** da execução do checkpoint — contém:
- Sucesso/falha geral (`success: true/false`)
- Resultados de cada validação (quais expectations passaram/falharam)
- Estatísticas (% sucesso, valores observados, etc.)
- Metadados (run_id, timestamp, etc.)

**Por que usar:** Para:
- Verificar programaticamente se a validação passou
- Tomar decisões (ex.: interromper pipeline se `success == False`)
- Debug (ver quais expectations falharam)

**Código:**
```python
checkpoint_result = checkpoint.run(
    batch_parameters={"dataframe": df},  # ← passa o DataFrame em runtime
    run_id=RunIdentifier(run_name=f"demo_run_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"),
)

# Verificar sucesso
if checkpoint_result["success"]:
    print("✅ Validação passou!")
else:
    print("❌ Validação falhou!")
    # Interromper pipeline, enviar alerta, etc.
```

---

## 📊 Resumo Visual do Fluxo

```
1. Context         ← Gerenciador central (configurações, stores)
   ↓
2. Datasource      ← Como conectar aos dados (Pandas, SQL, etc.)
   ↓
3. Data Asset      ← "Ponteiro" para um conjunto de dados
   ↓
4. Batch Definition ← Como criar um batch (lote) dos dados
   ↓
5. Expectation Suite ← Regras de validação (o que esperar)
   ↓
6. Validation Definition ← Liga batch + suite (o que validar + com quais regras)
   ↓
7. Data Docs Config ← Onde/como gerar relatórios HTML
   ↓
8. Actions         ← Tarefas automáticas pós-validação (salvar, gerar docs, notificar)
   ↓
9. Checkpoint      ← "Job" que executa validations + actions
   ↓
10. Checkpoint Result ← Resultado da execução (sucesso/falha, estatísticas)
```

---

## 🎯 Analogia Prática (Pipeline de Dados)

Imagine um **sistema de controle de qualidade em uma fábrica**:

| Componente | Analogia |
|------------|----------|
| **Context** | Configuração da fábrica (onde ficam as máquinas, registros) |
| **Datasource** | Esteira transportadora (de onde vêm os produtos) |
| **Data Asset** | Tipo de produto (ex.: "lote de parafusos") |
| **Batch Definition** | Tamanho do lote a inspecionar (ex.: "todos os parafusos do dia") |
| **Expectation Suite** | Lista de checagem de qualidade (ex.: "diâmetro 5mm ± 0.1mm", "sem ferrugem") |
| **Validation Definition** | Instrução: "inspecionar lote X com checklist Y" |
| **Data Docs Config** | Onde imprimir o relatório de inspeção |
| **Actions** | O que fazer após inspeção (salvar resultado, gerar relatório, ligar para supervisor se falhar) |
| **Checkpoint** | O operador que executa a inspeção + ações automáticas |
| **Checkpoint Result** | Relatório final ("aprovado"/"reprovado", detalhes) |

---

## 🚀 Como Executar

### Execução Local

```bash
# Ativar ambiente Poetry
poetry shell

# Executar validação
python src/data_quality.py
```

**Saída esperada:**
```
Calculating Metrics: 100%|████████████████| 21/21 [00:00<00:00, 1237.21it/s]
{
    "success": true,
    "statistics": {
        "evaluated_validations": 1,
        "success_percent": 100.0,
        "successful_validations": 1,
        "unsuccessful_validations": 0
    },
    ...
}
```

O navegador abrirá automaticamente com os Data Docs.

---

## 📊 Visualizando os Resultados

### Data Docs (Relatórios HTML)

Após executar o script, o Great Expectations gera automaticamente:

```
gx/uncommitted/data_docs/local_site/
├── index.html                    # ← Home (lista de validações)
├── expectations/
│   └── expectation.html          # ← Documentação das regras
└── validations/
    └── expectation/
        └── demo_run_*/
            └── *.html            # ← Resultados detalhados
```

**Como visualizar:**
1. Abra `gx/uncommitted/data_docs/local_site/index.html` no navegador
2. Navegue para **"Validation Results"** (aba superior)
3. Clique em uma linha para ver detalhes da execução

**Informações disponíveis:**
- ✅ Status geral (sucesso/falha)
- 📊 Estatísticas (% sucesso, valores observados)
- 📋 Detalhes por expectation (passou/falhou, unexpected_count, etc.)
- 🕐 Timestamp e Run Name
- 📁 Asset e Batch utilizados

---

## 🔗 Integração com Orquestradores

### Exemplo: Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import great_expectations as gx
from great_expectations.core.run_identifier import RunIdentifier

def validate_data(**context):
    # 1. Carregar dados
    df = pd.read_csv("/path/to/dataset.csv")

    # 2. Carregar contexto GE (do disco)
    ge_context = gx.get_context(context_root_dir="/path/to/great_expectations")

    # 3. Executar checkpoint (configuração persistida)
    checkpoint_result = ge_context.run_checkpoint(
        checkpoint_name="checkpoint",
        batch_parameters={"dataframe": df},
        run_id=RunIdentifier(run_name=f"airflow_{datetime.now().isoformat()}"),
    )

    # 4. Verificar sucesso e interromper pipeline se falhar
    if not checkpoint_result["success"]:
        raise ValueError("Data validation failed!")

    return checkpoint_result["success"]

with DAG(
    dag_id="data_quality_validation",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
) as dag:

    validate_task = PythonOperator(
        task_id="validate_with_ge",
        python_callable=validate_data,
    )
```

**Vantagens:**
- ✅ Configurações versionadas no Git (`gx/checkpoints/`, `gx/expectations/`)
- ✅ Reutilizável em múltiplos DAGs/equipes
- ✅ Auditabilidade e rastreamento completo
- ✅ Interrupção automática de pipeline em caso de falha

---

## 🚀 Próximos Passos

1. **Teste com dados que falham**
   - Altere o CSV para incluir valores nulos/duplicados
   - Observe como o `checkpoint_result` mostra falhas detalhadas

2. **Adicione mais actions**
   ```python
   actions = [
       gx.checkpoint.actions.StoreValidationResultAction(
           name="store_validation_result"
       ),
       gx.checkpoint.actions.UpdateDataDocsAction(
           name="update_my_site",
           site_names=["my_data_docs_site"],
       ),
   ]
   ```

3. **Integre com orquestrador**
   - Crie um DAG do Airflow usando `context.run_checkpoint()`
   - Configure notificações (Slack, email) em caso de falha

4. **Versionamento completo**
   ```bash
   git add gx/checkpoints/ gx/expectations/ gx/great_expectations.yml
   git commit -m "Add GE configuration for production"
   ```

5. **Expanda validações**
   - Adicione expectations para outras colunas
   - Crie múltiplas suites (dev, staging, prod)
   - Valide dados de múltiplas fontes (SQL, S3, APIs)

---

## 📞 Suporte e Contato

**Jadeson Bruno**
- 📧 Email: jadesonbruno.a@outlook.com
- 🐙 GitHub: [@JadesonBruno](https://github.com/JadesonBruno)
- 💼 LinkedIn: [Jadeson Bruno](https://www.linkedin.com/in/jadeson-silva/)

---

⭐ **Se este projeto foi útil, deixe uma estrela no repositório!**

📝 **Licença**: MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
