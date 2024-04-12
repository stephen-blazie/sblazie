#uORF_finder_tool
#locates uORFs in 5'UTRs from a .fasta input
#by Stephen Blazie
#please cite: Blazie et al., Eukaryotic initiation factor EIF-3.G augments 
mRNA translation efficiency to regulate neuronal activity. eLIFE. 2015

import Bio
from Bio import SeqIO

with open("output.fasta", "w") as f:
    uORF_count=0 # no. of genes with at least one uORF
    quartet_count=0 # no. of genes with at least one GGGG
    for seq_record in SeqIO.parse("EIF3_5UTRs_spliced.fasta", "fasta"):
        i=0
        j=0
        gene_count=0
        quartet_gene_count=0
        for x in seq_record.seq:
            if seq_record.seq[i:i+3] == 'ATG':
                #print(seq_record.id, "\tStart codon at position", i, 
"to", i+2)
                j=i+3
                for elem in seq_record.seq[i: :3]:
                    codon=seq_record.seq[j:j+3]
                    if codon == 'TGA' or codon == 'TAA' or codon == 'TAG':
                        if gene_count < 1:
                            print(seq_record.id, 
"uORF",seq_record.seq[i:j+3])
                            gene_count+=1
                            uORF_count+=1
                        #print("\t\tSTOP codon at position", j, "to", j+2)
                        #print("\b\tuORF:", seq_record.seq[i:j+3])
                        break #break for loop since first stop codon in 
this uORF is reached
                    j+=3
            if seq_record.seq[i:i+5] == 'GGGGG':
                if quartet_gene_count<1:
                    quartet_count +=1
                    quartet_gene_count +=1
                    print(seq_record.id, "g5", seq_record.seq[i-10:i+14])
            i+=1
print("Total uORFs found:", uORF_count)
print("Total G-quartets found", quartet_count)
#print(uORF_genes)
         

