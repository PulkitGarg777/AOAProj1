# AOA Project 1 - Algorithm Analysis

## Project Overview
This project implements and analyzes two fundamental algorithmic paradigms:
1. **Greedy Algorithm** - Real-world problem solved optimally using greedy approach
2. **Divide and Conquer Algorithm** - Real-world problem solved using D&C technique

## Project Requirements (100 pts total)

### For Each Problem (50 pts each):
- [ ] Identify real problem (10 pts)
- [ ] Abstract the problem (5 pts)
- [ ] Provide algorithm solution (10 pts)
- [ ] Running time analysis (5 pts)
- [ ] Proof of correctness (10 pts)
- [ ] Explain in problem domain language (5 pts)
- [ ] Implementation with experimental verification (5 pts)

## Project Structure

```
AOAProj1/
├── report/                 # LaTeX report files
│   ├── main.tex           # Main document
│   ├── sections/          # Individual sections
│   ├── figures/           # Graphs and diagrams
│   └── bibliography.bib   # References
├── src/                   # Source code
│   ├── greedy/            # Greedy algorithm implementation
│   ├── divide_conquer/    # Divide and Conquer implementation
│   └── utils/             # Common utilities
├── experiments/           # Experimental data and results
│   ├── data/             # Generated test data
│   └── results/          # Experimental results
└── docs/                 # Additional documentation
```

## Getting Started

### Prerequisites
- Python 3.8+ (for implementation)
- LaTeX distribution (or use Overleaf)
- Required Python packages: numpy, matplotlib, pandas

### Installation
```bash
pip install -r requirements.txt
```

### Running Experiments
```bash
# Greedy algorithm experiments
python src/greedy/experiment.py

# Divide and Conquer experiments
python src/divide_conquer/experiment.py
```

## Report Guidelines

### Structure
Follow ACM/IEEE conference paper format with sections:
1. Abstract
2. Introduction
3. Problem 1: Greedy Algorithm
   - Problem Description
   - Problem Abstraction
   - Algorithm Design
   - Running Time Analysis
   - Proof of Correctness
   - Implementation and Experimental Results
4. Problem 2: Divide and Conquer
   - (Same subsections as above)
5. Conclusion
6. References
7. Appendices
   - LLM Usage Log
   - Source Code

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
All LLM interactions must be documented in `docs/llm_usage_log.md` with:
- Tool used
- Prompt
- Response
- How the response was used/modified

## Team Members
- [Add names here]

## License
Academic project for University of Florida - Analysis of Algorithms course
