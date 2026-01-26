import re

def generate_report(blocks, issues, top_n=3, show_ascii=True):
    """
    Generate a full-featured performance report with ASCII visualizations.

    Sections:
    - Overview
    - Detailed block info (time, memory, functions)
    - Top slow blocks
    - Detected issues
    - Recommendations
    """

    lines = []

    # Overview
    lines.append("📊 Advanced Script Performance Report\n")
    total_time = sum(b["duration"] for b in blocks)
    total_mem = sum(b["mem_peak"] for b in blocks)
    lines.append(f"Total blocks profiled: {len(blocks)}")
    lines.append(f"Total execution time: {total_time:.2f}s")
    lines.append(f"Total peak memory: {total_mem/1e6:.2f} MB\n")

    # Detailed block info
    lines.append(f"{'Block':25} {'Time(s)':>10} {'PeakMem(MB)':>12} {'Funcs':>6} {'Status':>15}")
    lines.append("-"*75)

    for b in blocks:
        funcs = b.get("functions_detected", 0)
        status = ""
        if b["duration"] > 1.0:
            status += "⏱ Slow "
        if b["mem_peak"] > 10_000_000:
            status += "💾 Heavy"
        line = f"{b['name']:25} {b['duration']:10.2f} {b['mem_peak']/1e6:12.2f} {funcs:6} {status:>15}"
        lines.append(line)

        # ASCII bar visualization
        if show_ascii:
            time_bar = "█" * int(b["duration"]*10)
            mem_bar = "▓" * int(b["mem_peak"]/1e6/2)
            lines.append(f"    Time: {time_bar} ({b['duration']:.2f}s)")
            lines.append(f"    Mem : {mem_bar} ({b['mem_peak']/1e6:.2f} MB)")

    # Top N slow blocks
    lines.append("\n🔥 Top slow blocks")
    top_slow = sorted(blocks, key=lambda b: b["duration"], reverse=True)[:top_n]
    for b in top_slow:
        lines.append(f"- {b['name']} ({b['duration']:.2f}s)")

    # Detected issues
    lines.append("\n⚠️ Detected Issues")
    if not issues:
        lines.append("No major issues detected ✅")
    else:
        for issue in issues:
            lines.append(f"- {issue['name']}: {issue['message']}")

    # Recommendations
    lines.append("\n💡 Recommendations:")
    for b in blocks:
        code = b.get("code", "")
        recs = []
        if "apply(" in code:
            recs.append("Vectorize `.apply()` operations")
        if "iterrows" in code:
            recs.append("Replace `.iterrows()` with vectorized ops")
        if "read_csv" in code:
            recs.append("Cache CSV reads")
        if re.search(r"for .* in .*:\s+for .* in .*:", code):
            recs.append("Flatten nested loops with vectorization")

        if recs:
            lines.append(f"- {b['name']}: " + "; ".join(recs))

    return "\n".join(lines)
