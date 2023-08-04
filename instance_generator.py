from QUMO import *
import os

sizes = [5, 6]

for i in sizes:
    folder_name = "QUMO_problems/N"+str(i)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for j in range(10):
        file_name = "QUMO_N{0}_ridx{1}".format(i, j)
        QUMO_instance().random_instance(i, 1000, 1e4).dump_instance(folder_name+"/"+file_name)
