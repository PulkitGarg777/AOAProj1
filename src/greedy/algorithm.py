"""
Greedy Algorithm Implementation: EV Charging Station Scheduler
Problem: Maximize number of charging sessions on a single charger

Real-world application: Electric vehicle charging station scheduling
Given charging session requests with start/finish times, select maximum 
number of non-overlapping sessions that can be served on one charger.

This is the classic Activity Selection problem applied to EV infrastructure.
"""

import time
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class ChargingSession:
    """Represents an EV charging session request."""
    session_id: int
    start_time: float  # minutes since midnight or unix timestamp
    finish_time: float
    user_id: Optional[str] = None
    energy_kwh: Optional[float] = None
    
    def __repr__(self):
        return f"Session({self.session_id}: {self.start_time:.1f}-{self.finish_time:.1f})"
    
    def duration(self) -> float:
        """Return session duration."""
        return self.finish_time - self.start_time
    
    def overlaps_with(self, other: 'ChargingSession') -> bool:
        """Check if this session overlaps with another."""
        return not (self.finish_time <= other.start_time or 
                   other.finish_time <= self.start_time)


class EVChargingScheduler:
    """
    Greedy algorithm for EV charging station scheduling.
    
    Greedy Choice: Always select the charging session with earliest finish time
    that doesn't conflict with previously selected sessions.
    
    This maximizes the number of sessions that can be served.
    Time Complexity: O(n log n) for sorting + O(n) for selection = O(n log n)
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        self.comparisons = 0
        self.selections = 0
    
    def solve(self, sessions: List[ChargingSession]) -> List[ChargingSession]:
        """
        Select maximum number of non-overlapping charging sessions.
        
        Args:
            sessions: List of charging session requests
            
        Returns:
            List of selected non-overlapping sessions (optimal)
        """
        if not sessions:
            return []
        
        self.comparisons = 0
        self.selections = 0
        
        # Step 1: Sort by finish time (greedy criterion)
        # O(n log n)
        sorted_sessions = sorted(sessions, key=lambda s: s.finish_time)
        
        # Step 2: Select first session (earliest finish time)
        selected = [sorted_sessions[0]]
        self.selections = 1
        last_finish = sorted_sessions[0].finish_time
        
        # Step 3: Greedily select remaining sessions
        # O(n)
        for session in sorted_sessions[1:]:
            self.comparisons += 1
            # If session starts after last selected session finishes
            if session.start_time >= last_finish:
                selected.append(session)
                self.selections += 1
                last_finish = session.finish_time
        
        return selected
    
    def validate_solution(self, sessions: List[ChargingSession], 
                         solution: List[ChargingSession]) -> bool:
        """
        Validate that solution contains non-overlapping sessions.
        
        Args:
            sessions: Original input sessions
            solution: Proposed solution
            
        Returns:
            True if solution is valid, False otherwise
        """
        if not solution:
            return True
        
        # Check all selected sessions are from input
        session_ids = {s.session_id for s in sessions}
        if not all(s.session_id in session_ids for s in solution):
            return False
        
        # Check no overlaps (pairwise)
        for i in range(len(solution)):
            for j in range(i + 1, len(solution)):
                if solution[i].overlaps_with(solution[j]):
                    return False
        
        return True
    
    def compute_utilization(self, selected: List[ChargingSession], 
                           total_time: float) -> float:
        """
        Compute charger utilization percentage.
        
        Args:
            selected: Selected sessions
            total_time: Total time window (e.g., 1440 for 24 hours)
            
        Returns:
            Utilization as percentage (0-100)
        """
        if total_time <= 0:
            return 0.0
        
        total_charging_time = sum(s.duration() for s in selected)
        return (total_charging_time / total_time) * 100


def generate_test_data(size: int, 
                      time_window: float = 1440.0,
                      avg_duration: float = 60.0,
                      seed: Optional[int] = None) -> List[ChargingSession]:
    """
    Generate synthetic EV charging session data.
    
    Uses Poisson arrivals during day with rush-hour intensity variation.
    
    Args:
        size: Number of sessions to generate
        time_window: Total time window in minutes (default 1440 = 24 hours)
        avg_duration: Average session duration in minutes (default 60)
        seed: Random seed for reproducibility
        
    Returns:
        List of ChargingSession objects
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    sessions = []
    
    for i in range(size):
        # Poisson arrivals with rush-hour peaks (7-9am, 5-7pm)
        # Use beta distribution to bias towards rush hours
        hour_fraction = np.random.beta(2, 5)  # Skews towards beginning/end
        start_time = hour_fraction * time_window
        
        # Duration: exponential distribution with some minimum
        # Typical EV charging: 30 min to 2 hours
        duration = np.random.exponential(avg_duration) + 15
        duration = min(duration, 180)  # Cap at 3 hours
        
        finish_time = start_time + duration
        
        # Energy typically 20-80 kWh for full charge
        energy_kwh = np.random.uniform(20, 80)
        
        sessions.append(ChargingSession(
            session_id=i,
            start_time=start_time,
            finish_time=finish_time,
            user_id=f"user_{i % 100}",
            energy_kwh=energy_kwh
        ))
    
    return sessions


def measure_runtime(scheduler: EVChargingScheduler, 
                   sessions: List[ChargingSession]) -> float:
    """
    Measure the runtime of the algorithm on given sessions.
    
    Args:
        scheduler: The scheduler instance
        sessions: Session data to run on
        
    Returns:
        Runtime in seconds
    """
    start_time = time.perf_counter()
    scheduler.solve(sessions)
    end_time = time.perf_counter()
    return end_time - start_time


if __name__ == "__main__":
    print("="*70)
    print("EV CHARGING STATION SCHEDULER (Greedy Algorithm)")
    print("="*70)
    
    scheduler = EVChargingScheduler()
    
    # Test 1: Small example
    print("\n📊 Test 1: Small example (manual)")
    sessions = [
        ChargingSession(0, 60, 120, "user_a", 50.0),   # 1h-2h
        ChargingSession(1, 90, 150, "user_b", 45.0),   # 1.5h-2.5h
        ChargingSession(2, 30, 180, "user_c", 60.0),   # 0.5h-3h
        ChargingSession(3, 150, 210, "user_d", 40.0),  # 2.5h-3.5h
        ChargingSession(4, 240, 300, "user_e", 55.0),  # 4h-5h
        ChargingSession(5, 150, 270, "user_f", 65.0),  # 2.5h-4.5h
    ]
    
    print(f"Input: {len(sessions)} charging requests")
    for s in sessions:
        print(f"  {s}")
    
    selected = scheduler.solve(sessions)
    print(f"\n✅ Selected {len(selected)} sessions (optimal):")
    for s in selected:
        print(f"  {s}")
    
    is_valid = scheduler.validate_solution(sessions, selected)
    utilization = scheduler.compute_utilization(selected, 1440)
    print(f"\n✓ Valid: {is_valid}")
    print(f"✓ Comparisons: {scheduler.comparisons}")
    print(f"✓ Utilization: {utilization:.2f}%")
    
    # Test 2: Larger synthetic data
    print("\n" + "="*70)
    print("📊 Test 2: Synthetic data (n=100)")
    print("="*70)
    
    sessions = generate_test_data(100, seed=42)
    selected = scheduler.solve(sessions)
    runtime = measure_runtime(scheduler, sessions)
    
    print(f"Input: {len(sessions)} sessions")
    print(f"Selected: {len(selected)} sessions")
    print(f"Valid: {scheduler.validate_solution(sessions, selected)}")
    print(f"Utilization: {scheduler.compute_utilization(selected, 1440):.2f}%")
    print(f"Runtime: {runtime*1000:.3f} ms")
    
    # Test 3: Scaling behavior
    print("\n" + "="*70)
    print("📊 Test 3: Runtime scaling")
    print("="*70)
    
    print(f"{'Size':>8} {'Time (ms)':>12} {'Selected':>10} {'Util %':>10}")
    print("-" * 50)
    
    for size in [100, 500, 1000, 5000, 10000]:
        sessions = generate_test_data(size, seed=42)
        runtime = measure_runtime(scheduler, sessions)
        selected = scheduler.solve(sessions)
        util = scheduler.compute_utilization(selected, 1440)
        
        print(f"{size:8d} {runtime*1000:12.3f} {len(selected):10d} {util:10.2f}")
    
    print("\n✅ Implementation complete! Ready for experiments.")
    print("Next: Run experiment.py for full analysis with visualizations.")
