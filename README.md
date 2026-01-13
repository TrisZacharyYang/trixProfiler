# trixProfiler

This is a performance analysis app made by Tris Yang. Through the use of graphical interface, it allows the user to profile python codes at code-block level, detect bottleneck, memory-intensive tasks and inefficient codes. It also provides insightful on optimizations. 

This project focuses on optimizations and efficiency.

-------------------------------------------------------------

FEATURES

Tracks the following: 
- Block-level execution time
- Peak memory usage
- Slowest blocks, memory-heavy blocks and averages
- Loading multiple CSVs

Detect inefficient coding patterns such as:
- Dataframe apply with axis = 1
- iterrows usage
- Nested loops
- Large iterable creation
  
Addition: It also generate optimization recommandation 

-------------------------------------------------------------

PHILOSOPHY

I attempted to combine dynamic profiling and static analysis to provide unqiue ideas of any Python scripts. This program design was inspired by modern IDE AI profilers.

-------------------------------------------------------------

STRUCTURE

trixProfiler
--- profiler.py
--- report.py

