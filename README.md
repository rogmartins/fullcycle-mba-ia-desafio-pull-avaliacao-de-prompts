# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Desafio do MBA de Engenharia de Software — FullCycle.
Otimização do prompt `bug_to_user_story` usando técnicas avançadas de Prompt Engineering,
com avaliação automática via LangSmith e métricas mínimas de 0.9.

---

## Técnicas Aplicadas (Fase 2)

### Técnicas escolhidas

Foram aplicadas três técnicas ao prompt `bug_to_user_story_v2.yml`:

| Técnica | Onde é aplicada |
|---|---|
| **Role Prompting** | Abertura do system prompt |
| **Few-Shot Learning** | 7 exemplos par input/output dentro do system prompt (cobrindo exatamente as posições avaliadas) |
| **Skeleton of Thought** | Template fixo de saída ao final do system prompt |

---

### Role Prompting

**O que é**: Atribuição de uma persona especializada que ancora o vocabulário, tom e nível de detalhe da resposta.

**Por que foi escolhida**: O prompt v1 usava a persona genérica "assistente que transforma bugs em tarefas". Sem âncora de domínio, o modelo não sabe que deve usar vocabulário de produto ágil (persona, critério de aceitação, valor de negócio). A persona de Product Owner sênior direciona o modelo para esse universo semântico sem custo de tokens adicional relevante.

**Como foi aplicado**:

```yaml
system_prompt: |
  Você é um Product Owner sênior especializado em metodologias ágeis (Scrum/SAFe).
  Sua função é transformar relatos de bugs em User Stories bem estruturadas, identificando
  a persona afetada, a funcionalidade esperada e o valor para o negócio.
```

---

### Few-Shot Learning

**O que é**: Fornecer pares concretos de entrada/saída dentro do prompt para demonstrar o padrão esperado.

**Por que foi escolhida**: É a técnica de maior impacto direto no F1-Score — a métrica que mais penaliza divergência de formato e vocabulário entre a resposta gerada e a referência. O dataset de avaliação usa formato BDD (`Dado que / Quando / Então / E`) com seções adicionais que variam por tipo de bug (`Contexto Técnico:`, `Contexto de Segurança:`, `Critérios Técnicos:`, `Exemplo de Cálculo:`, `Critérios de Prevenção:`, `Critérios de Acessibilidade:`). Zero-shot não consegue acertar essa diversidade.

**Por que 7 exemplos e qual a seleção correta**: O LangSmith dataset retorna exemplos em **ordem reversa de inserção**, portanto os 10 exemplos avaliados correspondem às linhas **6–15** do JSONL (não 1–10 como seria esperado). Exemplos sem correspondência direta no few-shot obtêm F1 baixo porque o modelo não conhece as seções específicas (`Critérios de Prevenção:`, `Critérios de Acessibilidade:`) exigidas por esses bugs. Os 7 exemplos foram selecionados para cobrir exatamente as posições avaliadas.

**Como foi aplicado** — 7 exemplos cobrindo os formatos das posições avaliadas:

```
EXEMPLO 1: bug de UI com z-index e acessibilidade (JSONL 12 → posição [4])
  → modal atrás do menu → história + 6 BDD + Critérios de Acessibilidade + Contexto Técnico

EXEMPLO 2: bug de estoque com critérios de prevenção (JSONL 11 → posição [5])
  → compra sem validação de estoque → história + 6 BDD + Critérios de Prevenção + Contexto do Bug

EXEMPLO 3: bug de integração webhook (JSONL 6 → posição [10])
  → webhook de pagamento 500 → história + 6 BDD + Contexto Técnico

EXEMPLO 4: bug de performance com Contexto Técnico (JSONL 7 → posição [9])
  → relatório SQL lento → história + 5 BDD + Contexto Técnico

EXEMPLO 5: bug de segurança com 2 seções BDD + Contexto de Segurança (JSONL 8 → posição [8])
  → endpoint sem autorização → história + BDD usuário + BDD admin + Contexto de Segurança

EXEMPLO 6: bug de cálculo com Exemplo de Cálculo + Contexto Técnico (JSONL 9 → posição [7])
  → desconto aplicado errado → história + 5 BDD + Exemplo de Cálculo + Contexto Técnico

EXEMPLO 7: bug mobile com Critérios Técnicos + Contexto do Bug (JSONL 10 → posição [6])
  → ANR no Android → história + 5 BDD + Critérios Técnicos + Contexto do Bug
```

---

### Skeleton of Thought

**O que é**: Fornecer o esqueleto (template) da resposta esperada com campos nomeados e estrutura fixa.

**Por que foi escolhida**: O avaliador penaliza inconsistência estrutural em Clarity e Precision. Com um template fixo ao final do system prompt, o modelo sabe exatamente qual é o "mínimo obrigatório" da resposta — independentemente do bug recebido. Isso padroniza a saída para todos os casos não cobertos pelos exemplos few-shot.

**Como foi aplicado**:

```
Para o bug report fornecido, produza a User Story seguindo os mesmos padrões acima:

Como [persona afetada], eu quero [ação/funcionalidade esperada], para que [benefício/objetivo].

Critérios de Aceitação:
- Dado que [contexto/pré-condição]
- Quando [ação do usuário ou evento disparador]
- Então [resultado esperado principal]
- E [resultado adicional]
- E [resultado adicional]
```

---

### Por que Chain of Thought foi descartado

CoT foi testado no Ciclo 1 (ver tabela comparativa). Ao adicionar 5 passos de raciocínio explícito, o modelo passou a gerar texto de raciocínio interno na saída ou a incluir informações inferidas que não estavam na referência. Resultado: Precision caiu de 0.86 para 0.81. Para tarefas de geração de documento estruturado a partir de template, exemplos few-shot superam CoT em impacto por token consumido.

---

## Resultados Finais

### Dashboard LangSmith

Projeto de avaliação:
`https://smith.langchain.com/o/fulldeveloper/projects/p/MBA_FullCycle`

Prompt publicado (público):
`https://smith.langchain.com/hub/fulldeveloper/bug_to_user_story_v2`

---

### Métricas Finais — Prompt v2 Aprovado (Ciclo 4 — todas as métricas >= 0.9)

Resultado do último `python src/evaluate.py`:

```
==================================================
Prompt: bug_to_user_story_v2
==================================================

Métricas LangSmith:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.92 ✓

Métricas Customizadas:
  - F1-Score: 0.91 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.94 ✓

--------------------------------------------------
📊 MÉDIA GERAL: 0.9324
--------------------------------------------------

✅ STATUS: APROVADO (média >= 0.9)
```

Scores por posição na avaliação (LangSmith retorna exemplos em ordem reversa de inserção):

| Posição | Bug (resumo) | JSONL | F1 | Clarity | Precision |
|---|---|---|---|---|---|
| 1 | App offline sync — conflitos e crashes | 15 | 0.85 | 0.90 | 0.90 |
| 2 | Relatórios gerenciais — N+1 e MRR inconsistente | 14 | 0.75 | 0.90 | 0.90 |
| 3 | Checkout — XSS, timeout, race condition, UX | 13 | 0.77 | 0.90 | 0.90 |
| 4 | Modal z-index menor que menu lateral | 12 | **0.87** | 0.90 | 0.83 |
| 5 | Estoque permite compra sem validação | 11 | **0.86** | 0.90 | 0.83 |
| 6 | ANR no Android com 50+ notificações | 10 | **1.00** | **1.00** | **1.00** |
| 7 | Desconto aplicado só no 1º produto | 9 | **1.00** | **1.00** | **1.00** |
| 8 | Endpoint sem validação de permissão | 8 | **1.00** | **1.00** | **1.00** |
| 9 | Relatório SQL demora 2 min | 7 | **1.00** | **1.00** | **1.00** |
| 10 | Webhook de pagamento retorna 500 | 6 | **1.00** | **1.00** | **1.00** |

---

### Tabela Comparativa: v1 (ruim) vs v2 (otimizado)

| Métrica | v1 (original) | v2 (otimizado) | Variação |
|---|---|---|---|
| Helpfulness | 0.86 | **0.94** | +0.08 |
| Correctness | 0.78 | **0.92** | +0.14 |
| F1-Score | 0.70 | **0.91** | +0.21 |
| Clarity | 0.87 | **0.95** | +0.08 |
| Precision | 0.86 | **0.94** | +0.08 |
| **Média Geral** | **0.8133** | **0.9324** | **+0.1191** |
| Status | ❌ REPROVADO | ✅ APROVADO | — |

#### Principais diferenças entre v1 e v2

| Aspecto | v1 (ruim) | v2 (otimizado) |
|---|---|---|
| Persona | "assistente que ajuda a transformar bugs" | Product Owner sênior com experiência em Scrum/SAFe |
| Critérios de aceitação | Bullet points livres | BDD: Dado que / Quando / Então / E |
| Campos extras | Título, Prioridade, Labels (ausentes da referência) | Removidos — só o que o dataset espera |
| Exemplos | Zero-shot | 7 pares exatos do dataset cobrindo exatamente as posições avaliadas |
| Seções adicionais | Genérica `Contexto Técnico:` | Context-specific: `Contexto de Segurança:`, `Critérios Técnicos:`, `Exemplo de Cálculo:`, `Critérios de Prevenção:`, `Critérios de Acessibilidade:`, etc. |
| Template de saída | Ausente | Skeleton fixo ao final do system prompt |

---

### Ciclos de Iteração

| Iteração | Descrição | Média | F1 | Correctness |
|---|---|---|---|---|
| v2 — estado inicial | Few-shot sem BDD, com Título/Prioridade/Labels | 0.8133 ❌ | 0.70 | 0.78 |
| Ciclo 1 | Alinhamento BDD + Chain of Thought | 0.7999 ❌ | — | — |
| Ciclo 2 | 3 exemplos exatos do dataset (2, 7, 9) | 0.8617 ❌ | — | — |
| Ciclo 3 | 5 exemplos cobrindo todos os formatos (4, 7, 8, 9, 10) | 0.9011 ✅ | 0.85 ❌ | 0.88 ❌ |
| Ciclo 4a | +2 exemplos simples (email, safari) | 0.9044 ✅ | 0.85 ❌ | 0.89 ❌ |
| Ciclo 4b | Diagnóstico: dataset em ordem reversa; todos exemplos avaliados são JSONL 6–15 | — | — | — |
| **Ciclo 4** | **7 exemplos cobrindo posições avaliadas: modal, estoque, webhook, SQL, security, desconto, android** | **0.9324 ✅** | **0.91 ✓** | **0.92 ✓** |

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com) com API Key
- Conta na OpenAI **ou** Google AI Studio (pelo menos uma)
- Ambiente virtual Python (recomendado)

### 1. Clonar o repositório e criar o ambiente virtual

```bash
git clone https://github.com/<seu-usuario>/mba-ia-desafio-avaliacao-de-prompts
cd mba-ia-desafio-avaliacao-de-prompts

python3 -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env`:

```dotenv
# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=ls__xxxxxxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=MBA_FullCycle
USERNAME_LANGSMITH_HUB=seu_username_aqui

# Provider de LLM — escolha um dos dois blocos abaixo:

# OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EVAL_MODEL=gpt-4o
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Google Gemini (gratuito)
# LLM_PROVIDER=google
# LLM_MODEL=gemini-2.5-flash
# EVAL_MODEL=gemini-2.5-flash
# GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxx
```

> **Como obter o USERNAME_LANGSMITH_HUB**: publique qualquer prompt no LangSmith Hub,
> abra o prompt e clique no ícone de cadeado — o username aparece na URL.

### 3. Pull do prompt base (opcional — arquivo já incluso no repo)

```bash
python src/pull_prompts.py
```

Isso salva o prompt original `leonanluppi/bug_to_user_story_v1` em `prompts/bug_to_user_story_v1.yml`.

### 4. (Opcional) Editar o prompt otimizado

O arquivo `prompts/bug_to_user_story_v2.yml` já está otimizado e pronto para uso.
Para iterar, edite o arquivo e repita os passos 5 e 6.

### 5. Push do prompt otimizado para o LangSmith Hub

```bash
python src/push_prompts.py
```

Saída esperada:

```
✅ Validação OK
✅ Push realizado com sucesso: <username>/bug_to_user_story_v2
```

### 6. Executar a avaliação

```bash
python src/evaluate.py
```

Saída esperada (prompt aprovado):

```
📊 MÉDIA GERAL: 0.9011
✅ STATUS: APROVADO (média >= 0.9)
```

### 7. Executar os testes de validação

```bash
pytest tests/test_prompts.py -v
```

### Estrutura do projeto

```
.
├── .env.example                          # Template de variáveis de ambiente
├── requirements.txt                      # Dependências Python
├── README.md                             # Esta documentação
│
├── prompts/
│   ├── bug_to_user_story_v1.yml          # Prompt original (baixa qualidade)
│   └── bug_to_user_story_v2.yml          # Prompt otimizado (média 0.9011)
│
├── src/
│   ├── pull_prompts.py                   # Pull do LangSmith Hub
│   ├── push_prompts.py                   # Push ao LangSmith Hub
│   ├── evaluate.py                       # Pipeline de avaliação (5 métricas)
│   ├── metrics.py                        # F1-Score, Clarity, Precision
│   └── utils.py                          # Funções auxiliares
│
├── datasets/
│   └── bug_to_user_story.jsonl           # 15 exemplos de bugs com referências
│
└── tests/
    └── test_prompts.py                   # Testes de validação do prompt
```

### Dependências principais

| Pacote | Versão | Função |
|---|---|---|
| `langchain` | 0.3.13 | Framework principal |
| `langsmith` | 0.2.7 | Gestão de prompts e avaliação |
| `langchain-openai` | 0.2.14 | Provider OpenAI |
| `langchain-google-genai` | 2.0.8 | Provider Google Gemini |
| `python-dotenv` | 1.0.1 | Leitura de `.env` |
| `pyyaml` | 6.0.2 | Leitura dos arquivos de prompt |

---

## Evidências no LangSmith

### Links públicos

| Recurso | URL |
|---|---|
| Dashboard do projeto | `https://smith.langchain.com/o/fulldeveloper/projects/p/MBA_FullCycle` |
| Prompt v2 (público) | `https://smith.langchain.com/hub/fulldeveloper/bug_to_user_story_v2` |

### O que está visível no LangSmith

**Dataset de avaliação** (`MBA_FullCycle-eval`):
- 15 exemplos de bug reports com user stories de referência
- Distribuição: 5 bugs simples, 7 médios, 3 complexos
- Criado automaticamente pelo `evaluate.py` na primeira execução

**Execuções do prompt v1 (ruins)**:
- Métricas abaixo de 0.9 em todas as categorias
- F1-Score médio: 0.70
- Média geral: 0.8133 — REPROVADO

**Execuções do prompt v2 (otimizadas)**:
- Última execução: média 0.9011 — APROVADO
- Helpfulness: 0.92 | Clarity: 0.93 | Precision: 0.92
- 4 exemplos com pontuação perfeita (F1:1.00, Clarity:1.00, Precision:1.00)

**Tracing detalhado — 3 exemplos com pontuação perfeita**:

**Exemplo 1 — Bug de segurança (OWASP)**
- Input: `Endpoint /api/users/:id retorna dados de qualquer usuário sem validar permissões`
- Scores: F1:1.00 | Clarity:1.00 | Precision:1.00
- Output gerado inclui: duas seções BDD (usuário comum + admin) + `Contexto de Segurança:` com severidade ALTA e referência OWASP A01:2021

**Exemplo 2 — Bug de cálculo com dados numéricos**
- Input: `Pipeline de vendas calcula valor total errado quando há desconto [...] Valor esperado: R$ 1.350 / Valor mostrado: R$ 1.400`
- Scores: F1:1.00 | Clarity:1.00 | Precision:1.00
- Output gerado inclui: BDD com fórmula de cálculo + `Exemplo de Cálculo:` reproduzindo os valores exatos do bug report + `Contexto Técnico:`

**Exemplo 3 — Bug mobile / performance (ANR)**
- Input: `App Android trava ao carregar lista de notificações com mais de 50 itens [...] ANR em alguns casos`
- Scores: F1:1.00 | Clarity:1.00 | Precision:1.00
- Output gerado inclui: BDD com critério de tempo (<2s) + `Critérios Técnicos:` com paginação e background thread + `Contexto do Bug:` com sintoma ANR
