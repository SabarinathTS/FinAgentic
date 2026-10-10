# 📐 System Development Schema & Architecture Specification

Technical architecture and schema reference for the FinAgentic autonomous agent system.

---

## 1. High-Level System Architecture Schema

The FinAgentic platform is organized into six decoupled architectural layers: **Presentation**, **Orchestration**, **Cognitive Agents**, **Tool Execution**, **Persistence/Memory**, and **Model Providers**.

```mermaid
graph TB
    subgraph "1. Presentation Layer"
        UI["🖥️ Streamlit Web Interface (src/main.py)"]
        CLI["💻 Rich Command-Line Interface (src/cli.py)"]
    end

    subgraph "2. Orchestration Layer (LangGraph)"
        WF["🔄 FinancialAgentWorkflow (src/workflow.py)"]
        State["📦 AgentState (State Graph Context)"]
        WF <--> State
    end

    subgraph "3. Cognitive Agent Layer"
        ReAct["🧠 ReActAgent (src/react_agent.py)<br/>Thought ➜ Action ➜ Observation Loop"]
        RAG["📚 RAGEngine (src/rag_engine.py)<br/>Semantic Chunking & Context Retrieval"]
    end

    subgraph "4. Tool Execution Layer (MCP-Style)"
        Registry["🛠️ ToolRegistry (src/tool_system.py)"]
        StockTool["📈 StockDataTool (Real-time yfinance)"]
        CalcTool["🔢 CalculatorTool (Math & P/E Evaluator)"]
        SearchTool["🌐 WebSearchTool (News & Industry Signals)"]
        Registry --> StockTool
        Registry --> CalcTool
        Registry --> SearchTool
    end

    subgraph "5. Storage & Persistence Layer"
        FAISS_DB[("🗄️ FAISS Vector Store (data/vector_store/)")]
        TraceStore[("📝 Execution Traces (data/traces/)")]
    end

    subgraph "6. Model Provider & Inference Layer"
        OllamaLocal["🏠 Local LLMs via Ollama<br/>(Llama 3.2, Qwen 2.5, Nomic Embed)"]
        CloudAPIs["☁️ Cloud Provider APIs<br/>(OpenAI, Anthropic, Gemini, Groq, Mistral)"]
        Config["⚙️ OllamaConfig & .env (src/config.py)"]
    end

    UI --> WF
    CLI --> WF
    WF --> ReAct
    WF --> RAG
    ReAct --> Registry
    RAG --> FAISS_DB
    ReAct --> TraceStore
    ReAct --> OllamaLocal
    ReAct -.-> CloudAPIs
    RAG --> OllamaLocal
    Config --> OllamaLocal
    Config --> CloudAPIs
```

---

## 2. LangGraph State Machine Workflow Schema

The LangGraph orchestrator models the financial reasoning process as a deterministic **Directed Acyclic Graph (DAG)** with strongly typed state transitions.

### 2.1 State Graph Lifecycle Diagram

```mermaid
stateDiagram-v2
    [*] --> QueryAnalysis: User Query / Ticker Input
    QueryAnalysis --> DataCollection: Validated Intent & Ticker
    DataCollection --> RAGRetrieval: Market Data Acquired
    RAGRetrieval --> TechnicalAnalysis: Financial Filings Retrieved
    TechnicalAnalysis --> SynthesisReport: Technical Indicators Computed
    SynthesisReport --> [*]: Final Financial Intelligence Report Delivered
```

### 2.2 State Transition Nodes

| Node Name | Input State Attributes | Output State Mutations | Responsibilities |
|---|---|---|---|
| `analyze_query` | `query`, `ticker` | `step`, `reasoning_steps` | Parses ticker symbols, validates query intent, initializes analysis strategy. |
| `collect_data` | `ticker` | `market_data`, `reasoning_steps` | Invokes `StockDataTool` via tool registry to fetch real-time price, P/E, volume, and beta. |
| `retrieve_context` | `query`, `ticker` | `rag_context`, `reasoning_steps` | Queries the FAISS vector database for 10-K, 10-Q, and company filing disclosures. |
| `analyze_technicals`| `market_data` | `technical_signals`, `reasoning_steps` | Executes quantitative metrics (Moving Averages, RSI indicators, Valuation spreads). |
| `synthesize_report` | All Accumulated State | `final_report`, `status` | Synthesizes an executive decision report with recommendations and risk factors. |

---

## 3. ReAct (Reasoning + Acting) Cognitive Loop Schema

The ReAct pattern implements a multi-hop cognitive loop where the model iteratively reasons about the current observation before selecting an action.

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Workflow
    participant Agent as ReActAgent
    participant LLM as Model Inference (Ollama/Cloud)
    participant Registry as ToolRegistry
    participant Tool as Target Tool

    User->>Agent: think(query)
    loop Up to max_reasoning_steps (Default: 10)
        Agent->>LLM: Prompt (History + Observations + Tool Schemas)
        LLM-->>Agent: Generated "Thought" & "Action: tool_name[params]"
        Agent->>Agent: Parse Action & Validate Arguments
        alt Action == "Final Answer"
            Agent-->>User: Return Answer & Complete Reasoning Trace
        else Action == Tool Call
            Agent->>Registry: execute(tool_name, params)
            Registry->>Tool: run(**params)
            Tool-->>Registry: Result payload
            Registry-->>Agent: Observation
            Agent->>Agent: Record Step in Reasoning Trace
        end
    end
```

---

## 4. Vector RAG Pipeline & Storage Schema

The Retrieval-Augmented Generation (RAG) engine operates on dense semantic vector embeddings stored in a local FAISS index.

```mermaid
flowchart LR
    subgraph "Ingestion Pipeline"
        Doc[Financial Reports / News] --> Splitter[RecursiveCharacterTextSplitter<br/>chunk_size: 512, overlap: 50]
        Splitter --> Chunks[Text Chunks]
        Chunks --> Embedder[OllamaEmbeddings<br/>nomic-embed-text]
        Embedder --> Vectors[Vector Embeddings]
        Vectors --> FAISS[(FAISS CPU Index)]
    end

    subgraph "Retrieval & Generation"
        UserQ[User Question] --> QEmbed[Embed Query]
        QEmbed --> SimSearch[FAISS Similarity Search<br/>top_k = 5]
        FAISS -.-> SimSearch
        SimSearch --> Context[Retrieved Document Context]
        Context --> GenLLM[LLM Generator]
        UserQ --> GenLLM
        GenLLM --> Output[Grounded Financial Insight]
    end
```

---

## 5. Data & State Schema Specifications

### 5.1 LangGraph State Schema (`AgentState`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AgentState",
  "type": "object",
  "properties": {
    "query": { "type": "string", "description": "User analytical prompt" },
    "ticker": { "type": "string", "description": "Target stock ticker symbol (e.g., AAPL, NVDA)" },
    "market_data": { 
      "type": "object", 
      "properties": {
        "price": { "type": "number" },
        "pe_ratio": { "type": "number" },
        "market_cap": { "type": "number" },
        "52_week_high": { "type": "number" },
        "52_week_low": { "type": "number" }
      }
    },
    "rag_context": { 
      "type": "array", 
      "items": { "type": "string" },
      "description": "Retrieved document text excerpts"
    },
    "technical_signals": {
      "type": "object",
      "properties": {
        "trend": { "type": "string", "enum": ["Bullish", "Bearish", "Neutral"] },
        "rsi": { "type": "number" },
        "recommendation": { "type": "string" }
      }
    },
    "reasoning_steps": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "step_number": { "type": "integer" },
          "thought": { "type": "string" },
          "action": { "type": "string" },
          "observation": { "type": "string" }
        }
      }
    },
    "final_report": { "type": "string", "description": "Synthesized executive report" },
    "status": { "type": "string", "enum": ["initialized", "in_progress", "completed", "failed"] }
  },
  "required": ["query", "ticker"]
}
```

### 5.2 Tool Interface Schema (`BaseTool`)

Each tool registered in the `ToolRegistry` conforms to the Model Context Protocol (MCP) tool format:

```json
{
  "name": "stock_data",
  "description": "Fetch real-time market data, valuation metrics, and fundamentals for a given equity ticker.",
  "parameters": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Standard stock exchange ticker symbol (e.g., AAPL, MSFT, GOOGL)"
      }
    },
    "required": ["ticker"]
  }
}
```

---

## 6. Configuration & Runtime Environment Schema

The application configuration in `src/config.py` parses parameters with hierarchical precedence:
`CLI Flags > Environment Variables (.env) > Built-in Defaults`.

```json
{
  "OLLAMA_BASE_URL": { "type": "string", "default": "http://localhost:11434" },
  "REASONING_MODEL": { "type": "string", "default": "llama3.2:latest" },
  "ANALYSIS_MODEL": { "type": "string", "default": "qwen2.5:latest" },
  "EMBEDDING_MODEL": { "type": "string", "default": "nomic-embed-text:latest" },
  "VECTOR_STORE_TYPE": { "type": "string", "enum": ["faiss", "chroma"], "default": "faiss" },
  "LOG_LEVEL": { "type": "string", "default": "INFO" },
  "DATA_DIR": { "type": "string", "default": "./data" },
  "API_KEYS": {
    "OPENAI_API_KEY": { "type": "string", "sensitive": true },
    "ANTHROPIC_API_KEY": { "type": "string", "sensitive": true },
    "GEMINI_API_KEY": { "type": "string", "sensitive": true },
    "GROQ_API_KEY": { "type": "string", "sensitive": true },
    "TAVILY_API_KEY": { "type": "string", "sensitive": true },
    "FINNHUB_API_KEY": { "type": "string", "sensitive": true },
    "ALPHA_VANTAGE_API_KEY": { "type": "string", "sensitive": true }
  }
}
```


