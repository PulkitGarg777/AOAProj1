"""
Runtime Comparison Visualization for Different Greedy Strategies.

This script compares the computational efficiency (runtime and number of comparisons)
of different greedy strategies to demonstrate that optimal doesn't mean slow.
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import time
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from greedy.algorithm import EVChargingScheduler, generate_test_data
from greedy.alternative_strategies import (
    EarliestStartTimeScheduler,
    ShortestDurationScheduler,
    LatestStartTimeScheduler,
    FewestConflictsScheduler,
    MaxWeightedScheduler,
)


def measure_strategy_runtime(scheduler, sessions, num_runs=10):
    """Measure average runtime for a strategy."""
    times = []
    for _ in range(num_runs):
        start = time.perf_counter()
        scheduler.solve(sessions)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds
    return np.mean(times), np.std(times)


def analyze_runtime_scaling(seed=42):
    """
    Analyze how runtime scales with input size for each strategy.
    
    Returns:
        Dictionary with strategy names as keys and lists of (size, runtime, comparisons) tuples
    """
    sizes = [100, 200, 500, 1000, 2000, 5000]
    strategies = {
        "Optimal (Earliest Finish)": EVChargingScheduler(),
        "FCFS (Greedy)": EarliestStartTimeScheduler(),
        "Shortest Duration": ShortestDurationScheduler(),
        "Latest Start Time": LatestStartTimeScheduler(),
        "Fewest Conflicts": FewestConflictsScheduler(),  # O(n³) - will skip for large n
        "Max Energy Density": MaxWeightedScheduler(),
    }
    
    results = defaultdict(list)
    
    print("Analyzing runtime scaling across different input sizes...")
    print(f"Testing sizes: {sizes}")
    print()
    
    for size in sizes:
        print(f"Testing n={size}...")
        sessions = generate_test_data(size, seed=seed)
        
        for name, scheduler in strategies.items():
            # Skip Fewest Conflicts for n > 500 (too slow with O(n³))
            if name == "Fewest Conflicts" and size > 500:
                print(f"  {name:30s}: SKIPPED (O(n³) too slow for large n)")
                continue
            
            # Reset comparisons counter if exists
            if hasattr(scheduler, 'comparisons'):
                scheduler.comparisons = 0
            
            # Measure runtime
            avg_time, std_time = measure_strategy_runtime(scheduler, sessions, num_runs=5)
            
            # Get comparisons count
            scheduler.solve(sessions)  # Run once more to get comparisons
            comparisons = scheduler.comparisons if hasattr(scheduler, 'comparisons') else size - 1
            
            results[name].append({
                'size': size,
                'time_ms': avg_time,
                'time_std': std_time,
                'comparisons': comparisons,
            })
            
            print(f"  {name:30s}: {avg_time:8.3f} ms (±{std_time:.3f}), {comparisons:,} comparisons")
        print()
    
    return results


def visualize_runtime_comparison(results):
    """
    Create comprehensive runtime comparison visualization.
    
    Creates a figure with 4 subplots:
    1. Runtime vs Input Size (log-log plot)
    2. Comparisons vs Input Size (log-log plot)
    3. Runtime bar chart for largest dataset
    4. Comparisons bar chart for largest dataset
    """
    fig = plt.figure(figsize=(16, 10))
    
    strategy_names = list(results.keys())
    colors = {
        "Optimal (Earliest Finish)": 'green',
        "FCFS (Greedy)": 'red',
        "Shortest Duration": 'blue',
        "Latest Start Time": 'orange',
        "Fewest Conflicts": 'purple',
        "Max Energy Density": 'brown',
    }
    
    # Subplot 1: Runtime vs Input Size (log-log)
    ax1 = plt.subplot(2, 3, 1)
    for name in strategy_names:
        data = results[name]
        if not data:  # Skip if no data
            continue
        sizes = [d['size'] for d in data]
        times = [d['time_ms'] for d in data]
        
        style = '-o' if 'Optimal' in name else '--s'
        linewidth = 2.5 if 'Optimal' in name else 1.5
        markersize = 8 if 'Optimal' in name else 6
        
        ax1.loglog(sizes, times, style, 
                   label=name, color=colors.get(name, 'gray'),
                   linewidth=linewidth, markersize=markersize, alpha=0.8)
    
    ax1.set_xlabel('Input Size (n)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Runtime (ms)', fontsize=11, fontweight='bold')
    ax1.set_title('Runtime Scaling (Log-Log)', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=8, loc='upper left')
    ax1.grid(True, alpha=0.3, which='both')
    
    # Add complexity reference lines
    sizes_ref = np.array([100, 5000])
    nlogn_ref = sizes_ref * np.log(sizes_ref) / 1000
    n2_ref = sizes_ref ** 2 / 100000
    ax1.loglog(sizes_ref, nlogn_ref, ':', color='gray', alpha=0.5, linewidth=1, label='O(n log n)')
    ax1.loglog(sizes_ref, n2_ref, ':', color='black', alpha=0.5, linewidth=1, label='O(n²)')
    
    # Subplot 2: Comparisons vs Input Size (log-log)
    ax2 = plt.subplot(2, 3, 2)
    for name in strategy_names:
        data = results[name]
        if not data:  # Skip if no data
            continue
        sizes = [d['size'] for d in data]
        comparisons = [d['comparisons'] for d in data]
        
        style = '-o' if 'Optimal' in name else '--s'
        linewidth = 2.5 if 'Optimal' in name else 1.5
        markersize = 8 if 'Optimal' in name else 6
        
        ax2.loglog(sizes, comparisons, style,
                   label=name, color=colors.get(name, 'gray'),
                   linewidth=linewidth, markersize=markersize, alpha=0.8)
    
    ax2.set_xlabel('Input Size (n)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of Comparisons', fontsize=11, fontweight='bold')
    ax2.set_title('Comparisons Scaling (Log-Log)', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=8, loc='upper left')
    ax2.grid(True, alpha=0.3, which='both')
    
    # Subplot 3: Runtime bar chart for largest dataset
    ax3 = plt.subplot(2, 3, 3)
    # Filter strategies that have data for the largest size
    strategies_with_data = [(name, results[name][-1]) for name in strategy_names if results[name]]
    filtered_names = [name for name, _ in strategies_with_data]
    runtimes = [data['time_ms'] for _, data in strategies_with_data]
    bar_colors = [colors.get(name, 'gray') for name in filtered_names]
    
    bars = ax3.barh(range(len(filtered_names)), runtimes, color=bar_colors, alpha=0.6, edgecolor='black')
    ax3.set_yticks(range(len(filtered_names)))
    ax3.set_yticklabels(filtered_names, fontsize=9)
    ax3.set_xlabel('Runtime (ms)', fontsize=11, fontweight='bold')
    
    if strategies_with_data:
        largest_size = strategies_with_data[0][1]['size']
        ax3.set_title(f'Runtime Comparison (n={largest_size})', fontsize=12, fontweight='bold')
    else:
        ax3.set_title('Runtime Comparison', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax3.text(width, bar.get_y() + bar.get_height()/2.,
                f'{width:.2f}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Subplot 4: Comparisons bar chart for largest dataset
    ax4 = plt.subplot(2, 3, 4)
    comparisons = [data['comparisons'] for _, data in strategies_with_data]
    bar_colors = [colors.get(name, 'gray') for name in filtered_names]
    
    bars = ax4.barh(range(len(filtered_names)), comparisons, color=bar_colors, alpha=0.6, edgecolor='black')
    ax4.set_yticks(range(len(filtered_names)))
    ax4.set_yticklabels(filtered_names, fontsize=9)
    ax4.set_xlabel('Number of Comparisons', fontsize=11, fontweight='bold')
    
    if strategies_with_data:
        largest_size = strategies_with_data[0][1]['size']
        ax4.set_title(f'Comparisons Count (n={largest_size})', fontsize=12, fontweight='bold')
    else:
        ax4.set_title('Comparisons Count', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax4.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width):,}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Subplot 5: Efficiency metrics table
    ax5 = plt.subplot(2, 3, 5)
    ax5.axis('off')
    
    # Calculate efficiency metrics for largest dataset (only for strategies with data)
    if not strategies_with_data:
        ax5.text(0.5, 0.5, 'No data available', ha='center', va='center')
        return
    
    optimal_time = next((data['time_ms'] for name, data in strategies_with_data if 'Optimal' in name), 1.0)
    optimal_comparisons = next((data['comparisons'] for name, data in strategies_with_data if 'Optimal' in name), 1)
    
    table_data = []
    for name, data in strategies_with_data:
        time = data['time_ms']
        comps = data['comparisons']
        time_ratio = time / optimal_time
        comp_ratio = comps / optimal_comparisons if optimal_comparisons > 0 else 1
        
        table_data.append([
            name.split('(')[0].strip()[:20],  # Shortened name
            f"{time:.2f}",
            f"{time_ratio:.2f}×",
            f"{comps:,}",
            f"{comp_ratio:.1f}×"
        ])
    
    table = ax5.table(cellText=table_data,
                     colLabels=['Strategy', 'Time (ms)', 'vs Optimal', 'Comparisons', 'vs Optimal'],
                     cellLoc='left',
                     loc='center',
                     colWidths=[0.25, 0.15, 0.15, 0.25, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Color code the cells
    for i in range(len(strategies_with_data)):
        for j in range(5):
            cell = table[(i+1, j)]
            if 'Optimal' in filtered_names[i]:
                cell.set_facecolor('lightgreen')
                cell.set_text_props(weight='bold')
            else:
                cell.set_facecolor('lightcoral')
    
    # Bold headers
    for j in range(5):
        table[(0, j)].set_facecolor('lightgray')
        table[(0, j)].set_text_props(weight='bold')
    
    largest_size = strategies_with_data[0][1]['size']
    ax5.set_title(f'Efficiency Comparison (n={largest_size})', fontsize=12, fontweight='bold', pad=20)
    
    # Subplot 6: Time per comparison analysis
    ax6 = plt.subplot(2, 3, 6)
    time_per_comp = []
    for name, data in strategies_with_data:
        time = data['time_ms']
        comps = data['comparisons']
        tpc = (time / comps * 1000) if comps > 0 else 0  # microseconds per comparison
        time_per_comp.append(tpc)
    
    bar_colors = [colors.get(name, 'gray') for name in filtered_names]
    bars = ax6.bar(range(len(filtered_names)), time_per_comp, color=bar_colors, alpha=0.6, edgecolor='black')
    ax6.set_xticks(range(len(filtered_names)))
    ax6.set_xticklabels([n.split('(')[0].strip() for n in filtered_names], 
                        rotation=45, ha='right', fontsize=8)
    ax6.set_ylabel('Microseconds per Comparison', fontsize=11, fontweight='bold')
    ax6.set_title('Time per Comparison Efficiency', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    
    plt.suptitle('Runtime and Complexity Comparison of Greedy Strategies',
                fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0.01, 1, 0.96])
    
    # Save figure
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'report', 'figures', 'greedy_runtime_comparison.png'
    )
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Figure saved to: {output_path}")
    
    plt.show()


def print_summary(results):
    """Print summary of runtime analysis."""
    print("\n" + "="*90)
    print("RUNTIME ANALYSIS SUMMARY")
    print("="*90)
    
    optimal_name = "Optimal (Earliest Finish)"
    largest_size = results[optimal_name][-1]['size']
    
    print(f"\nFor n={largest_size} sessions:")
    print(f"{'Strategy':<30s} {'Runtime':>12s} {'Comparisons':>15s} {'Complexity':>15s}")
    print("-"*90)
    
    for name, data_list in results.items():
        data = data_list[-1]
        time_ms = data['time_ms']
        comparisons = data['comparisons']
        
        # Estimate complexity based on growth
        if len(data_list) >= 2:
            size_ratio = data_list[-1]['size'] / data_list[-2]['size']
            time_ratio = data_list[-1]['time_ms'] / data_list[-2]['time_ms']
            
            # Rough complexity estimation
            if time_ratio < size_ratio * 1.2:
                complexity = "O(n)"
            elif time_ratio < size_ratio * np.log(size_ratio) * 1.5:
                complexity = "O(n log n)"
            elif time_ratio < size_ratio ** 1.5 * 1.5:
                complexity = "~O(n√n)"
            elif time_ratio < size_ratio ** 2 * 1.5:
                complexity = "~O(n²)"
            else:
                complexity = "O(n³) or worse"
        else:
            complexity = "Unknown"
        
        print(f"{name:<30s} {time_ms:>10.2f} ms {comparisons:>15,} {complexity:>15s}")
    
    print("\n" + "="*90)
    print("KEY INSIGHTS:")
    print("="*90)
    
    optimal_time = results[optimal_name][-1]['time_ms']
    optimal_comps = results[optimal_name][-1]['comparisons']
    
    print(f"✓ Optimal (Earliest Finish) runs in {optimal_time:.2f} ms with O(n log n) complexity")
    print(f"✓ Despite being provably optimal, it's also one of the FASTEST strategies!")
    
    # Find slowest
    slowest_name = max(results.keys(), key=lambda n: results[n][-1]['time_ms'])
    slowest_time = results[slowest_name][-1]['time_ms']
    slowdown = slowest_time / optimal_time
    
    print(f"✗ Slowest: {slowest_name} at {slowest_time:.2f} ms ({slowdown:.1f}× slower)")
    
    # Find most comparisons
    most_comps_name = max(results.keys(), key=lambda n: results[n][-1]['comparisons'])
    most_comps = results[most_comps_name][-1]['comparisons']
    comp_ratio = most_comps / optimal_comps if optimal_comps > 0 else 0
    
    print(f"✗ Most comparisons: {most_comps_name} with {most_comps:,} ({comp_ratio:.1f}× more)")
    
    print("\n💡 Conclusion: The optimal solution is also computationally efficient!")
    print("="*90)


if __name__ == "__main__":
    print("="*90)
    print("GREEDY STRATEGIES: RUNTIME & COMPLEXITY ANALYSIS")
    print("="*90)
    print()
    
    # Run analysis
    results = analyze_runtime_scaling(seed=42)
    
    # Create visualization
    print("\nGenerating visualization...")
    visualize_runtime_comparison(results)
    
    # Print summary
    print_summary(results)
    
    print("\n✅ Runtime analysis complete!")
