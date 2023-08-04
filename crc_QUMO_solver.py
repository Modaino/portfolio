from QUMO import *
import gurobipy as gp
from gurobipy import GRB

def solve_instance(input):
    (file_name, problem) = input
    result = {}
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.start()
        with gp.Model(env=env) as m:
            # Allow for non-convex matrices
            m.Params.NonConvex = 2

            # Create variables
            x = m.addMVar(problem.instance_data['N'], vtype=GRB.SEMIINT)

            # Set objective
            qudratic_term = x @ problem.instance_data['J'] @ x
            m.setObjective(qudratic_term, GRB.MINIMIZE)    
            
            # Add constraint(s)
            m.addConstr(x.sum() == problem.constraints["Budget"], 'Budget')
            m.addConstr(x <= problem.constraints["Upperbox"], 'Upper limit on x')
            
            # Verify model formulation
            m.write('results/' + file_name.split('QUMO_problems')[1] + '.lp')

            # Optimize model
            m.optimize()
            
            for v in m.getVars():
                result[v.VarName] = v.X

            result['H'] = m.ObjVal
            result['t'] = m.Runtime
            result['N'] = problem.instance_data['N']

    return result

if __name__ == "__main__":
    import sys
    from multiprocessing import Pool
    import os

    if sys.argv[1] == 'undefined':
        task_id = -1
    else:
        task_id = int(sys.argv[1])
    problem_directory = sys.argv[2]

    file_names = []
    for filename in os.listdir(problem_directory):
        f = os.path.join(problem_directory, filename)
        if os.path.isfile(f):
            file_names.append(f)
    instances = [(filename, load_instance_from_json( filename )) for filename in file_names]
    results = []

    pool = Pool()
    chunksize = int( len(instances) / pool._processes )

    if chunksize < 1:
        chunksize = 1
    for ind, res in enumerate(pool.imap_unordered(solve_instance, instances, chunksize)):
        results.append(res)

    pool.close()
    pool.join()
    for (file_name, result_dic) in zip(file_names, results):
        my_path = "results/N" + str(result_dic['N']) + '/'
        if not os.path.exists(my_path):
            os.makedirs(my_path)
        result_path = 'results/' + file_name.split('QUMO_problems')[1] + '.sol'
        print("Writing results to " + result_path)
        with open(result_path, 'w') as the_file:
            for key, value in result_dic.items():
                the_file.write(key + ":" + str(value) + '\n')