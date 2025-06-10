import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd
import networkx as nx
import scipy.stats
import statistics
import os
import sys
import openpyxl
import pyxlsb

current_directory = str(os.path.abspath(__file__).replace("\\normal.py", ""))
trial_no = input("Enter trial name: ")

print("Enter values separated by newlines (Ctrl-Z to finish): ")
values_list = sys.stdin.readlines()
values_list = [value.rstrip("\n") for value in values_list]
print(values_list)
print(len(values_list))

df_normal_main = pd.read_excel(f"{current_directory}/normal.xlsb")

for value in values_list:
    while value not in list(df_normal_main.iloc[:,0]) and value in values_list:
        values_list.remove(value)

df_normal_main = df_normal_main[df_normal_main.iloc[:, 0].isin(values_list)]
print(df_normal_main.head())

Gn = nx.Graph()
Gn.add_nodes_from(values_list)

normal_pval = []
for locator1 in df_normal_main.iloc[:,0].index:
    for locator2 in df_normal_main.iloc[:,0].index:
        if locator1 != locator2:
            val1 = pd.Series(df_normal_main.loc[locator1][1:], dtype=float)
            val2 = pd.Series(df_normal_main.loc[locator2][1:], dtype=float)
            r, p_val = scipy.stats.pearsonr(val1, val2)
            if p_val < 0.00000005:
                normal_pval.append((p_val, r, df_normal_main.loc[locator1][0], df_normal_main.loc[locator2][0]))

adjusted_pvals = scipy.stats.false_discovery_control(list(zip(*normal_pval))[0])
normal_weights = []

for index, p_value in enumerate(adjusted_pvals):
    if p_value < 0.00000005:
        Gn.add_edge(f'{normal_pval[index][3]}', f'{normal_pval[index][2]}', weight=normal_pval[index][1])
        normal_weights.append(normal_pval[index][1])

#ADD PARAMETERS HERE

plt.title('''Normal Graph ''')
nx.draw_networkx(Gn, with_labels=True)
plt.savefig(f'{current_directory}/graphs/Normal_{trial_no}.png')
plt.show()
plt.clf()

nx.write_weighted_edgelist(Gn, f"{current_directory}/edgelists/normal_graph{trial_no}.edgelist")