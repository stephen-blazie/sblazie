#Polysome-profile_analyzer
#calculates the area under the curve using simpson's rule, for polysome 
profile inputs (.csv)
#by Stephen Blazie
#please cite: Blazie et al., Eukaryotic initiation factor EIF-3.G augments 
mRNA translation efficiency to regulate neuronal activity. eLIFE. 2015

import numpy as np
from scipy.integrate import simps
from numpy import trapz
import pandas as pd

#read-in each monosome/polysome csv file and store as a dataframe
df_N2_m = pd.read_csv("N2_monosome_1218.csv")
df_N2_p = pd.read_csv("N2_polysome_1218.csv")
df_ju807_m = pd.read_csv("ju807_monosome_1218.csv")
df_ju807_p = pd.read_csv("ju807_polysome_1218.csv")
df_n2420_m = pd.read_csv("n2420_monosome_1218.csv")
df_n2420_p = pd.read_csv("n2420_polysome_1218.csv")
df_ju807_n2420_m = pd.read_csv("ju807_n2420_monosome_1218.csv")
df_ju807_n2420_p = pd.read_csv("ju807_n2420_polysome_1218.csv")


#convert column 4 of each dataframe, which contains the absorbance values 
to a numpy array
N2_monosome = df_N2_m[df.columns[3]].to_numpy()
N2_polysome = df_N2_p[df.columns[3]].to_numpy()
ju807_monosome = df_ju807_m[df.columns[3]].to_numpy()
ju807_polysome = df_ju807_p[df.columns[3]].to_numpy()
n2420_monosome = df_n2420_m[df.columns[3]].to_numpy()
n2420_polysome = df_n2420_p[df.columns[3]].to_numpy()
ju807_n2420_monosome = df_ju807_n2420_m[df.columns[3]].to_numpy()
ju807_n2420_polysome = df_ju807_n2420_p[df.columns[3]].to_numpy()


#Simpson's rule for calculating AUC
#the dx=1 just steps the x-axis in increments of 1 instead of using actual 
values from
#the dataframe
N2_m_area = simps(N2_monosome, dx=1)
N2_p_area = simps(N2_polysome, dx=1)
ju807_m_area = simps(ju807_monosome, dx=1)
ju807_p_area = simps(ju807_polysome, dx=1)
n2420_m_area = simps(n2420_monosome, dx=1)
n2420_p_area = simps(n2420_polysome, dx=1)
ju807_n2420_m_area = simps(ju807_n2420_monosome, dx=1)
ju807_n2420_p_area = simps(ju807_n2420_polysome, dx=1)

#print the AUC results for each plot
print("N2_monosome_AUC =", N2_m_area)
print("N2_polysome_AUC =", N2_p_area)
print("ju807_monosome_AUC =", ju807_m_area)
print("ju807_polysome_AUC =", ju807_p_area)
print("n2420_monosome_AUC =", n2420_m_area)
print("n2420_polysome_AUC =", n2420_p_area)
print("ju807_n2420_monosome_AUC =", ju807_n2420_m_area)
print("ju807_n2420_polysome_AUC =", ju807_n2420_p_area)
print("\r", "\r")
print("N2 polysome to monosome ratio:  ",N2_p_area/N2_m_area)
print("ju807 polysome to monosome ratio:  ",ju807_p_area/ju807_m_area)
print("n2420 polysome to monosome ratio:  ",n2420_p_area/n2420_m_area)
print("ju807_n2420 polysome to monosome ratio:  
",ju807_n2420_p_area/ju807_n2420_m_area)
