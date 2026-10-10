"""Configuration for Ollama-based Financial Agent and API Integrations
This demonstrates local LLM usage with open-source models as well as API key management.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from pathlib import Path

# Load environment variables from .env and api_keys.env if present
try:
    from dotenv import load_dotenv
    # Look for .env in project root
    project_root = Path(__file__).resolve().parent.parent
    env_file = project_root / ".env"
    api_keys_file = project_root / "api_keys.env"
    
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
    if api_keys_file.exists():
        load_dotenv(dotenv_path=api_keys_file)
    # Default fallback
    load_dotenv()
except ImportError:
    pass

class OllamaModel(Enum):
    """Available open-source models in Ollama"""
    LLAMA3_8B = "llama3.2:latest"
    LLAMA3_70B = "llama3.2:70b"
    QWEN2_5 = "qwen2.5:latest"
    MISTRAL = "mistral:latest"
    MIXTRAL = "mixtral:latest"
    PHI3 = "phi3:latest"
    GEMMA2 = "gemma2:latest"
    DEEPSEEK = "deepseek-coder:latest"
    SOLAR = "solar:latest"

    # For embeddings
    NOMIC_EMBED = "nomic-embed-text:latest"
    MXBAI_EMBED = "mxbai-embed-large:latest"

@dataclass
class OllamaConfig:
    """Configuration for Ollama-based agents and API integrations

    This config demonstrates:
    - Multiple model support for different tasks
    - Local embedding models for RAG
    - Temperature and parameter tuning
    - Tool configuration for MCP-style interactions
    - Centralized API key management
    """

    # Ollama connection
    base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

    # Model selection - demonstrating task-specific models with env overrides
    reasoning_model: str = field(default_factory=lambda: os.getenv("REASONING_MODEL", OllamaModel.LLAMA3_8B.value))
    analysis_model: str = field(default_factory=lambda: os.getenv("ANALYSIS_MODEL", OllamaModel.QWEN2_5.value))
    coding_model: str = field(default_factory=lambda: os.getenv("CODING_MODEL", OllamaModel.DEEPSEEK.value))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", OllamaModel.NOMIC_EMBED.value))

    # Model parameters
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    num_predict: int = 2048

    # RAG configuration
    chunk_size: int = 512
    chunk_overlap: int = 50
    similarity_top_k: int = 5

    # Vector store settings
    vector_store_type: str = field(default_factory=lambda: os.getenv("VECTOR_STORE_TYPE", "faiss"))
    persist_directory: str = "./data/vector_store"

    # ReAct configuration
    max_reasoning_steps: int = 10
    enable_reasoning_trace: bool = True

    # Tool configuration (MCP-style)
    available_tools: List[str] = field(default_factory=lambda: [
        "web_search",
        "calculator",
        "code_interpreter",
        "file_reader",
        "sql_query",
        "api_caller"
    ])

    # Memory configuration
    memory_type: Literal["buffer", "summary", "kg"] = "buffer"
    max_memory_tokens: int = 2000

    # Logging and debugging
    verbose: bool = True
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    save_traces: bool = True
    trace_dir: str = "./data/traces"

    # API Keys (Loaded from .env / api_keys.env)
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    gemini_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    groq_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    mistral_api_key: Optional[str] = field(default_factory=lambda: os.getenv("MISTRAL_API_KEY"))
    deepseek_api_key: Optional[str] = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"))
    cohere_api_key: Optional[str] = field(default_factory=lambda: os.getenv("COHERE_API_KEY"))
    perplexity_api_key: Optional[str] = field(default_factory=lambda: os.getenv("PERPLEXITY_API_KEY"))
    tavily_api_key: Optional[str] = field(default_factory=lambda: os.getenv("TAVILY_API_KEY"))
    serpapi_api_key: Optional[str] = field(default_factory=lambda: os.getenv("SERPAPI_API_KEY"))
    finnhub_api_key: Optional[str] = field(default_factory=lambda: os.getenv("FINNHUB_API_KEY"))
    alpha_vantage_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ALPHA_VANTAGE_API_KEY"))
    polygon_api_key: Optional[str] = field(default_factory=lambda: os.getenv("POLYGON_API_KEY"))
    langchain_api_key: Optional[str] = field(default_factory=lambda: os.getenv("LANGCHAIN_API_KEY"))

    def __post_init__(self):
        # Set environment variable for langchain-ollama
        os.environ["OLLAMA_BASE_URL"] = self.base_url

    def get_api_key(self, name: str) -> Optional[str]:
        """Retrieve an API key by name from config or environment"""
        key_mapping = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "gemini": self.gemini_api_key,
            "google": self.gemini_api_key,
            "groq": self.groq_api_key,
            "mistral": self.mistral_api_key,
            "deepseek": self.deepseek_api_key,
            "cohere": self.cohere_api_key,
            "perplexity": self.perplexity_api_key,
            "tavily": self.tavily_api_key,
            "serpapi": self.serpapi_api_key,
            "finnhub": self.finnhub_api_key,
            "alpha_vantage": self.alpha_vantage_api_key,
            "polygon": self.polygon_api_key,
            "langchain": self.langchain_api_key,
        }
        normalized = name.lower().replace("-", "_").replace(" ", "_")
        if normalized in key_mapping:
            return key_mapping[normalized]
        return os.getenv(name)

    def list_configured_keys(self) -> Dict[str, bool]:
        """Return dict of available services and whether keys are provided"""
        return {
            "OpenAI": bool(self.openai_api_key),
            "Anthropic": bool(self.anthropic_api_key),
            "Google Gemini": bool(self.gemini_api_key),
            "Groq": bool(self.groq_api_key),
            "Mistral AI": bool(self.mistral_api_key),
            "DeepSeek": bool(self.deepseek_api_key),
            "Cohere": bool(self.cohere_api_key),
            "Perplexity": bool(self.perplexity_api_key),
            "Tavily Search": bool(self.tavily_api_key),
            "SerpAPI": bool(self.serpapi_api_key),
            "Finnhub": bool(self.finnhub_api_key),
            "Alpha Vantage": bool(self.alpha_vantage_api_key),
            "Polygon.io": bool(self.polygon_api_key),
            "LangSmith/LangChain": bool(self.langchain_api_key),
        }

    def get_model_config(self, task: str = "default") -> Dict[str, Any]:
        """Get model configuration for specific task"""
        model_map = {
            "reasoning": self.reasoning_model,
            "analysis": self.analysis_model,
            "coding": self.coding_model,
            "default": self.reasoning_model
        }

        return {
            "model": model_map.get(task, self.reasoning_model),
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "num_predict": self.num_predict,
            "options": {
                "num_ctx": 4096,  # Context window
                "num_batch": 512,  # Batch size for prompt eval
                "num_gpu": 1,      # Number of GPUs to use
            }
        }

    def validate(self) -> bool:
        """Validate Ollama connection and models"""
        import requests

        try:
            # Check Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama not responding at {self.base_url}")

            # Check required models are available
            available_models = [m["name"] for m in response.json().get("models", [])]
            required_models = [
                self.reasoning_model,
                self.analysis_model,
                self.embedding_model
            ]

            missing_models = [m for m in required_models if m not in available_models]

            if missing_models:
                print(f"⚠️ Missing models: {missing_models}")
                print("Pull them with: ollama pull <model_name>")
                return False

            return True

        except Exception as e:
            print(f"❌ Ollama validation failed: {e}")
            return False

# Global config instance
config = OllamaConfig()

# Educational helpers
def list_available_models():
    """List all models available in Ollama"""
    import requests

    try:
        response = requests.get(f"{config.base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
    except:
        return []

    return []

def pull_required_models():
    """Pull required models for FinAgentic agent system"""
    import subprocess

    required = [
        "llama3.2:latest",
        "qwen2.5:latest",
        "nomic-embed-text:latest"
    ]

    for model in required:
        print(f"Pulling {model}...")
        subprocess.run(["ollama", "pull", model])
