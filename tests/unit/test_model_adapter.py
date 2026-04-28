from src.model_adapter import check_ollama_status, create_adapter


def test_check_ollama_status_not_running():
    status = check_ollama_status("http://localhost:9999")
    assert status["status"] == "not_running"
    assert status["available_models"] == []


def test_create_adapter_ollama():
    adapter = create_adapter(backend="ollama", model_name="qwen2.5:7b")
    assert adapter.model_name == "qwen2.5:7b"
    assert adapter.base_url == "http://localhost:11434"


def test_create_adapter_default():
    adapter = create_adapter(backend="ollama")
    assert adapter.model_name == "qwen2.5:7b"


def test_create_adapter_invalid_backend():
    try:
        create_adapter(backend="invalid")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Unknown backend" in str(e)


def test_adapter_attributes():
    adapter = create_adapter(
        backend="ollama",
        model_name="qwen2.5:3b",
        temperature=0.2,
        num_ctx=4096,
    )
    assert adapter.model_name == "qwen2.5:3b"
    assert adapter.temperature == 0.2
    assert adapter.num_ctx == 4096


def test_llama_cpp_adapter_requires_model_path():
    try:
        create_adapter(backend="llama.cpp")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "model_path required" in str(e)