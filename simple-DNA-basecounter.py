#fasta base counter 
#by Stephen Blazie
#please cite: Blazie et al., Eukaryotic initiation factor EIF-3.G augments 
mRNA translation efficiency to regulate neuronal activity. eLIFE. 2015
#Simple DNA base content calculator for .fasta inputs.
#Prints the proportion of C, T, G, A for fasta_filename (edit .fasta 
filename to specify which .fasta to process)

# Added printout of total number of gene's processed April 17, 2020
fasta_filename = '200410_hg38_5UTRs_spliced.fasta'
input_file = open(fasta_filename, 'r')
count_lines = 0
print("input file name: ", fasta_filename, 
file=open(fasta_filename+".tab", "w"))
print("input file name: ", fasta_filename)
print("Results in output file: ",fasta_filename+".tab\n")
print("csv results in output file: ",fasta_filename+".csv\n")
print ('{}'.format("gene,#_C,#_G,Total (CGTA)"), 
file=open(fasta_filename+".csv","w"))
    
num_c = 0
num_g = 0
num_t = 0
num_a = 0
num_genes = 0 # count total number of genes processed.

for line in input_file:
    line = line.upper()
    if line[0] == '>':
        total = num_c+num_g+num_t+num_a
        if total != 0:   # means we have been reading a gene.
            num_genes += 1
            print ('number of Base Pairs ( C G T A):', num_c, num_g, 
num_t, num_a)
            print ('Total number of Base Pairs: ',total)
            print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
                   
format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'),"\n")
            print 
('{}{}{}{}{}{}{}'.format(gene,",",num_c,",",num_g,",",total), 
file=open(fasta_filename+".csv","a"))
            print ('number of Base Pairs ( C G T A):', num_c, num_g, 
num_t, num_a, file=open(fasta_filename+".tab", "a"))
            print ('Total number of Base Pairs: ',total, 
file=open(fasta_filename+".tab", "a"))
            print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
                   
format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'), 
file=open(fasta_filename+".tab", "a"))

        gene = line[1:-1]  # got a new gene
        num_c = 0
        num_g = 0
        num_t = 0
        num_a = 0
        total =0
        print("Gene: ",gene)
    else:
        for char in line:
            if char == 'C':
                num_c +=1
            elif char == 'G':
                num_g +=1
            elif char == 'T':
                num_t +=1
            elif char == 'A':
                num_a +=1                        
total = num_c+num_g+num_t+num_a                
if total != 0:   # means we have been reading a gene.
    num_genes += 1
    print ('number of Base Pairs ( C G T A):', num_c, num_g, num_t, num_a)
    print ('Total number of Base Pairs: ',total)
    print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
           
format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'),"\n")
    print ('{}{}{}{}{}{}{}'.format(gene,",",num_c,",",num_g,",",total), 
file=open(fasta_filename+".csv","a"))

    print ('number of Base Pairs ( C G T A):', num_c, num_g, num_t, num_a, 
file=open(fasta_filename+".tab", "a"))
    print ('Total number of Base Pairs: ',total, 
file=open(fasta_filename+".tab", "a"))
    print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
           format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'), 
file=open(fasta_filename+".tab", "a"))

    print ('Total number of genes in output file:', num_genes )

