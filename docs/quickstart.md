# Quick Start Guide

## Initial Setup

### 1. Install Python Dependencies
```powershell
# Navigate to project directory
cd c:\Users\pulki\Desktop\Pulkit_work\UF_Academics\Sem2\AOA\AOAProj1

# Install required packages
pip install -r requirements.txt
```

### 2. Set Up LaTeX (Choose One)

**Option A: Overleaf (Recommended)**
1. Go to https://www.overleaf.com
2. Create a free account
3. Create new project → Upload Project
4. Upload the `report/` folder contents
5. You can now collaborate and compile online

**Option B: Local LaTeX**
1. Install MiKTeX (Windows): https://miktex.org/download
2. Install TeXstudio (editor): https://www.texstudio.org/
3. Open `report/main.tex` in TeXstudio
4. Press F5 to compile

## Working on the Project

### Step 1: Choose Your Problems
1. Review `docs/problem_ideas.md` for suggestions
2. Select one greedy and one divide-and-conquer problem
3. Make sure they're from real-world domains, not just from algorithms textbooks

### Step 2: Implement Greedy Algorithm
```powershell
# Edit the algorithm
code src/greedy/algorithm.py

# Implement:
# - generate_test_data() function
# - GreedyAlgorithm.solve() method
# - GreedyAlgorithm.validate_solution() method

# Test your implementation
python src/greedy/algorithm.py

# Run experiments
python src/greedy/experiment.py
```

### Step 3: Implement Divide-and-Conquer Algorithm
```powershell
# Edit the algorithm
code src/divide_conquer/algorithm.py

# Implement:
# - generate_test_data() function
# - DivideConquerAlgorithm._divide_conquer() method
# - DivideConquerAlgorithm.validate_solution() method

# Test your implementation
python src/divide_conquer/algorithm.py

# Run experiments
python src/divide_conquer/experiment.py
```

### Step 4: Write the Report
1. Open `report/main.tex` in Overleaf or TeXstudio
2. Fill in each section:
   - Replace [TODO] comments with your content
   - Add your problem descriptions
   - Write formal abstractions
   - Include pseudocode using the algorithm environment
   - Add proofs of correctness
   - Include experimental graphs (automatically generated)

### Step 5: Document LLM Usage
Every time you use an LLM (ChatGPT, Claude, Copilot, etc.):
1. Open `docs/llm_usage_log.md`
2. Add a new entry with:
   - Date and purpose
   - Exact prompt
   - Full response
   - How you used/modified it
   - How you verified correctness

## Generating Final Report

### Using Overleaf
1. Click "Recompile" button
2. Download PDF when ready

### Using Local LaTeX
```powershell
cd report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Common Issues and Solutions

### Python Import Errors
```powershell
# Make sure you're in the project root
cd c:\Users\pulki\Desktop\Pulkit_work\UF_Academics\Sem2\AOA\AOAProj1

# Install packages
pip install numpy matplotlib pandas
```

### LaTeX Compilation Errors
- Make sure all required packages are installed (algorithm, algpseudocode, etc.)
- Check for missing $ symbols around math expressions
- Ensure all { } are balanced

### Graphs Not Showing
- Make sure `report/figures/` directory exists
- Run experiments before compiling LaTeX
- Check file paths in experiment.py

## Project Timeline Suggestion

**Week 1:**
- Day 1-2: Choose problems, understand requirements
- Day 3-4: Implement greedy algorithm
- Day 5-7: Implement divide-and-conquer algorithm

**Week 2:**
- Day 1-2: Run experiments, generate graphs
- Day 3-4: Write proofs and analysis
- Day 5-6: Complete LaTeX report
- Day 7: Final review, proofread, submit

## Tips for Success

1. **Start Early**: Don't wait until the last minute
2. **Test Incrementally**: Test your code with small inputs first
3. **Document As You Go**: Add LLM usage entries immediately
4. **Verify Everything**: Don't trust LLM-generated proofs blindly
5. **Use Version Control**: Commit changes regularly to git
6. **Collaborate**: If working in a group, divide work clearly
7. **Ask for Help**: Use office hours if stuck

## Useful Commands

```powershell
# Run greedy experiments
python src/greedy/experiment.py

# Run D&C experiments
python src/divide_conquer/experiment.py

# Check Python syntax
python -m py_compile src/greedy/algorithm.py

# Format Python code
pip install black
black src/

# View project structure
tree /F
```

## Resources

- **LaTeX Help**: https://www.overleaf.com/learn
- **Algorithm Pseudocode**: Search "latex algorithm2e examples"
- **Python Plotting**: https://matplotlib.org/stable/gallery/
- **Master Theorem**: CLRS Chapter 4
- **Greedy Proofs**: Kleinberg & Tardos Chapter 4

## Need Help?

1. Check `docs/problem_ideas.md` for problem suggestions
2. Review `docs/checklist.md` to track progress
3. Look at example code in `src/` directories
4. Refer to course materials and textbooks
5. Document all external help in LLM usage log

Good luck with your project! 🚀
