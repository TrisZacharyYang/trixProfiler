from profiler import UltraProfiler
from rules import detect_issues
from report import generate_report
import pandas as pd
import time
import os

profiler = UltraProfiler()

with profiler.track("load_data", "pd.read_csv('data.csv')"):
    df = pd.read_csv("data.csv")

with profiler.track("slow_apply", "df.apply(axis=1)"):
    df["c"] = df.apply(lambda x: x["a"] + x["b"], axis=1)

with profiler.track("sleep_test"):
    time.sleep(1.5)

profiler.function_analysis()  # new UltraProfiler method

issues = profiler.detect_patterns()  # replaces rules.detect_issues if you want profiler patterns
issues = sorted(
    issues,
    key=lambda i: next(b['duration'] for b in profiler.blocks if b['name']==i['name']),
    reverse=True
)

print(profiler.detailed_report())  # optional for full internal view
print(generate_report(profiler.blocks, issues))
