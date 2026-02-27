"""
Greedy Algorithms Assignment
Implement three greedy algorithms for delivery optimization.
"""

import json
import time


# ============================================================================
# PART 1: PACKAGE PRIORITIZATION (Activity Selection)
# ============================================================================

def maximize_deliveries(time_windows):
    """
    Schedule the maximum number of deliveries given time window constraints.
    
    This is the activity selection problem. Each delivery has a start and end time.
    You can only do one delivery at a time. A new delivery can start when the 
    previous one ends.
    
    Args:
        time_windows (list): List of dicts with 'delivery_id', 'start', 'end'
    
    Returns:
        list: List of delivery_ids that can be completed (maximum number possible)
    """
    # Greedy choice: always pick the delivery that ends earliest.
    # This leaves the most room for future deliveries.

    if not time_windows:
        return []

    # Sort by end time ascending
    windows_sorted = sorted(time_windows, key=lambda d: d["end"])

    selected_ids = []
    current_end = float("-inf")

    for d in windows_sorted:
        if d["start"] >= current_end:
            selected_ids.append(d["delivery_id"])
            current_end = d["end"]

    return selected_ids


# ============================================================================
# PART 2: TRUCK LOADING (Fractional Knapsack)
# ============================================================================

def optimize_truck_load(packages, weight_limit):
    """
    Maximize total priority value of packages loaded within weight constraint.
    
    This is the fractional knapsack problem. You can take fractions of packages
    (e.g., deliver part of a package). Goal is to maximize priority value while
    staying within the weight limit.
    
    Args:
        packages (list): List of dicts with 'package_id', 'weight', 'priority'
        weight_limit (int): Maximum weight the truck can carry
    
    Returns:
        dict: {
            'total_priority': float,
            'total_weight': float,
            'packages': list of dicts with 'package_id' and 'fraction'
        }
    """
    if not packages or weight_limit <= 0:
        return {"total_priority": 0.0, "total_weight": 0.0, "packages": []}

    # Sort by priority-to-weight ratio descending (value density)
    def ratio(p):
        # Avoid division by zero; if weight is 0 and priority > 0, treat as "infinite"
        if p["weight"] == 0:
            return float("inf") if p["priority"] > 0 else 0.0
        return p["priority"] / p["weight"]

    packages_sorted = sorted(packages, key=ratio, reverse=True)

    remaining = float(weight_limit)
    total_priority = 0.0
    total_weight = 0.0
    taken = []

    for p in packages_sorted:
        if remaining <= 0:
            break

        w = float(p["weight"])
        v = float(p["priority"])

        if w <= 0:
            # If it has no weight, take it fully (if it has positive value)
            if v > 0:
                taken.append({"package_id": p["package_id"], "fraction": 1.0})
                total_priority += v
            continue

        if w <= remaining:
            # Take the whole package
            taken.append({"package_id": p["package_id"], "fraction": 1.0})
            remaining -= w
            total_weight += w
            total_priority += v
        else:
            # Take a fraction to fill the remaining capacity
            frac = remaining / w
            taken.append({"package_id": p["package_id"], "fraction": frac})
            total_weight += remaining
            total_priority += v * frac
            remaining = 0.0

    return {
        "total_priority": total_priority,
        "total_weight": total_weight,
        "packages": taken
    }


# ============================================================================
# PART 3: DRIVER ASSIGNMENT (Interval Scheduling)
# ============================================================================

def minimize_drivers(deliveries):
    """
    Assign deliveries to the minimum number of drivers needed.
    
    Each delivery has a start and end time. A driver can do a delivery if it 
    doesn't overlap with their other assigned deliveries. Goal is to use the
    fewest drivers possible.
    
    Args:
        deliveries (list): List of dicts with 'delivery_id', 'start', 'end'
    
    Returns:
        dict: {
            'num_drivers': int,
            'assignments': list of lists (each sublist is one driver's deliveries)
        }
    """
    if not deliveries:
        return {"num_drivers": 0, "assignments": []}

    # Sort deliveries by start time (then end time to be consistent)
    jobs = sorted(deliveries, key=lambda d: (d["start"], d["end"]))

    # We'll store assignments as lists of delivery_ids per driver
    assignments = []
    # Track the time each driver becomes available (end time of last job)
    driver_end_times = []

    for job in jobs:
        placed = False

        for i in range(len(assignments)):
            # If this driver is free before the job starts, assign it
            if job["start"] >= driver_end_times[i]:
                assignments[i].append(job["delivery_id"])
                driver_end_times[i] = job["end"]
                placed = True
                break

        if not placed:
            # Need a new driver
            assignments.append([job["delivery_id"]])
            driver_end_times.append(job["end"])

    return {"num_drivers": len(assignments), "assignments": assignments}


# ============================================================================
# TESTING & BENCHMARKING
# ============================================================================

def load_scenario(filename):
    """Load a scenario from JSON file."""
    with open(f"scenarios/{filename}", "r") as f:
        return json.load(f)


def test_package_prioritization():
    """Test package prioritization with small known cases."""
    print("="*70)
    print("TESTING PACKAGE PRIORITIZATION")
    print("="*70 + "\n")
    
    # Test case 1: Non-overlapping deliveries (should select all)
    test1 = [
        {'delivery_id': 'A', 'start': 1, 'end': 2},
        {'delivery_id': 'B', 'start': 3, 'end': 4},
        {'delivery_id': 'C', 'start': 5, 'end': 6}
    ]
    result1 = maximize_deliveries(test1)
    print(f"Test 1: Non-overlapping")
    print(f"  Expected: 3 deliveries")
    print(f"  Got: {len(result1)} deliveries")
    print(f"  {'✓ PASS' if len(result1) == 3 else '✗ FAIL'}\n")
    
    # Test case 2: All overlapping (should select 1)
    test2 = [
        {'delivery_id': 'A', 'start': 1, 'end': 5},
        {'delivery_id': 'B', 'start': 2, 'end': 4},
        {'delivery_id': 'C', 'start': 3, 'end': 6}
    ]
    result2 = maximize_deliveries(test2)
    print(f"Test 2: All overlapping")
    print(f"  Expected: 1-2 deliveries (depends on greedy choice)")
    print(f"  Got: {len(result2)} deliveries")
    print(f"  Result: {result2}\n")
    
   # Test case 3: Mixed overlapping
    test3 = [
        {'delivery_id': 'A', 'start': 1, 'end': 3},
        {'delivery_id': 'B', 'start': 2, 'end': 5},
        {'delivery_id': 'C', 'start': 4, 'end': 7},
        {'delivery_id': 'D', 'start': 6, 'end': 9}
    ]
    result3 = maximize_deliveries(test3)
    print(f"Test 3: Mixed overlapping")
    print(f"  Expected: 2 deliveries (A ends at 3, C starts at 4)")
    print(f"  Got: {len(result3)} deliveries")
    print(f"  Result: {result3}")
    print(f"  {'✓ PASS' if len(result3) == 2 else '✗ FAIL'}\n")


def test_truck_loading():
    """Test truck loading with small known cases."""
    print("="*70)
    print("TESTING TRUCK LOADING")
    print("="*70 + "\n")
    
    # Test case 1: All packages fit
    packages1 = [
        {'package_id': 'A', 'weight': 10, 'priority': 60},
        {'package_id': 'B', 'weight': 20, 'priority': 100}
    ]
    result1 = optimize_truck_load(packages1, 50)
    print(f"Test 1: All packages fit")
    print(f"  Expected: Total priority = 160, weight = 30")
    print(f"  Got: Priority = {result1['total_priority']}, weight = {result1['total_weight']}")
    print(f"  {'✓ PASS' if result1['total_priority'] == 160 else '✗ FAIL'}\n")
    
    # Test case 2: Fractional required
    packages2 = [
        {'package_id': 'A', 'weight': 10, 'priority': 60},  # ratio = 6.0
        {'package_id': 'B', 'weight': 20, 'priority': 100}, # ratio = 5.0
        {'package_id': 'C', 'weight': 30, 'priority': 120}  # ratio = 4.0
    ]
    result2 = optimize_truck_load(packages2, 50)
    print(f"Test 2: Fractional knapsack")
    print(f"  Expected: Take A (full), B (full), C (partial)")
    print(f"  Expected priority: ~240 (60 + 100 + 80 from 2/3 of C)")
    print(f"  Got: Priority = {result2['total_priority']}, weight = {result2['total_weight']}")
    print(f"  Packages: {result2['packages']}\n")


def test_driver_assignment():
    """Test driver assignment with small known cases."""
    print("="*70)
    print("TESTING DRIVER ASSIGNMENT")
    print("="*70 + "\n")
    
    # Test case 1: All non-overlapping (need 1 driver)
    deliveries1 = [
        {'delivery_id': 'A', 'start': 1, 'end': 2},
        {'delivery_id': 'B', 'start': 3, 'end': 4},
        {'delivery_id': 'C', 'start': 5, 'end': 6}
    ]
    result1 = minimize_drivers(deliveries1)
    print(f"Test 1: Non-overlapping")
    print(f"  Expected: 1 driver")
    print(f"  Got: {result1['num_drivers']} drivers")
    print(f"  {'✓ PASS' if result1['num_drivers'] == 1 else '✗ FAIL'}\n")
    
    # Test case 2: All overlapping (need 3 drivers)
    deliveries2 = [
        {'delivery_id': 'A', 'start': 1, 'end': 5},
        {'delivery_id': 'B', 'start': 2, 'end': 6},
        {'delivery_id': 'C', 'start': 3, 'end': 7}
    ]
    result2 = minimize_drivers(deliveries2)
    print(f"Test 2: All overlapping")
    print(f"  Expected: 3 drivers")
    print(f"  Got: {result2['num_drivers']} drivers")
    print(f"  {'✓ PASS' if result2['num_drivers'] == 3 else '✗ FAIL'}\n")
    
    # Test case 3: Mixed
    deliveries3 = [
        {'delivery_id': 'A', 'start': 1, 'end': 3},
        {'delivery_id': 'B', 'start': 2, 'end': 4},
        {'delivery_id': 'C', 'start': 4, 'end': 6},
        {'delivery_id': 'D', 'start': 5, 'end': 7}
    ]
    result3 = minimize_drivers(deliveries3)
    print(f"Test 3: Mixed overlapping")
    print(f"  Expected: 2 drivers")
    print(f"  Got: {result3['num_drivers']} drivers")
    print(f"  Assignments: {result3['assignments']}")
    print(f"  {'✓ PASS' if result3['num_drivers'] == 2 else '✗ FAIL'}\n")


def benchmark_scenarios():
    """Benchmark all algorithms on realistic scenarios."""
    print("\n" + "="*70)
    print("BENCHMARKING ON REALISTIC SCENARIOS")
    print("="*70 + "\n")
    
    # Benchmark package prioritization
    print("Scenario 1: Package Prioritization (50 deliveries)")
    print("-" * 70)
    data = load_scenario("package_prioritization.json")
    
    start = time.perf_counter()
    result = maximize_deliveries(data)
    elapsed = time.perf_counter() - start
    
    print(f"  Deliveries scheduled: {len(result)} out of {len(data)}")
    print(f"  Runtime: {elapsed*1000:.4f} ms\n")
    
    # Benchmark truck loading
    print("Scenario 2: Truck Loading (100 packages, 500 lb limit)")
    print("-" * 70)
    data = load_scenario("truck_loading.json")
    
    start = time.perf_counter()
    result = optimize_truck_load(data['packages'], data['truck_capacity'])
    elapsed = time.perf_counter() - start
    
    print(f"  Total priority loaded: {result['total_priority']:.2f}")
    print(f"  Total weight loaded: {result['total_weight']:.2f} lbs")
    print(f"  Packages used: {len(result['packages'])}")
    print(f"  Runtime: {elapsed*1000:.4f} ms\n")
    
    # Benchmark driver assignment
    print("Scenario 3: Driver Assignment (60 deliveries)")
    print("-" * 70)
    data = load_scenario("driver_assignment.json")
    
    start = time.perf_counter()
    result = minimize_drivers(data)
    elapsed = time.perf_counter() - start
    
    print(f"  Drivers needed: {result['num_drivers']}")
    print(f"  Runtime: {elapsed*1000:.4f} ms\n")


if __name__ == "__main__":
    print("GREEDY ALGORITHMS ASSIGNMENT - STARTER CODE")
    print("Implement the greedy functions above, then run tests.\n")
    
    # Uncomment these as you complete each part:
    
    test_package_prioritization()
    test_truck_loading()
    test_driver_assignment()
    benchmark_scenarios()
    
    print("\n⚠ Uncomment the test functions in the main block to run tests!")