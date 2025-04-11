
def validate(solution, tests): # solution -> index, included; tests -> disease
    # number of unique columns
    unique_columns = set()
    matrix = [tests[i] for i,t in solution if t==1]
    for i in range(len(matrix[0])):
        unique_columns.add("".join(map(str, (matrix[j][i] for j in range(len(matrix))))))
    return len(unique_columns) >= len(matrix[0])

def visualize(solution, tests, costs): 
    c_matrix = [[costs[i]]+tests[i] for i,t in solution if t==1]
    for row in c_matrix:
        print(f"cost {row[0]}: {' '.join((map(str,row[1:])))}")
    
if __name__ == "__main__":
    # example validation
    solution = [(0,1),(1,0),(2,1),(3,0)]
    tests = [
        [0,1,1],
        [1,1,1],
        [1,1,0],
        [1,0,1],
    ]
    print(validate(solution, tests))

    # example visualization
    costs = [1,1,1,1]
    visualize(solution, tests, costs)
