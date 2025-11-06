"""
EXAMPLE: Activity Selection Problem (Greedy Algorithm)
This is a COMPLETE example to show you how the structure works.
You should implement YOUR OWN problem for the project.

Problem: Given a set of activities with start and finish times, 
select the maximum number of non-overlapping activities.

This is a classic greedy problem that can serve as a template.
"""

import time
import random
from typing import List, Tuple


class Activity:
    """Represents an activity with start and finish times."""
    def __init__(self, start: int, finish: int, id: int):
        self.start = start
        self.finish = finish
        self.id = id
    
    def __repr__(self):
        return f"Activity({self.id}: {self.start}->{self.finish})"


class ActivitySelectionGreedy:
    """
    Greedy algorithm for activity selection problem.
    
    Greedy Choice: Always select the activity with earliest finish time
    that doesn't conflict with previously selected activities.
    """
    
    def solve(self, activities: List[Activity]) -> List[Activity]:
        """
        Select maximum number of non-overlapping activities.
        
        Args:
            activities: List of Activity objects
            
        Returns:
            List of selected activities
        """
        if not activities:
            return []
        
        # Step 1: Sort by finish time (greedy criterion)
        sorted_activities = sorted(activities, key=lambda a: a.finish)
        
        # Step 2: Select first activity
        selected = [sorted_activities[0]]
        last_finish = sorted_activities[0].finish
        
        # Step 3: Greedily select remaining activities
        for activity in sorted_activities[1:]:
            # If activity starts after last selected activity finishes
            if activity.start >= last_finish:
                selected.append(activity)
                last_finish = activity.finish
        
        return selected
    
    def validate_solution(self, activities: List[Activity], 
                         solution: List[Activity]) -> bool:
        """
        Validate that solution contains non-overlapping activities.
        """
        if not solution:
            return True
        
        # Check all selected activities are from input
        activity_ids = {a.id for a in activities}
        if not all(a.id in activity_ids for a in solution):
            return False
        
        # Check no overlaps
        sorted_solution = sorted(solution, key=lambda a: a.start)
        for i in range(len(sorted_solution) - 1):
            if sorted_solution[i].finish > sorted_solution[i + 1].start:
                return False
        
        return True


def generate_test_data(size: int) -> List[Activity]:
    """
    Generate random activities.
    
    Args:
        size: Number of activities
        
    Returns:
        List of Activity objects
    """
    activities = []
    for i in range(size):
        start = random.randint(0, 100)
        duration = random.randint(1, 20)
        finish = start + duration
        activities.append(Activity(start, finish, i))
    
    return activities


def measure_runtime(algorithm: ActivitySelectionGreedy, 
                   test_data: List[Activity]) -> float:
    """Measure runtime of the algorithm."""
    start_time = time.perf_counter()
    algorithm.solve(test_data)
    end_time = time.perf_counter()
    return end_time - start_time


if __name__ == "__main__":
    print("="*60)
    print("EXAMPLE: Activity Selection (Greedy Algorithm)")
    print("="*60)
    
    algorithm = ActivitySelectionGreedy()
    
    # Test with small example
    print("\nTest 1: Small example")
    activities = [
        Activity(1, 4, 0),
        Activity(3, 5, 1),
        Activity(0, 6, 2),
        Activity(5, 7, 3),
        Activity(8, 9, 4),
        Activity(5, 9, 5)
    ]
    
    print("Input activities:")
    for a in activities:
        print(f"  {a}")
    
    solution = algorithm.solve(activities)
    print(f"\nSelected {len(solution)} activities:")
    for a in solution:
        print(f"  {a}")
    
    is_valid = algorithm.validate_solution(activities, solution)
    print(f"\nSolution is valid: {is_valid}")
    
    # Test with larger random data
    print("\n" + "="*60)
    print("Test 2: Random data (size 100)")
    print("="*60)
    
    test_data = generate_test_data(100)
    solution = algorithm.solve(test_data)
    is_valid = algorithm.validate_solution(test_data, solution)
    runtime = measure_runtime(algorithm, test_data)
    
    print(f"Input: {len(test_data)} activities")
    print(f"Selected: {len(solution)} activities")
    print(f"Valid: {is_valid}")
    print(f"Runtime: {runtime:.6f} seconds")
    
    # Quick runtime test
    print("\n" + "="*60)
    print("Test 3: Runtime scaling")
    print("="*60)
    
    for size in [100, 500, 1000, 5000]:
        test_data = generate_test_data(size)
        runtime = measure_runtime(algorithm, test_data)
        print(f"Size {size:5d}: {runtime:.6f}s")
    
    print("\n✓ Example complete! Use this as a template for your problem.")
