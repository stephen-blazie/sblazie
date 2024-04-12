#Tissue-specific seCLIP-seq analyzer
#detects RBP binding site differences between samples (.csv converted .bed 
files as input)
#by Stephen Blazie
#please cite: Blazie et al., Eukaryotic initiation factor EIF-3.G augments 
mRNA translation efficiency to regulate neuronal activity. eLIFE. 2015

import pandas as pd
N2 = pd.read_csv("bed_files/N2_full_reads.csv") 
WT_rep1 = pd.read_csv("bed_files/4941_full_reads.csv")
WT_rep2 = pd.read_csv("bed_files/4942_full_reads.csv")
C130Y_rep1 = pd.read_csv("bed_files/5651_full_reads.csv")
C130Y_rep2 = pd.read_csv("bed_files/5652_full_reads.csv")
delRRM_rep1 = pd.read_csv("bed_files/6231_full_reads.csv")
delRRM_rep2 = pd.read_csv("bed_files/6232_full_reads.csv")


def remove_errors(dataframe):
    i = dataframe[((dataframe.genename == 'sdha-1') &(dataframe.location 
== 'CDS'))].index
    dataframe = dataframe.drop(i)  
    i = dataframe[((dataframe.genename == 'sel-2') &(dataframe.location == 
'CDS'))].index
    dataframe = dataframe.drop(i) 
    i = dataframe[((dataframe.genename == 'lev-10') &(dataframe.location 
== 'CDS'))].index
    dataframe = dataframe.drop(i) 
    i = dataframe[((dataframe.genename == 'F43C11.8') &(dataframe.location 
== 'CDS'))].index
    dataframe = dataframe.drop(i) 
    i = dataframe[((dataframe.genename == 'sepa-1') &(dataframe.location 
== 'CDS'))].index
    dataframe = dataframe.drop(i) 
    i = dataframe[((dataframe.genename == 'F54B3.1') &(dataframe.location 
== 'CDS'))].index
    dataframe = dataframe.drop(i) 
    return dataframe


#decide how many peaks show up in both replicates. This will set a rule 
that peak must be called in both reps
def merge_replicates(rep1, rep2, reps_concat):
    df = rep1.merge(rep2, on = ['genename'], how='left', indicator=True)
    df = df[(df._merge=='both')]
    df = df.groupby(['genename']).size().to_frame('size').reset_index()
    df.drop(['size'], axis=1, inplace=True)
    
    dataframe = reps_concat.merge(df, on = ['genename'], how='left', 
indicator=True)
    dataframe = dataframe[(dataframe._merge=='both')]
    dataframe.drop(['_merge'], axis=1, inplace=True)
    return dataframe

#function filters the merged-peak files for foldchange>=1.5 with >=20 CLIP 
reads
def filter_peaks(dataframe):
    
dataframe=dataframe[(dataframe.foldchange>=1.5)&(dataframe.CLIP_reads>=20)]
    return dataframe

#function groups by genename and feature location, and adds another column 
that counts the numer of peaks map to that feature
def count_peaks(rep1, rep2):
    rep1_count = rep1.groupby(['genename', 
'location']).size().to_frame('peak_count').reset_index()
    rep2_count = rep2.groupby(['genename', 
'location']).size().to_frame('peak_count').reset_index()
    rep1_rep2_concat = pd.concat([rep1_count, rep2_count], axis=0)
    dataframe = rep1_rep2_concat.groupby(['genename', 'location'], 
as_index=False).agg({'peak_count':['max']})
    dataframe.columns = dataframe.columns.droplevel(1)
    #dataframe.drop(['foldchange'], axis=1, inplace=True)
    return dataframe

def subtract_N2(dataframe, peakcounts, peakcounts_to_subtract):
    peakcounts_merged = peakcounts.merge(peakcounts_to_subtract, on = 
['genename', 'location'], how = 'left', indicator=True)
    # note that the '|' in the code below stands in place of the boolean 
'OR', which is the same as an SQL Select * From x where a=b or a=c
    dataframe_concat = 
peakcounts_merged[(peakcounts_merged._merge=='left_only')|((peakcounts_merged._merge=='both')&(peakcounts_merged.peak_count_x>peakcounts_merged.peak_count_y))]
    dataframe_concat.drop(['_merge'], axis=1, inplace=True)
    merged = dataframe.merge(dataframe_concat, on = ['genename', 
'location'], how = 'left', indicator=True)
    dataframe = merged[(merged._merge=='both')]
    dataframe.drop(['peak_count_y', '_merge'], axis=1, inplace=True)
    dataframe.set_axis(['Chr', 'start', 'end', 'pvalue', 'foldchange', 
'strand', 'WBGene', 'genename', 'location', 'CLIP_reads', 'INPUT_reads', 
'peak_count'], axis=1, inplace=True)
    return dataframe

def subtract_delRRM(dataframe, peakcounts, peakcounts_to_subtract):
    peakcounts_merged = peakcounts.merge(peakcounts_to_subtract, on = 
['genename', 'location'], how = 'left', indicator=True)
    # note that the '|' in the code below stands in place of the boolean 
'OR', which is the same as an SQL Select * From x where a=b or a=c
    dataframe_concat = 
peakcounts_merged[(peakcounts_merged._merge=='left_only')]
    dataframe_concat.drop(['_merge'], axis=1, inplace=True)
    merged = dataframe.merge(dataframe_concat, on = ['genename', 
'location'], how = 'left', indicator=True)
    dataframe = merged[(merged._merge=='both')]
    dataframe.drop(['_merge', 'foldchange_y'], axis=1, inplace=True)
    dataframe.set_axis(['Chr', 'start', 'end', 'pvalue', 'foldchange', 
'strand', 'WBGene', 'genename', 'location', 'CLIP_reads', 'INPUT_reads', 
'peak_count'], axis=1, inplace=True)
    return dataframe

#function takes the subtracted peak table and groups by peak gene_name and 
feature(location) so that the resulting
#table has only one peak per location per gene. The groupby selects the 
peak with the most reads when more than one
#peak is found per feature(location). IMPORTANT!! Often, there are 
multiple peaks with the same number of reads in
# the same feature. In these cases, both peaks are taken. This is why 
there are often multiple peaks per location in the same gene
def group(dataframe):
    grouped = dataframe.groupby(['genename', 'location'], 
as_index=False).agg({'CLIP_reads':['max']})
    grouped.columns = grouped.columns.droplevel(1)
    merged = grouped.merge(dataframe, on = ['genename', 'location', 
'CLIP_reads'], how = 'left', indicator=True)
    merged = merged[(merged._merge=='both')]
    merged.drop(['_merge'], axis=1, inplace=True) 
    merged = merged[['Chr', 'start', 'end', 'pvalue', 'foldchange', 
'strand', 'WBGene', 'genename', 'location', 'CLIP_reads', 'INPUT_reads']]
    merged = merged.drop_duplicates()
    return merged

#function restricts the final peak list to those peaks meeting a certain 
location criteria. ex. 5'UTR/CDS
def restrict(dataframe, criteria):
    dataframe = dataframe[dataframe['location'].isin(criteria)]
    return dataframe

#removing erroneous peaks
WT_rep1 = remove_errors(WT_rep1)
WT_rep2 = remove_errors(WT_rep2)
C130Y_rep1 = remove_errors(C130Y_rep1)
C130Y_rep2 = remove_errors(C130Y_rep2)
delRRM_rep1 = remove_errors(delRRM_rep1)
delRRM_rep2 = remove_errors(delRRM_rep2)
N2 = remove_errors(N2)

#filtering the raw peak files for foldchange>=1.5 with >=20 CLIP reads
N2_filtered = filter_peaks(N2)
WT_rep1_filtered = filter_peaks(WT_rep1)
WT_rep2_filtered = filter_peaks(WT_rep2)
C130Y_rep1_filtered = filter_peaks(C130Y_rep1)
C130Y_rep2_filtered = filter_peaks(C130Y_rep2)
delRRM_rep1_filtered = filter_peaks(delRRM_rep1)
delRRM_rep2_filtered = filter_peaks(delRRM_rep2)

#concatenate the replicates before filtering/subtraction
WT_concat=pd.concat([WT_rep1_filtered, WT_rep2_filtered], axis=0)
C130Y_concat=pd.concat([C130Y_rep1_filtered, C130Y_rep2_filtered], axis=0)
delRRM_concat=pd.concat([delRRM_rep1_filtered, delRRM_rep2_filtered], 
axis=0)

#further filters for peaks that are called in both replicates. DO NOT use 
the filtered files, use raw for this
WT_merged=merge_replicates(WT_rep1, WT_rep2, WT_concat)
C130Y_merged=merge_replicates(C130Y_rep1, C130Y_rep2, C130Y_concat)
delRRM_merged=merge_replicates(delRRM_rep1, delRRM_rep2, delRRM_concat)

N2_peakcounts = count_peaks(N2_filtered, N2_filtered)                                                                                                           
WT_peakcounts = count_peaks(WT_rep1_filtered, WT_rep2_filtered)
C130Y_peakcounts = count_peaks(C130Y_rep1_filtered, C130Y_rep2_filtered)
delRRM_peakcounts = count_peaks(delRRM_rep1_filtered, 
delRRM_rep2_filtered)

#subtract the N2
WT_subN2 = subtract_N2(WT_merged, WT_peakcounts, N2_peakcounts)
WT_subN2_grouped = group(WT_subN2)
#print(WT_subN2_grouped.head)
C130Y_subN2 = subtract_N2(C130Y_merged, C130Y_peakcounts, N2_peakcounts)
C130Y_subN2_grouped = group(C130Y_subN2)
delRRM_subN2 = subtract_N2(delRRM_merged, delRRM_peakcounts, 
N2_peakcounts)
delRRM_subN2_grouped = group(delRRM_subN2)

def tables(dataset, subN2_grouped, subN2_subdelRRM_grouped):
    subN2_total_genes = 
subN2_grouped[['genename']].drop_duplicates().reset_index(drop=True)
    subN2_coding_clusters = 
subN2_grouped[subN2_grouped['location'].isin(['5utr', 'CDS', '3utr', 
'stop_codon'])]
    
subN2_coding_genes=subN2_coding_clusters[['genename']].drop_duplicates().reset_index(drop=True)
    subN2_noncoding_clusters = 
subN2_grouped[~subN2_grouped['location'].isin(['5utr', 'CDS', '3utr', 
'stop_codon'])]
    
subN2_noncoding_genes=subN2_noncoding_clusters[['genename']].drop_duplicates().reset_index(drop=True)
    if dataset == "WT" or dataset == "C130Y":
        subN2_subdelRRM_coding_clusters = 
subN2_subdelRRM_grouped[subN2_subdelRRM_grouped['location'].isin(['5utr', 
'CDS', '3utr', 'stop_codon'])]
        
subN2_subdelRRM_coding_genes=subN2_subdelRRM_coding_clusters[['genename']].drop_duplicates().reset_index(drop=True)
        subN2_subdelRRM_noncoding_clusters = 
subN2_subdelRRM_grouped[~subN2_subdelRRM_grouped['location'].isin(['5utr', 
'CDS', '3utr', 'stop_codon'])]
        subN2_subdelRRM_noncoding_genes = 
subN2_subdelRRM_noncoding_clusters[['genename']].drop_duplicates().reset_index(drop=True)
        subN2_subdelRRM_coding_clusters_3UTR = 
subN2_subdelRRM_grouped[subN2_subdelRRM_grouped['location'].isin(['3utr', 
'stop_codon'])]
        subN2_subdelRRM_coding_clusters_5UTRprox = 
subN2_subdelRRM_grouped[subN2_subdelRRM_grouped['location'].isin(['5utr', 
'CDS'])]
        
    print("Total", dataset, "_subN2_clusters:", subN2_grouped.shape[0])
    print(dataset, "_subN2_coding_clusters:", 
subN2_coding_clusters.shape[0])
    print(dataset, "_subN2_noncoding_clusters:", 
subN2_noncoding_clusters.shape[0])
    print("\n")
    print(dataset, "_subN2_coding_genes:", subN2_coding_genes.shape[0])
    print(dataset, "_subN2_noncoding_genes:", 
subN2_noncoding_genes.shape[0])
    print("\n")
    print("---------------------------")
    if dataset == "WT" or dataset == "C130Y":
        print("Total", dataset, "_subN2_subdelRRM_clusters:", 
subN2_subdelRRM_grouped.shape[0])
        print(dataset, "_subN2_subdelRRM_coding_clusters:", 
subN2_subdelRRM_coding_clusters.shape[0])
        print(dataset, "_subN2_subdelRRM_noncoding_clusters:", 
subN2_subdelRRM_noncoding_clusters.shape[0])
        print("\n")
        print(dataset, "_subN2_subdelRRM_coding_genes:", 
subN2_subdelRRM_coding_genes.shape[0])
        print(dataset, "_subN2_subdelRRM_noncoding_genes:", 
subN2_subdelRRM_noncoding_genes.shape[0])
        print("\n")
        print("---------------------------")
        print(dataset, "_subN2_subdelRRM_3UTR_clusters:", 
subN2_subdelRRM_coding_clusters_3UTR.shape[0])
        print(dataset, "_subN2_subdelRRM_5UTRprox_clusters:", 
subN2_subdelRRM_coding_clusters_5UTRprox.shape[0])
        print("\n")
        print("---------------------------")


#tables("WT", WT_subN2_grouped, WT_subN2_subdelRRM_grouped)
#tables("C130Y", C130Y_subN2_grouped, C130Y_subN2_subdelRRM_grouped)


"""
WT_subN2_total_genes = 
WT_subN2_grouped[['genename']].drop_duplicates().reset_index(drop=True)
WT_subN2_coding_clusters = 
WT_subN2_grouped[WT_subN2_grouped['location'].isin(['5utr', 'CDS', '3utr', 
'stop_codon'])]
WT_subN2_coding_genes=WT_subN2_coding_clusters[['genename']].drop_duplicates().reset_index(drop=True)
WT_subN2_noncoding_clusters = 
WT_subN2_grouped[~WT_subN2_grouped['location'].isin(['5utr', 'CDS', 
'3utr', 'stop_codon'])]
WT_subN2_noncoding_genes=WT_subN2_noncoding_clusters[['genename']].drop_duplicates().reset_index(drop=True)
print("Total_WT_subN2_clusters:", WT_subN2_grouped.shape[0])
print("WT_subN2_coding_clusters:", WT_subN2_coding_clusters.shape[0])
print("WT_subN2_noncoding_clusters:", 
WT_subN2_noncoding_clusters.shape[0])
#print("Total_WT_subN2_genes:", WT_subN2_total_genes.shape[0])
print("WT_subN2_coding_genes:", WT_subN2_coding_genes.shape[0])
print("WT_subN2_noncoding_genes:", WT_subN2_noncoding_genes.shape[0])
"""


#subtract the delRRM, the first line shortens the group table to just the 
three needed columns to do the subtraction
delRRM_subN2_peaks = delRRM_subN2_grouped[['genename', 'location', 
'foldchange']]
WT_subN2_subdelRRM = subtract_delRRM(WT_subN2_grouped, WT_peakcounts, 
delRRM_subN2_peaks)
WT_subN2_subdelRRM_grouped = group(WT_subN2_subdelRRM)
C130Y_subN2_subdelRRM = subtract_delRRM(C130Y_subN2_grouped, 
C130Y_peakcounts, delRRM_subN2_peaks)
C130Y_subN2_subdelRRM_grouped = group(C130Y_subN2_subdelRRM)

#the following generates numbers of clusters/genes before/after 
subtraction of N2 and delRRM for manuscript tables
tables("WT", WT_subN2_grouped, WT_subN2_subdelRRM_grouped)
tables("C130Y", C130Y_subN2_grouped, C130Y_subN2_subdelRRM_grouped)
tables("delRRM", delRRM_subN2_grouped, delRRM_subN2_grouped)


#filtering final list of peaks by 5'UTR proximal or 3'UTR
C130Y_subN2_subdelRRM_5UTRproximal = 
restrict(C130Y_subN2_subdelRRM_grouped,['5utr','CDS'])
C130Y_subN2_subdelRRM_5UTRproximal.to_csv("scatter_plots/inputs/C130Y_targets.csv")
C130Y_subN2_subdelRRM_3UTR = 
restrict(C130Y_subN2_subdelRRM_grouped,['3utr','stop_codon'])
C130Y_subN2_subdelRRM_3UTR.to_csv("scatter_plots/inputs/C130Y_3UTR_targets.csv")
WT_subN2_subdelRRM_5UTRproximal = 
restrict(WT_subN2_subdelRRM_grouped,['5utr','CDS'])
WT_subN2_subdelRRM_5UTRproximal.to_csv("scatter_plots/inputs/WT_3UTR_targets.csv")
WT_subN2_subdelRRM_3UTR = 
restrict(WT_subN2_subdelRRM_grouped,['3utr','stop_codon'])
WT_subN2_subdelRRM_3UTR.to_csv("scatter_plots/inputs/WT_3UTR_targets.csv")
print(C130Y_subN2_subdelRRM_5UTRproximal.shape)
print(WT_subN2_subdelRRM_5UTRproximal.shape)
print("3UTR shape C130Y:", C130Y_subN2_subdelRRM_3UTR.shape)
print("3UTR shape WT:", WT_subN2_subdelRRM_3UTR.shape)

#comparing full gene list among WT and C130Y with the output of SQL script
full_gene_list = pd.concat([WT_subN2_subdelRRM_5UTRproximal, 
C130Y_subN2_subdelRRM_5UTRproximal], axis=0)
full_gene_list = full_gene_list[['genename', 'location']]
full_gene_list = full_gene_list.drop_duplicates()
full_gene_list.to_csv("scatter_plots/inputs/eif3_targets.csv")
full_gene_list = full_gene_list[['genename']]
print (full_gene_list.shape)
full_gene_list = full_gene_list.drop_duplicates()
print (full_gene_list.shape)
full_gene_list.to_csv("5UTR_analysis/inputs/eif3_targets_grouped.csv")
targets_232 = pd.read_excel("232_eif-3g_target_genes.xlsx")
joined_targets = full_gene_list.merge(targets_232, on = ['genename'], how 
= 'left', indicator = True)
joined_targets_left = joined_targets[(joined_targets._merge=='left_only')]
print (joined_targets_left.shape)
print(joined_targets_left) 

