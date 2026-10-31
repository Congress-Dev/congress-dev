import pytest

from congress_parser.prompt_runners import utils
from congress_parser.prompt_runners.utils import (
    MODEL_ENV_VARS,
    openrouter_model,
    resolve_model,
)


def test_unset_model_raises_naming_env_var(monkeypatch):
    monkeypatch.delenv("LLM_MODEL_BILL_TAGGER", raising=False)
    with pytest.raises(ValueError, match="LLM_MODEL_BILL_TAGGER"):
        resolve_model("bill_tagger")


def test_env_and_override(monkeypatch):
    monkeypatch.setenv("LLM_MODEL_BILL_TAGGER", " vendor/a ")
    assert resolve_model("bill_tagger") == "vendor/a"
    assert resolve_model("bill_tagger", "vendor/b") == "vendor/b"


def test_every_use_case_has_distinct_env_var():
    assert len(set(MODEL_ENV_VARS.values())) == len(MODEL_ENV_VARS)


def test_openrouter_prefix_and_ollama_rejected():
    assert openrouter_model("vendor/m") == "openrouter/vendor/m"
    assert openrouter_model("openrouter/vendor/m") == "openrouter/vendor/m"
    with pytest.raises(ValueError, match="Ollama"):
        openrouter_model("ollama/qwen2.5:32b")


def test_run_query_uses_openrouter_without_ollama_params(monkeypatch):
    captured = {}

    class Resp:
        usage = None

    def fake_completion(**kwargs):
        captured.update(kwargs)
        return Resp()

    monkeypatch.setattr(utils, "completion", fake_completion)
    utils.run_query("hi", "vendor/m")
    assert captured["model"] == "openrouter/vendor/m"
    assert captured["response_format"] == {"type": "json_object"}
    assert not {"api_base", "format", "num_ctx"} & captured.keys()
    utils.run_query("hi", "vendor/m", json=False)
    assert captured["response_format"] is None
