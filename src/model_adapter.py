"""Model adapter for local GGUF models via Ollama."""

import os
from typing import Optional

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from langchain_community.llms import LlamaCpp
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False


class ModelAdapter:
    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        num_ctx: int = 8192,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.num_ctx = num_ctx
        self._llm = None

    def load(self):
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("langchain-ollama not installed. Run: uv add langchain-ollama")
        self._llm = ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=self.temperature,
            num_ctx=self.num_ctx,
        )
        return self

    def invoke(self, prompt: str) -> str:
        if self._llm is None:
            self.load()
        return self._llm.invoke(prompt)

    def generate(self, prompt: str, **kwargs) -> str:
        return self.invoke(prompt)


class LlamaCppAdapter:
    def __init__(
        self,
        model_path: str,
        temperature: float = 0.1,
        n_ctx: int = 8192,
        n_gpu_layers: int = 35,
        n_threads: int = 8,
    ):
        self.model_path = model_path
        self.temperature = temperature
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.n_threads = n_threads
        self._llm = None

    def load(self):
        if not LLAMA_CPP_AVAILABLE:
            raise RuntimeError("llama-cpp-python not installed. Run: uv add llama-cpp-python")
        self._llm = LlamaCpp(
            model_path=self.model_path,
            temperature=self.temperature,
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            n_threads=self.n_threads,
        )
        return self

    def invoke(self, prompt: str) -> str:
        if self._llm is None:
            self.load()
        return self._llm.invoke(prompt)

    def generate(self, prompt: str, **kwargs) -> str:
        return self.invoke(prompt)


def create_adapter(
    backend: str = "ollama",
    model_name: Optional[str] = None,
    model_path: Optional[str] = None,
    **kwargs,
) -> ModelAdapter | LlamaCppAdapter:
    if backend == "ollama":
        if model_name is None:
            model_name = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        return ModelAdapter(model_name=model_name, **kwargs)
    elif backend == "llama.cpp":
        if model_path is None:
            raise ValueError("model_path required for llama.cpp backend")
        return LlamaCppAdapter(model_path=model_path, **kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def check_ollama_status(base_url: str = "http://localhost:11434") -> dict:
    import urllib.request
    import json

    try:
        req = urllib.request.Request(f"{base_url}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            models = data.get("models", [])
            return {
                "status": "running",
                "available_models": [m["name"] for m in models],
            }
    except Exception:
        return {
            "status": "not_running",
            "available_models": [],
        }