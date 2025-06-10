import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd
import networkx as nx
import scipy.stats
import statistics
import os
import sys, math
import openpyxl
import pyxlsb

current_directory = str(os.path.abspath(__file__).replace("\\cancer.py", ""))
trial_no = input("Enter trial name: ")

print("Enter values separated by newlines (Ctrl-Z to finish): ")
values_list = sys.stdin.readlines()
values_list = [value.rstrip("\n") for value in values_list]
print(values_list)
print(len(values_list))

df_cancer_main = pd.read_excel(f"{current_directory}/cancer.xlsb")

for value in values_list:
    while value not in list(df_cancer_main.iloc[:,0]) and value in values_list:
        values_list.remove(value)

df_cancer_main = df_cancer_main[df_cancer_main.iloc[:, 0].isin(values_list)]
print(df_cancer_main.head())

Gc = nx.Graph()
Gc.add_nodes_from(values_list)

cancer_pvals = []
for locator1 in df_cancer_main.iloc[:,0].index:
    for locator2 in df_cancer_main.iloc[:,0].index:
        if locator1 != locator2:
            val1 = pd.Series(df_cancer_main.loc[locator1][1:], dtype=float)
            val2 = pd.Series(df_cancer_main.loc[locator2][1:], dtype=float)
            r, p_val = scipy.stats.pearsonr(val1, val2)
            if p_val < 0.00000005:
                cancer_pvals.append((p_val, r, df_cancer_main.loc[locator1][0], df_cancer_main.loc[locator2][0]))

adjusted_pvals = scipy.stats.false_discovery_control(list(zip(*cancer_pvals))[0])
tcga_weights = []

for index, p_value in enumerate(adjusted_pvals):
    if p_value < 0.00000005:
        Gc.add_edge(f'{cancer_pvals[index][3]}', f'{cancer_pvals[index][2]}', weight=cancer_pvals[index][1])
        tcga_weights.append(cancer_pvals[index][1])

# ADD PARAMETERS HERE

plt.title(''' CANCER GRAPH ''')
nx.draw_networkx(Gc, with_labels=True)
plt.savefig(f'{current_directory}/graphs/cancer_{trial_no}.png')
plt.show()
plt.clf()

nx.write_weighted_edgelist(Gc, f"{current_directory}/edgelists/cancer_graph{trial_no}.edgelist")