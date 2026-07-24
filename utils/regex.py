import re

def extract_duration_months(duration: str | None) -> int | None:
    if not duration:
        return None

    match = re.search(r"\d+", duration)
    return int(match.group()) if match else None