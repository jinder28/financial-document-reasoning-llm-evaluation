from app.scoring.metric_calculator import MetricCalculator


def test_metric_calculator_condition_accuracy():
    records = [
        {"condition": "Long_Context", "is_correct": "YES", "expected_label": "Supported", "predicted_label": "Supported"},
        {"condition": "Long_Context", "is_correct": "NO", "expected_label": "Supported", "predicted_label": "Contradicted"},
    ]
    metrics = MetricCalculator().calculate_condition_metrics(records)
    assert metrics[0]["accuracy"] == 0.5
