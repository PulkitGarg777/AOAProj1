"""
Experimental validation of EV Charging Scheduler.

This script implements PRODUCTION-QUALITY experiments with:
- Real data loading (CSV format)
- Synthetic data with Poisson arrivals
- Baseline comparisons (FCFS, Random)
- 10-trial averaging with reproducible seeds
- Complete visualizations (Gantt, log-log, utilization, comparison)
- CSV output for reproducibility

Machine specs and seeds are logged for full reproducibility.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import sys
import os
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import platform
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Determine project root for consistent paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
FIGURES_DIR = os.path.join(PROJECT_ROOT, 'report', 'figures')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'experiments', 'results')
DATA_DIR = os.path.join(PROJECT_ROOT, 'experiments', 'data')

# Create directories if they don't exist
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

from greedy.algorithm import (
    EVChargingScheduler, 
    ChargingSession, 
    generate_test_data, 
    measure_runtime
)



# ============================================================================
# BASELINE ALGORITHMS (for comparison)
# ============================================================================

class FCFSScheduler:
    """First-Come-First-Served baseline: accept in arrival order."""
    
    def solve(self, sessions: List[ChargingSession]) -> List[ChargingSession]:
        if not sessions:
            return []
        
        # Sort by start time (arrival order)
        sorted_sessions = sorted(sessions, key=lambda s: s.start_time)
        selected = [sorted_sessions[0]]
        last_finish = sorted_sessions[0].finish_time
        
        for session in sorted_sessions[1:]:
            if session.start_time >= last_finish:
                selected.append(session)
                last_finish = session.finish_time
        
        return selected


class RandomScheduler:
    """Random baseline: accept sessions in random order."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def solve(self, sessions: List[ChargingSession]) -> List[ChargingSession]:
        if not sessions:
            return []
        
        # Shuffle randomly
        random.seed(self.seed)
        shuffled = sessions.copy()
        random.shuffle(shuffled)
        
        # Sort by finish time after shuffle
        sorted_sessions = sorted(shuffled, key=lambda s: s.finish_time)
        selected = [sorted_sessions[0]]
        last_finish = sorted_sessions[0].finish_time
        
        for session in sorted_sessions[1:]:
            if session.start_time >= last_finish:
                selected.append(session)
                last_finish = session.finish_time
        
        return selected


# ============================================================================
# DATA LOADING (for real datasets)
# ============================================================================

def load_real_data(filepath: str) -> List[ChargingSession]:
    """
    Load real EV charging data from CSV.
    
    Expected CSV format:
        session_id, start_time, finish_time, [user_id], [energy_kwh]
    
    Or with timestamps:
        session_id, start_timestamp, end_timestamp, ...
    
    Times should be numeric (minutes since midnight or unix timestamp).
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        List of ChargingSession objects
    """
    try:
        df = pd.read_csv(filepath)
        sessions = []
        
        for idx, row in df.iterrows():
            # Handle session_id that might be string or int
            sess_id = row.get('session_id', idx)
            if isinstance(sess_id, str) and sess_id.startswith('SES'):
                sess_id = int(sess_id[3:])  # Extract number from "SES000996"
            else:
                sess_id = int(sess_id) if sess_id else idx
            
            sessions.append(ChargingSession(
                session_id=sess_id,
                start_time=float(row['start_time']),
                finish_time=float(row['finish_time']),
                user_id=str(row.get('user_id', f'user_{idx}')),
                energy_kwh=float(row.get('energy_kwh', 50.0))
            ))
        
        return sessions
    except FileNotFoundError:
        print(f"⚠️  Real data file not found: {filepath}")
        print("    Using synthetic data instead.")
        return []
    except Exception as e:
        print(f"⚠️  Error loading real data: {e}")
        print("    Using synthetic data instead.")
        return []


# ============================================================================
# RUNTIME EXPERIMENTS
# ============================================================================

def run_experiments(sizes: List[int], num_trials: int = 10, 
                   base_seed: int = 42) -> pd.DataFrame:
    """
    Run runtime experiments for different input sizes with multiple trials.
    
    Uses different random seeds per trial for robustness.
    
    Args:
        sizes: List of input sizes to test
        num_trials: Number of trials per size for averaging
        base_seed: Base seed for reproducibility
        
    Returns:
        DataFrame with experimental results
    """
    results = []
    
    for size in sizes:
        print(f"Testing size {size}...")
        runtimes = []
        selected_counts = []
        
        for trial in range(num_trials):
            seed = base_seed + trial
            sessions = generate_test_data(size, seed=seed)
            
            scheduler = EVChargingScheduler()
            runtime = measure_runtime(scheduler, sessions)
            selected = scheduler.solve(sessions)
            
            runtimes.append(runtime)
            selected_counts.append(len(selected))
        
        avg_runtime = np.mean(runtimes)
        std_runtime = np.std(runtimes)
        avg_selected = np.mean(selected_counts)
        
        results.append({
            'size': size,
            'avg_runtime': avg_runtime,
            'std_runtime': std_runtime,
            'min_runtime': min(runtimes),
            'max_runtime': max(runtimes),
            'avg_selected': avg_selected,
            'selection_rate': avg_selected / size * 100
        })
        
        print(f"  Average runtime: {avg_runtime:.6f}s (±{std_runtime:.6f}s)")
        print(f"  Average selected: {avg_selected:.1f} ({avg_selected/size*100:.1f}%)")
    
    return pd.DataFrame(results)


# ============================================================================
# BASELINE COMPARISON
# ============================================================================

def compare_algorithms(sessions: List[ChargingSession], seed: int = 42) -> Dict:
    """Compare greedy, FCFS, and random schedulers."""
    greedy = EVChargingScheduler()
    fcfs = FCFSScheduler()
    random_sched = RandomScheduler(seed=seed)
    
    greedy_selected = greedy.solve(sessions)
    fcfs_selected = fcfs.solve(sessions)
    random_selected = random_sched.solve(sessions)
    
    return {
        'greedy': len(greedy_selected),
        'fcfs': len(fcfs_selected),
        'random': len(random_selected),
        'greedy_util': greedy.compute_utilization(greedy_selected, 1440),
        'fcfs_util': greedy.compute_utilization(fcfs_selected, 1440),
        'random_util': greedy.compute_utilization(random_selected, 1440),
        'greedy_sessions': greedy_selected,
        'fcfs_sessions': fcfs_selected,
        'random_sessions': random_selected
    }


# ============================================================================
# VISUALIZATIONS
# ============================================================================

def plot_gantt_chart(sessions: List[ChargingSession], 
                     selected: List[ChargingSession],
                     title: str = "EV Charging Schedule",
                     save_path: Optional[str] = None):
    """
    Create Gantt chart showing selected vs rejected sessions.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    selected_ids = {s.session_id for s in selected}
    
    # Plot rejected sessions (gray)
    y_rejected = 0
    for session in sessions:
        if session.session_id not in selected_ids:
            ax.barh(y_rejected, session.duration(), 
                   left=session.start_time,
                   height=0.8, 
                   color='lightgray', 
                   alpha=0.5,
                   edgecolor='gray')
            y_rejected += 1
    
    # Plot selected sessions (green)
    y_selected = y_rejected + 1
    for session in selected:
        ax.barh(y_selected, session.duration(), 
               left=session.start_time,
               height=0.8, 
               color='green', 
               alpha=0.7,
               edgecolor='darkgreen',
               linewidth=2)
        y_selected += 1
    
    ax.set_xlabel('Time (minutes since midnight)', fontsize=12)
    ax.set_ylabel('Sessions', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.7, edgecolor='darkgreen', label='Selected'),
        Patch(facecolor='lightgray', alpha=0.5, edgecolor='gray', label='Rejected')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Add hour markers
    hours = [i * 60 for i in range(25)]
    ax.set_xticks(hours)
    ax.set_xticklabels([f"{i}h" if i % 3 == 0 else "" for i in range(25)])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Gantt chart saved to {save_path}")
    
    plt.close()


def plot_runtime_analysis(df: pd.DataFrame, save_path: Optional[str] = None):
    """
    Create comprehensive runtime analysis plots.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Runtime vs n (log-log)
    ax1 = axes[0, 0]
    ax1.errorbar(df['size'], df['avg_runtime'], yerr=df['std_runtime'],
                 marker='o', capsize=5, label='Measured', color='blue', linewidth=2)
    
    # Reference curve: C * n log n
    n_vals = np.array(df['size'])
    # Fit constant C from first few points
    C = df['avg_runtime'].iloc[2] / (n_vals[2] * np.log(n_vals[2]))
    reference = C * n_vals * np.log(n_vals)
    ax1.plot(n_vals, reference, '--', label=f'C·n log n (C={C:.2e})', color='red', linewidth=2)
    
    ax1.set_xlabel('Input Size (n)', fontsize=12)
    ax1.set_ylabel('Runtime (seconds)', fontsize=12)
    ax1.set_title('Runtime vs Input Size', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Plot 2: Normalized runtime (should be flat for O(n log n))
    ax2 = axes[0, 1]
    normalized = df['avg_runtime'] / (df['size'] * np.log(df['size']))
    ax2.plot(df['size'], normalized, marker='s', color='green', linewidth=2)
    ax2.axhline(y=normalized.mean(), color='red', linestyle='--', 
                label=f'Mean: {normalized.mean():.2e}', linewidth=2)
    ax2.set_xlabel('Input Size (n)', fontsize=12)
    ax2.set_ylabel('Runtime / (n log n)', fontsize=12)
    ax2.set_title('Normalized Runtime (Expected: Constant)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Selection rate
    ax3 = axes[1, 0]
    ax3.plot(df['size'], df['selection_rate'], marker='D', color='purple', linewidth=2)
    ax3.set_xlabel('Input Size (n)', fontsize=12)
    ax3.set_ylabel('Selection Rate (%)', fontsize=12)
    ax3.set_title('Percentage of Sessions Selected', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 100)
    
    # Plot 4: Runtime statistics table
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    table_data = []
    for _, row in df.iterrows():
        table_data.append([
            f"{int(row['size'])}",
            f"{row['avg_runtime']*1000:.2f}",
            f"{row['std_runtime']*1000:.2f}",
            f"{int(row['avg_selected'])}"
        ])
    
    table = ax4.table(cellText=table_data,
                     colLabels=['Size', 'Time (ms)', 'Std (ms)', 'Selected'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    ax4.set_title('Runtime Statistics', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Runtime analysis saved to {save_path}")
    
    plt.close()


def plot_algorithm_comparison(comparison_results: List[Dict], 
                              save_path: Optional[str] = None):
    """
    Compare greedy, FCFS, and random algorithms.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Aggregate results
    algorithms = ['Greedy\n(Optimal)', 'FCFS', 'Random']
    counts = [
        np.mean([r['greedy'] for r in comparison_results]),
        np.mean([r['fcfs'] for r in comparison_results]),
        np.mean([r['random'] for r in comparison_results])
    ]
    utils = [
        np.mean([r['greedy_util'] for r in comparison_results]),
        np.mean([r['fcfs_util'] for r in comparison_results]),
        np.mean([r['random_util'] for r in comparison_results])
    ]
    
    # Plot 1: Sessions accepted
    colors = ['green', 'orange', 'gray']
    bars1 = ax1.bar(algorithms, counts, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Sessions Accepted', fontsize=12)
    ax1.set_title('Number of Sessions Scheduled', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, count in zip(bars1, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count:.1f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Plot 2: Utilization
    bars2 = ax2.bar(algorithms, utils, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Utilization (%)', fontsize=12)
    ax2.set_title('Charger Utilization', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 100)
    
    # Add value labels
    for bar, util in zip(bars2, utils):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{util:.1f}%',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Algorithm comparison saved to {save_path}")
    
    plt.close()


def plot_utilization_heatmap(sessions: List[ChargingSession],
                             selected: List[ChargingSession],
                             save_path: Optional[str] = None):
    """
    Create heatmap of charger utilization by hour.
    """
    fig, ax = plt.subplots(figsize=(14, 4))
    
    # Create hourly bins
    hours = 24
    utilization = np.zeros(hours)
    
    for session in selected:
        start_hour = int(session.start_time // 60)
        end_hour = int(session.finish_time // 60)
        
        for h in range(start_hour, min(end_hour + 1, hours)):
            utilization[h] += 1
    
    # Plot heatmap
    im = ax.imshow([utilization], cmap='YlOrRd', aspect='auto', interpolation='nearest')
    
    ax.set_xticks(range(hours))
    ax.set_xticklabels([f"{h}h" for h in range(hours)], rotation=45)
    ax.set_yticks([0])
    ax.set_yticklabels(['Charger'])
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_title('Charger Utilization by Hour', fontsize=14, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Active Sessions', fontsize=12)
    
    # Add value labels
    for h in range(hours):
        ax.text(h, 0, f'{int(utilization[h])}', 
               ha='center', va='center', fontsize=9, fontweight='bold',
               color='white' if utilization[h] > utilization.max()/2 else 'black')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Utilization heatmap saved to {save_path}")
    
    plt.close()


# ============================================================================
# SAVE RESULTS
# ============================================================================

def save_results(df: pd.DataFrame, filename: str = 'greedy_results.csv'):
    """Save experimental results to CSV."""
    filepath = os.path.join(RESULTS_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"💾 Results saved to {filepath}")


def log_environment():
    """Log machine specs and environment for reproducibility."""
    print("\n" + "="*70)
    print("ENVIRONMENT SPECIFICATIONS (for reproducibility)")
    print("="*70)
    print(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {platform.python_version()}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"NumPy: {np.__version__}")
    print(f"Pandas: {pd.__version__}")
    print(f"Matplotlib: {plt.matplotlib.__version__}")
    print(f"Random Seed: 42 (base)")
    print("="*70 + "\n")


def plot_results(df: pd.DataFrame, theoretical_complexity: str = "n log n"):
    """
    Plot experimental results and compare with theoretical complexity.
    
    Args:
        df: DataFrame with experimental results
        theoretical_complexity: String describing theoretical complexity
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Runtime vs Input Size
    ax1.errorbar(df['size'], df['avg_runtime'], yerr=df['std_runtime'],
                 marker='o', capsize=5, label='Experimental')
    ax1.set_xlabel('Input Size (n)', fontsize=12)
    ax1.set_ylabel('Runtime (seconds)', fontsize=12)
    ax1.set_title('Greedy Algorithm Runtime Analysis', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Normalized Runtime (to verify complexity)
    # Adjust this based on your theoretical complexity
    if theoretical_complexity == "n":
        normalized = df['avg_runtime'] / df['size']
        ylabel = 'Runtime / n'
    elif theoretical_complexity == "n log n":
        normalized = df['avg_runtime'] / (df['size'] * np.log(df['size']))
        ylabel = 'Runtime / (n log n)'
    elif theoretical_complexity == "n^2":
        normalized = df['avg_runtime'] / (df['size'] ** 2)
        ylabel = 'Runtime / n²'
    else:
        normalized = df['avg_runtime']
        ylabel = 'Runtime'
    
    ax2.plot(df['size'], normalized, marker='s', color='red')
    ax2.set_xlabel('Input Size (n)', fontsize=12)
    ax2.set_ylabel(ylabel, fontsize=12)
    ax2.set_title(f'Normalized Runtime (Expected: O({theoretical_complexity}))', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=normalized.mean(), color='green', linestyle='--', 
                label=f'Mean: {normalized.mean():.2e}')
    ax2.legend()
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('../../report/figures', exist_ok=True)
    output_path = os.path.join(FIGURES_DIR, 'greedy_runtime.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Figure saved to {output_path}")
    
    plt.show()


def save_results(df: pd.DataFrame, filename: str = 'greedy_results.csv'):
    """
    Save experimental results to CSV file.
    
    Args:
        df: DataFrame with results
        filename: Output filename
    """
    os.makedirs('../../experiments/results', exist_ok=True)
    filepath = os.path.join('../../experiments/results', filename)
    df.to_csv(filepath, index=False)
    print(f"Results saved to {filepath}")


if __name__ == "__main__":
    print("="*70)
    print("EV CHARGING SCHEDULER - EXPERIMENTAL VALIDATION")
    print("="*70)
    
    # Log environment
    log_environment()
    
    # ========================================================================
    # EXPERIMENT 1: Runtime Scaling
    # ========================================================================
    print("\n📊 EXPERIMENT 1: Runtime Scaling Analysis")
    print("="*70)
    
    sizes = [100, 500, 1000, 2000, 4000, 8000, 16000]
    print(f"Testing sizes: {sizes}")
    print(f"Trials per size: 10")
    print("Running experiments...\n")
    
    results_df = run_experiments(sizes, num_trials=10, base_seed=42)
    
    # Display results
    print("\n" + "="*70)
    print("RUNTIME RESULTS")
    print("="*70)
    print(results_df.to_string(index=False))
    
    # Save results
    save_results(results_df, 'ev_charging_runtime.csv')
    
    # Plot runtime analysis
    runtime_fig_path = os.path.join(FIGURES_DIR, 'greedy_runtime.png')
    plot_runtime_analysis(results_df, runtime_fig_path)
    
    # ========================================================================
    # EXPERIMENT 2: Algorithm Comparison (Greedy vs Baselines)
    # ========================================================================
    print("\n📊 EXPERIMENT 2: Algorithm Comparison")
    print("="*70)
    
    comparison_results = []
    test_size = 1000
    num_comparisons = 10
    
    print(f"Comparing algorithms on {num_comparisons} random datasets (n={test_size})...")
    
    for i in range(num_comparisons):
        sessions = generate_test_data(test_size, seed=42 + i)
        result = compare_algorithms(sessions, seed=42 + i)
        comparison_results.append(result)
        
        if i == 0:  # Print first comparison details
            print(f"\nExample comparison:")
            print(f"  Greedy:  {result['greedy']} sessions ({result['greedy_util']:.1f}% util)")
            print(f"  FCFS:    {result['fcfs']} sessions ({result['fcfs_util']:.1f}% util)")
            print(f"  Random:  {result['random']} sessions ({result['random_util']:.1f}% util)")
    
    # Average results
    print(f"\nAverage over {num_comparisons} trials:")
    print(f"  Greedy:  {np.mean([r['greedy'] for r in comparison_results]):.1f} sessions")
    print(f"  FCFS:    {np.mean([r['fcfs'] for r in comparison_results]):.1f} sessions")
    print(f"  Random:  {np.mean([r['random'] for r in comparison_results]):.1f} sessions")
    
    comparison_fig_path = os.path.join(FIGURES_DIR, 'greedy_comparison.png')
    plot_algorithm_comparison(comparison_results, comparison_fig_path)
    
    # ========================================================================
    # EXPERIMENT 3: Domain Visualizations
    # ========================================================================
    print("\n📊 EXPERIMENT 3: Domain Visualizations")
    print("="*70)
    
    # Generate a sample day for visualization
    print("Generating sample day visualization...")
    sample_sessions = generate_test_data(200, seed=42)
    scheduler = EVChargingScheduler()
    selected = scheduler.solve(sample_sessions)
    
    print(f"Sample day: {len(sample_sessions)} requests, {len(selected)} selected")
    print(f"Utilization: {scheduler.compute_utilization(selected, 1440):.1f}%")
    
    # Gantt chart
    gantt_fig_path = os.path.join(FIGURES_DIR, 'greedy_gantt.png')
    plot_gantt_chart(sample_sessions, selected, 
                    "EV Charging Schedule - Sample Day",
                    gantt_fig_path)
    
    # Utilization heatmap
    heatmap_fig_path = os.path.join(FIGURES_DIR, 'greedy_utilization_heatmap.png')
    plot_utilization_heatmap(sample_sessions, selected, heatmap_fig_path)
    
    # ========================================================================
    # EXPERIMENT 4: Correctness Validation
    # ========================================================================
    print("\n📊 EXPERIMENT 4: Correctness Validation")
    print("="*70)
    
    print("Validating solution correctness on random instances...")
    num_validations = 100
    all_valid = True
    
    for i in range(num_validations):
        sessions = generate_test_data(random.randint(10, 500), seed=42 + i)
        scheduler = EVChargingScheduler()
        selected = scheduler.solve(sessions)
        
        if not scheduler.validate_solution(sessions, selected):
            print(f"❌ Validation FAILED on instance {i}")
            all_valid = False
            break
    
    if all_valid:
        print(f"✅ All {num_validations} random instances validated successfully!")
        print("   No overlapping sessions in any solution.")
    
    # ========================================================================
    # EXPERIMENT 5: Real Data (if available)
    # ========================================================================
    print("\n📊 EXPERIMENT 5: Real Data Analysis")
    print("="*70)
    
    # Use absolute path from project root
    real_data_path = os.path.join(DATA_DIR, 'ev_charging_real.csv')
    real_sessions = load_real_data(real_data_path)
    
    if real_sessions:
        print(f"Loaded {len(real_sessions)} sessions from real data")
        scheduler = EVChargingScheduler()
        selected = scheduler.solve(real_sessions)
        
        print(f"Selected: {len(selected)} sessions")
        print(f"Utilization: {scheduler.compute_utilization(selected, 1440):.1f}%")
        
        # Create visualizations for real data
        real_gantt_path = os.path.join(FIGURES_DIR, 'greedy_gantt_real.png')
        plot_gantt_chart(real_sessions, selected,
                        "EV Charging Schedule - Real Data",
                        real_gantt_path)
    else:
        print("No real data file found. Instructions:")
        print(f"  1. Obtain EV charging session data (CSV format)")
        print(f"  2. Save to: {real_data_path}")
        print(f"  3. Format: session_id, start_time, finish_time, [user_id], [energy_kwh]")
        print(f"  4. Re-run this script")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("EXPERIMENTAL VALIDATION COMPLETE")
    print("="*70)
    print("\n✅ Experiments completed successfully!")
    print("\n📊 Generated figures:")
    print("  - greedy_runtime.png (runtime analysis)")
    print("  - greedy_comparison.png (algorithm comparison)")
    print("  - greedy_gantt.png (schedule visualization)")
    print("  - greedy_utilization_heatmap.png (hourly utilization)")
    print("\n💾 Saved data:")
    print("  - experiments/results/ev_charging_runtime.csv")
    print("\n📝 Next steps:")
    print("  1. Review generated figures in report/figures/")
    print("  2. Include figures in LaTeX report")
    print("  3. Add analysis and discussion")
    print("  4. Document this experiment in llm_usage_log.md")
    print("\n🎉 Ready for report writing!")
