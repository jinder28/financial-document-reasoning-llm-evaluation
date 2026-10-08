from app.config.runtime_settings import ExperimentRuntimeSettings


def test_runtime_settings_loads_defaults():
    settings = ExperimentRuntimeSettings.from_environment()
    assert settings.openai_model_id
    assert settings.rag_top_k == 8
