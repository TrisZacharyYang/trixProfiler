import re

def detect_issues(blocks, slow_threshold=1.0, mem_threshold=10_000_000):
    issues = []

    for block in blocks:
        name = block["name"]
        code = block.get("code", "")
        duration = block.get("duration", 0)
        mem_peak = block.get("mem_peak", 0)

        # Slow block
        if duration > slow_threshold:
            issues.append({
                "name": name,
                "message": f"Slow block ({duration:.2f}s)"
            })

        # Memory-heavy
        if mem_peak > mem_threshold:
            issues.append({
                "name": name,
                "message": f"High memory usage ({mem_peak/1e6:.2f} MB)"
            })

        # CSV loading
        if "read_csv" in code:
            issues.append({
                "name": name,
                "message": "Detected CSV loading — consider caching"
            })

        # Row-wise apply
        if re.search(r"\.apply\(", code):
            issues.append({
                "name": name,
                "message": "Row-wise apply detected — vectorize if possible"
            })

        # iterrows
        if "iterrows" in code:
            issues.append({
                "name": name,
                "message": "iterrows() detected — vectorize if possible"
            })

        # Nested loops (simple regex)
        if re.search(r"for .* in .*:\s+for .* in .*:", code):
            issues.append({
                "name": name,
                "message": "Nested loop detected — consider vectorization"
            })

    return issues
