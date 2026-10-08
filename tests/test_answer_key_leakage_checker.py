from app.validation.answer_key_leakage_checker import AnswerKeyLeakageChecker


def test_leakage_checker_allows_model_prompt_without_answer_key_fields():
    checker = AnswerKeyLeakageChecker()
    checker.assert_model_payload_contains_no_scoring_fields(
        {"messages": [{"role": "user", "content": "Classify this SEC claim."}]}
    )


def test_leakage_checker_blocks_expected_label_field():
    checker = AnswerKeyLeakageChecker()
    try:
        checker.assert_model_payload_contains_no_scoring_fields({"expected_label": "Supported"})
    except ValueError as error:
        assert "expected_label" in str(error)
    else:
        raise AssertionError("Expected leakage checker to block expected_label")
