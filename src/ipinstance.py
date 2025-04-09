from dataclasses import dataclass
import numpy  as np
from docplex.mp.model import Model
import random

@dataclass(frozen=True)
class IPConfig:
   numTests: int # number of tests
   numDiseases : int # number of diseases
   costOfTest: np.ndarray #[numTests] the cost of each test
   A : np.ndarray #[numTests][numDiseases] 0/1 matrix if test is positive for disease


#  * File Format
#  * #Tests (i.e., n)
#  * #Diseases (i.e., m)
#  * Cost_1 Cost_2 . . . Cost_n
#  * A(1,1) A(1,2) . . . A(1, m)
#  * A(2,1) A(2,2) . . . A(2, m)
#  * . . . . . . . . . . . . . .
#  * A(n,1) A(n,2) . . . A(n, m)

def data_parse(filename : str) :
    try:
      with open(filename,"r") as fl:
        numTests = int(fl.readline().strip()) #n 
        numDiseases = int(fl.readline().strip()) #m

        costOfTest = np.array([float(i) for i in fl.readline().strip().split()])

        A = np.zeros((numTests,numDiseases))
        for i in range(0,numTests):
          A[i,:] = np.array([int(i) for i in fl.readline().strip().split() ])
        return numTests,numDiseases,costOfTest,A
    except Exception as e:
       print(f"Error reading instance file. File format may be incorrect.{e}")
       exit(1)

class IPInstance:

  def __init__(self,filename : str) -> None:
    numT,numD,cst,A = data_parse(filename)
    self.numTests = numT
    self.numDiseases = numD
    self.costOfTest = cst
    self.A = A
    self.model = Model() #CPLEX solver

  # notes
    # heuristic -> based on the number of decmials
      # refine values until integral
    # branch and bound
      # solve and continue to add constraints

  def declare_base_variables_and_constraints(self,): # declare initial variables and constraints
    self.variables = self.model.continuous_var_list(self.numTests, 0, 1)
    for i in range(self.numDiseases):
      s = self.model.sum(self.variables[j]*self.A[j][i] for j in range(self.numTests))
      self.model.add_constraint(s<=self.numTests-1)
      self.model.add_constraint(s>=1)
    self.model.minimize(self.model.scal_prod(terms=self.variables, coefs=self.costOfTest))

  def solve_lp(self,): # solve the linear relaxation of the problem
    if self.model.solve():
      return self.model.objective_value
    else: return -1

  def heuristic(self, constraint_name_path): 
    # note: not a good heuristic

    # first variable not in constraint path
    current_constraints = [int(cn[:-1]) for cn in constraint_name_path]
    for i in range(self.numTests):
      if i not in current_constraints: return i
    raise Exception("[heuristic] out of variables exception")

  def branch_and_bound(self,):
    self.declare_base_variables_and_constraints() # initial problem declaration

    # other approaches
      # inital branch selection
      # search over all decision variables? 

    # debugging information
    self.model.print_information()

    # branch and bound 
    variable_index_stack = [] 
    constraint_name_path = []
    current_optimal_bound = float("inf")
    current_optimal_path = [] # for debugging purposes

    # note: which variable to start with?
    random_index = random.choice(range(self.numTests)) # replace with heuristic
    variable_index_stack.append((random_index, 0))
    variable_index_stack.append((random_index, 1))
    
    while len(variable_index_stack)>0: # dfs 

      # debugging
      print(variable_index_stack)

      # branch on next constraint on stack, backtrack if necessary
      variable_index, value = variable_index_stack.pop()
      constraint_name = f"{variable_index}{value}"
      constraint_name_other = f"{variable_index}{0 if value==1 else 1}"
      try: # backtrack constraints if necessary
        if (i:=constraint_name_path.index(constraint_name_other))!=-1: 
          for _ in range(len(constraint_name_path)-i):
            self.model.remove_constraint(constraint_name_path.pop())
      except: pass
      constraint_name_path.append(constraint_name)
      self.model.add_constraint(self.variables[variable_index]==value, ctname=constraint_name)

      # solve for lower bound
      branch_bound = self.solve_lp()
      if branch_bound>current_optimal_bound or branch_bound<0: continue # early stop branch

      # branch node or leaf node
      if len(constraint_name_path) == self.numTests: # leaf case
        if branch_bound<current_optimal_bound:
          current_optimal_bound = branch_bound
          current_optimal_path = list(constraint_name_path) # for debugging purposes
      else: # branch case
        # note: order based on their branch bound?
        next_variable_index = self.heuristic(constraint_name_path)
        variable_index_stack.append((next_variable_index, 0))
        variable_index_stack.append((next_variable_index, 1))
    
    # debugging information
    print(current_optimal_path)

    return current_optimal_bound
  
  def toString(self):
    out = ""
    out = f"Number of test: {self.numTests}\n"
    out+=f"Number of diseases: {self.numDiseases}\n"
    cst_str = " ".join([str(i) for i in self.costOfTest])
    out+=f"Cost of tests: {cst_str}\n"
    A_str = "\n".join([" ".join([str(j) for j in self.A[i]]) for i in range(0,self.A.shape[0])])
    out+=f"A:\n{A_str}"
    return out