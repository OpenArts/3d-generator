from ai.prompt import analyze_prompt

def test_prompt():
    a = analyze_prompt("small realistic wooden crate")
    assert a.category == "furniture"
