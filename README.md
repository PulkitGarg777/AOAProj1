# AOA Project 1 - Algorithm Analysis

## Team Members
- Pulkit Garg (UFID: 31125456)
- Radhe Sharma (UFID: )

## Project Overview

This project implements and analyzes two fundamental algorithmic paradigms:

### Problem 1: Greedy Algorithm - EV Charging Station Scheduler
- **Real-World Problem:** Electric Vehicle charging station session scheduling
- **Algorithm:** Activity Selection using earliest-finish-time greedy strategy
- **Complexity:** O(n log n)
- **Dataset:** 5,449 real charging sessions from 5,000 EV stations
- **Status:** Implementation complete, experiments complete, LaTeX report complete

### Problem 2: Divide and Conquer Algorithm 
- **Status:** To be implemented

## Project Structure

```
AOAProj1/
├── report/                                    # LaTeX report files
│   ├── main.tex                              # Complete report (410 lines)
│   ├── bibliography.bib                      # References
│   └── figures/                              # Generated visualizations
│       ├── greedy_strategy_comparison.png    # 6-subplot strategy analysis
│       └── greedy_runtime_comparison.png     # 6-subplot runtime analysis
│
├── src/                                       # Source code
│   ├── greedy/
│   │   ├── algorithm.py                      # Core EV scheduling algorithm
│   │   ├── alternative_strategies.py         # 5 alternative greedy strategies
│   │   ├── experiment.py                     # Experimental framework (deleted old version)
│   │   ├── visualize_strategies.py           # Strategy comparison visualization
│   │   ├── visualize_runtime_comparison.py   # Runtime analysis visualization
│   │   └── example_activity_selection.py     # Original template
│   │
│   ├── divide_conquer/
│   │   ├── algorithm.py                      # Template
│   │   ├── experiment.py                     # Template
│   │   └── example_binary_search.py          # Template
│   │
│   └── utils/
│       ├── helpers.py                        # Common utilities
│       └── transform_station_to_sessions.py  # Data transformer
│
├── experiments/                               # Experimental data
│   └── data/
│       ├── ev_charging_sessions_full.csv     # 5,449 sessions (all attributes)
│       ├── ev_charging_real.csv              # 5,449 sessions (minimal format)
│       └── detailed_ev_charging_stations.csv # Original 5,000 stations
│
└── docs/                                      # Documentation
    └── llm_usage_log.md                      # Complete LLM usage documentation (15 interactions)
```

## Getting Started

### Prerequisites

- Python 3.11+
- Required packages: numpy, pandas, matplotlib

### Installation

```bash
pip install -r requirements.txt
```

### Running the Greedy Algorithm Analysis

```bash
# Run alternative strategies comparison
cd src/greedy
python alternative_strategies.py

# Generate strategy comparison visualization
python visualize_strategies.py

# Generate runtime comparison visualization
python visualize_runtime_comparison.py
```

## Key Results (Problem 1: Greedy Algorithm)

### Strategy Comparison

Our analysis compared 6 different greedy strategies:

1. **Optimal (Earliest Finish Time):** 100% optimal - Provably correct
2. **Shortest Duration First:** 94% of optimal
3. **Latest Start Time:** 100% of optimal (lucky on this dataset, no theoretical guarantee)
4. **Fewest Conflicts:** 99.6% of optimal, but O(n³) complexity
5. **Max Energy Density:** 95% of optimal
6. **FCFS (Earliest Start):** Only 52% of optimal - Worst performance

**Key Insight:** The choice of greedy criterion is critical. Earliest-finish-time has both mathematical proof and empirical validation of optimality.

### Runtime Analysis

- **Optimal Strategy:** 1.47 ms for n=5,000 sessions with O(n log n) complexity
- **FCFS Strategy:** 1.42 ms (fast but only 52% optimal)
- **Fewest Conflicts:** 20,730 ms for n=500 (14,055× slower with O(n³) complexity)

**Key Insight:** The optimal solution is also computationally efficient - correctness does not sacrifice speed.

## Report Guidelines

The LaTeX report (`report/main.tex`) contains:

- Complete Problem 1 (Greedy Algorithm) with all 7 required sections
- Formal proof of correctness using exchange argument
- Two comprehensive experimental analyses (strategy comparison + runtime analysis)
- Professional ACM conference paper formatting

### LaTeX Compilation

Using Overleaf (recommended) or local:

```bash
cd report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## LLM Usage Tracking

All LLM interactions are documented in `docs/llm_usage_log.md` with:

- Tool used (GitHub Copilot)
- Complete prompts and responses
- How responses were used/modified
- Verification methods
- 15 interactions fully documented
