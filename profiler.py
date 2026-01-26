import time
import tracemalloc
import re
import sys
from contextlib import contextmanager
from collections import defaultdict
import inspect
import math

class UltraProfiler:
    """
    trixProfiler
    """

    def __init__(self):
        self.blocks = []  # Stores all profiled blocks
        self.summary_stats = {}
        self.function_stats = defaultdict(list)  # Stores function-level times
        self.csv_loads = set()
        self.block_order = 0  # Tracks execution order

    # Context Manager for Profiling
    @contextmanager
    def track(self, name, code_snippet=""):
        """
        Profile a block of code with time, memory, and function-level analysis.
        """
        self.block_order += 1
        tracemalloc.start()
        start_mem, _ = tracemalloc.get_traced_memory()
        start_time = time.time()

        # Optional: capture functions defined inside block
        funcs_before = set(inspect.getmembers(sys.modules[__name__], inspect.isfunction))

        yield

        end_time = time.time()
        end_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        funcs_after = set(inspect.getmembers(sys.modules[__name__], inspect.isfunction))
        new_funcs = funcs_after - funcs_before

        self.blocks.append({
            "name": name,
            "order": self.block_order,
            "code": code_snippet,
            "duration": end_time - start_time,
            "mem_used": end_mem - start_mem,
            "mem_peak": peak_mem,
            "functions_defined": [f[0] for f in new_funcs],
        })

    # Function-Level Stats
    def function_analysis(self):
        """
        Analyze all functions defined inside blocks for time estimates.
        Placeholder for future line-by-line profiling.
        """
        for block in self.blocks:
            funcs = block.get("functions_defined", [])
            for f in funcs:
                self.function_stats[f].append(block["duration"] / max(len(funcs), 1))

    # Pattern Detection
    def detect_patterns(self):
        """
        Detect common inefficiencies and repeated I/O in blocks.
        Returns list of issues with block name and description.
        """
        issues = []
        seen_csv = set()

        for block in self.blocks:
            name = block["name"]
            code = block.get("code", "")
            duration = block.get("duration", 0)
            mem_peak = block.get("mem_peak", 0)

            # Slow block
            if duration > 1.0:
                issues.append({"name": name, "message": f"Slow block ({duration:.2f}s)"})

            # Memory heavy
            if mem_peak > 10_000_000:
                issues.append({"name": name, "message": f"High memory usage ({mem_peak/1e6:.2f} MB)"})

            # CSV repeated load detection
            if "read_csv" in code:
                if code not in seen_csv:
                    issues.append({"name": name, "message": "Detected CSV loading — consider caching"})
                    seen_csv.add(code)

            # Row-wise apply
            if re.search(r"\.apply\(", code):
                issues.append({"name": name, "message": "Row-wise apply detected — vectorize if possible"})

            # Iterrows
            if "iterrows" in code:
                issues.append({"name": name, "message": "iterrows() detected — vectorize if possible"})

            # Nested loops
            if re.search(r"for .* in .*:\s+for .* in .*:", code):
                issues.append({"name": name, "message": "Nested loop detected — consider vectorization"})

            # Large objects (dummy check for arrays/lists over 100k)
            if re.search(r"range\(\d{5,}\)", code):
                issues.append({"name": name, "message": "Large iterable detected — memory intensive"})

            # Logging heavy operations
            if re.search(r"print\(", code):
                issues.append({"name": name, "message": "Print statements may slow performance in loops"})

        return issues

    # Summary Stats
    def summarize(self):
        """
        Compute aggregated statistics across blocks.
        """
        if not self.blocks:
            return {}

        total_time = sum(b["duration"] for b in self.blocks)
        total_mem = sum(b["mem_peak"] for b in self.blocks)
        slowest = max(self.blocks, key=lambda b: b["duration"])
        heaviest = max(self.blocks, key=lambda b: b["mem_peak"])
        avg_time = total_time / len(self.blocks)
        median_time = self._median([b["duration"] for b in self.blocks])
        avg_mem = total_mem / len(self.blocks)
        median_mem = self._median([b["mem_peak"] for b in self.blocks])

        self.summary_stats = {
            "total_time": total_time,
            "total_mem": total_mem,
            "slowest_block": slowest["name"],
            "heaviest_block": heaviest["name"],
            "average_time": avg_time,
            "median_time": median_time,
            "average_mem": avg_mem,
            "median_mem": median_mem
        }
        return self.summary_stats

    # Utility Functions
    def _median(self, data):
        """Compute median of a list"""
        if not data:
            return 0
        data = sorted(data)
        n = len(data)
        if n % 2 == 0:
            return (data[n//2 - 1] + data[n//2]) / 2
        return data[n//2]

    def top_k_blocks(self, k=3, by="duration"):
        """Return top k blocks by duration or memory"""
        if by == "duration":
            return sorted(self.blocks, key=lambda b: b["duration"], reverse=True)[:k]
        elif by == "mem":
            return sorted(self.blocks, key=lambda b: b["mem_peak"], reverse=True)[:k]
        return self.blocks

    # ASCII Visualization
    def ascii_bars(self, block, scale_time=10, scale_mem=2_000_000):
        """
        Generate ASCII bars for a single block's time and memory.
        """
        time_len = int(block["duration"] * scale_time)
        mem_len = int(block["mem_peak"] / scale_mem)
        return "Time: " + "█" * time_len + f" ({block['duration']:.2f}s)\n" + \
               "Mem : " + "▓" * mem_len + f" ({block['mem_peak']/1e6:.2f}MB)"

    # Detailed Block Report
    def detailed_report(self):
        """
        Return a detailed string report for debugging or logging.
        """
        lines = []
        lines.append(f"Total blocks: {len(self.blocks)}\n")
        for b in self.blocks:
            lines.append(f"Block: {b['name']}")
            lines.append(f"  Duration: {b['duration']:.2f}s, Peak Memory: {b['mem_peak']/1e6:.2f} MB")
            lines.append(f"  Functions Defined: {', '.join(b.get('functions_defined', []))}")
            lines.append(self.ascii_bars(b))
            lines.append("-"*50)
        return "\n".join(lines)
