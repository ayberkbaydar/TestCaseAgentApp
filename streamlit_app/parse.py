import re

def preprocess_output(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith("### "):
            continue
        if line.strip() == "---":
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

def parse_test_cases(raw_output: str) -> list:
    raw_output = preprocess_output(raw_output)

    pattern_full = re.compile(
        r"Title\s*:\s*(.*?)\n"
        r"Preconditions\s*:\s*(.*?)\n(?:Steps|Step)\s*:\s*(.*?)\n"
        r"Expected\s*Result\s*:\s*(.*?)(?=\nTitle\s*:|\Z)",
        re.DOTALL | re.IGNORECASE
    )

    pattern_partial = re.compile(
        r"Title\s*:\s*(.*?)\n"
        r"Preconditions\s*:\s*(.*?)\n(?:Steps|Step)\s*:\s*(.*?)(?=\nTitle\s*:|\Z)",
        re.DOTALL | re.IGNORECASE
    )

    structured = []
    titles_captured = set()

    for match in pattern_full.findall(raw_output):
        title = match[0].strip()
        titles_captured.add(title)
        structured.append({
            "test_name": title,
            "preconditions": match[1].strip(),
            "steps": match[2].strip(),
            "expected_result": match[3].strip()
        })

    for match in pattern_partial.findall(raw_output):
        title = match[0].strip()
        if title not in titles_captured:
            structured.append({
                "test_name": title,
                "preconditions": match[1].strip(),
                "steps": match[2].strip(),
                "expected_result": ""
            })

    return structured
