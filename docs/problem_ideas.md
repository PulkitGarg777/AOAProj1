# Problem Ideas and Suggestions

## Greedy Algorithm Problems

### 1. Activity Selection / Meeting Room Scheduling
- **Real-world application**: Conference room scheduling, task scheduling
- **Input**: Set of activities with start and finish times
- **Greedy choice**: Select activity with earliest finish time
- **Time complexity**: O(n log n)
- **Abstraction**: Intervals on a timeline

### 2. Huffman Coding
- **Real-world application**: Data compression (ZIP, JPEG, MP3)
- **Input**: Character frequencies in a text
- **Greedy choice**: Combine two lowest-frequency nodes
- **Time complexity**: O(n log n)
- **Abstraction**: Binary tree construction

### 3. Fractional Knapsack
- **Real-world application**: Resource allocation, portfolio optimization
- **Input**: Items with values and weights, knapsack capacity
- **Greedy choice**: Take items with highest value-to-weight ratio
- **Time complexity**: O(n log n)
- **Abstraction**: Optimization over a set with constraints

### 4. Minimum Spanning Tree (Kruskal's or Prim's)
- **Real-world application**: Network design, circuit design
- **Input**: Weighted graph
- **Greedy choice**: Add cheapest edge that doesn't create cycle
- **Time complexity**: O(E log V)
- **Abstraction**: Graph problem

### 5. Interval Partitioning
- **Real-world application**: Classroom assignment, processor scheduling
- **Input**: Set of intervals (lectures with start/end times)
- **Greedy choice**: Assign to earliest available resource
- **Time complexity**: O(n log n)
- **Abstraction**: Interval graph coloring

### 6. Gas Station Problem
- **Real-world application**: Route planning, refueling strategy
- **Input**: Distances between gas stations, tank capacity
- **Greedy choice**: Go as far as possible before refueling
- **Time complexity**: O(n)
- **Abstraction**: Sequential decision problem

---

## Divide and Conquer Problems

### 1. Closest Pair of Points
- **Real-world application**: Air traffic control, clustering in ML
- **Input**: Set of points in 2D plane
- **Divide**: Split by median x-coordinate
- **Time complexity**: O(n log n)
- **Abstraction**: Geometric problem

### 2. Convex Hull (using D&C)
- **Real-world application**: Computer graphics, pattern recognition
- **Input**: Set of points in 2D plane
- **Divide**: Split into left and right halves
- **Time complexity**: O(n log n)
- **Abstraction**: Computational geometry

### 3. Karatsuba Multiplication
- **Real-world application**: Cryptography, large number arithmetic
- **Input**: Two large integers
- **Divide**: Split numbers into halves
- **Time complexity**: O(n^1.585)
- **Abstraction**: Recursive arithmetic

### 4. Merge Sort Variations
- **Real-world application**: External sorting, database operations
- **Input**: Array of elements
- **Divide**: Split array in half
- **Time complexity**: O(n log n)
- **Abstraction**: Sorting problem

### 5. Binary Search Variations
- **Real-world application**: Search engines, database indexing
- **Input**: Sorted array, target value
- **Divide**: Split search space in half
- **Time complexity**: O(log n)
- **Abstraction**: Search problem

### 6. Skyline Problem
- **Real-world application**: City skyline visualization, CAD systems
- **Input**: Set of rectangular buildings
- **Divide**: Split buildings into left and right sets
- **Time complexity**: O(n log n)
- **Abstraction**: Geometric merging problem

### 7. Strassen's Matrix Multiplication
- **Real-world application**: Scientific computing, graphics
- **Input**: Two n×n matrices
- **Divide**: Split matrices into quadrants
- **Time complexity**: O(n^2.807)
- **Abstraction**: Matrix operations

### 8. Count Inversions in Array
- **Real-world application**: Ranking similarity, collaborative filtering
- **Input**: Array of elements
- **Divide**: Split array and count inversions
- **Time complexity**: O(n log n)
- **Abstraction**: Array analysis problem

---

## Tips for Choosing Problems

1. **For Greedy**: Look for problems where:
   - Local optimal choices lead to global optimum
   - You can prove "greedy choice property" and "optimal substructure"
   - Exchange argument or "stays ahead" proof works

2. **For Divide & Conquer**: Look for problems where:
   - Problem can be split into independent subproblems
   - Subproblems have the same structure as original
   - Solutions can be efficiently combined
   - Master Theorem applies for analysis

3. **Avoid**: Problems from "Algorithms" textbooks directly
4. **Prefer**: Real-world applications from other CS areas or non-CS domains
5. **Document**: The connection between real problem and abstract formulation

---

## Resources

- Kleinberg & Tardos: "Algorithm Design" (excellent for greedy proofs)
- CLRS: "Introduction to Algorithms" (comprehensive coverage)
- Look at applications in: ML, Computer Graphics, Networks, Databases, Bioinformatics
