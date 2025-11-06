"""
Common utility functions for algorithm implementations.
"""

import time
import functools
from typing import Callable, Any


def timer(func: Callable) -> Callable:
    """
    Decorator to measure execution time of a function.
    
    Args:
        func: Function to time
        
    Returns:
        Wrapped function that prints execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds")
        return result
    return wrapper


def compare_algorithms(algo1: Callable, algo2: Callable, test_data: Any) -> None:
    """
    Compare runtime of two algorithms on the same test data.
    
    Args:
        algo1: First algorithm function
        algo2: Second algorithm function
        test_data: Test data to run on
    """
    print(f"Comparing algorithms...")
    
    start1 = time.perf_counter()
    result1 = algo1(test_data)
    end1 = time.perf_counter()
    time1 = end1 - start1
    
    start2 = time.perf_counter()
    result2 = algo2(test_data)
    end2 = time.perf_counter()
    time2 = end2 - start2
    
    print(f"Algorithm 1: {time1:.6f}s")
    print(f"Algorithm 2: {time2:.6f}s")
    print(f"Speedup: {time2/time1:.2f}x")
    
    if result1 == result2:
        print("✓ Both algorithms produced the same result")
    else:
        print("✗ Warning: Algorithms produced different results!")
