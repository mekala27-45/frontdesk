from pathlib import Path
import pytest
from scripts.check_no_em_dash import violations
from scripts.check_published_numbers import render

def test_punctuation_clean_violation_empty(tmp_path):
    path=tmp_path/"template.json"
    path.write_text('{"reply":"Hello"}')
    assert not violations(tmp_path,["template.json"])
    path.write_text(chr(0x2014),encoding="utf-8")
    assert violations(tmp_path,["template.json"])==["template.json"]
    with pytest.raises(ValueError):
        violations(tmp_path,[])

def test_renderer_clean_violation_empty(tmp_path):
    directory=tmp_path/"docs/templates"
    directory.mkdir(parents=True)
    (directory/"README.md").write_text("Measured $count")
    assert not render(tmp_path,{"count":"1"},True)
    assert not render(tmp_path,{"count":"1"})
    (tmp_path/"README.md").write_text("Measured 1 plus an invented claim")
    assert render(tmp_path,{"count":"1"})==["README.md"]
    with pytest.raises(ValueError):
        render(tmp_path,{})
    with pytest.raises(ValueError):
        render(tmp_path/"missing",{"count":"1"})

