from app.prompts.prompt_payload_writer import PromptPayloadWriter


def test_prompt_payload_writer_builds_descriptive_payload():
    payload = PromptPayloadWriter().build_model_request_payload(
        run_id="MR001_LC",
        case_id="F001_C01",
        condition="Long_Context",
        system_instruction="system",
        user_prompt="user",
    )
    assert payload["run_id"] == "MR001_LC"
    assert payload["messages"][1]["content"] == "user"
