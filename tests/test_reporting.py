import json

from llm_theory_lab.registry import run_toy_suite
from llm_theory_lab.result import write_report


def test_report_writes_json_and_markdown(tmp_path) -> None:
    result = run_toy_suite(["C02"])
    json_path = tmp_path / "result.json"
    markdown_path = tmp_path / "report.md"
    write_report(result, json_path=json_path, markdown_path=markdown_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload[0]["experiment_id"] == "C02"
    assert payload[0]["status"] == "pass"
    learning = payload[0]["metadata"]["learning"]
    assert learning["lesson_path"] == "docs/course/02-weights-activations-and-logits.md"
    assert "temperature=0" in learning["does_not_show"]

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "C02" in markdown
    assert "温度、softmax 与 token 赔率" in markdown
    assert "怎样解释这次结果" in markdown
    assert "反证条件" in markdown
    assert "不能推出" in markdown
    assert "docs/labs/01-softmax-and-odds.md" in markdown
