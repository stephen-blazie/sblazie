#GC-base positioning calculator
#by Stephen Blazie
#please cite: Blazie et al., Eukaryotic initiation factor EIF-3.G augments 
mRNA translation efficiency to regulate neuronal activity. eLIFE. 2015
#Graphs GC content in 5'UTRs. Accepts .fasta inputs and returns matlab 
plot graph outputs.

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy
fasta_filename = 'EIF3G_5UTRs_spliced.fasta'
input_file = open(fasta_filename, 'r')
count_lines = 0
print("input file name: ", fasta_filename, 
file=open(fasta_filename+".tab", "w"))
print("input file name: ", fasta_filename)
print("Results in output file: ",fasta_filename+".tab\n")
print("csv results in output file: ",fasta_filename+".csv\n")
print ('{}'.format("gene,#_C,#_G,Total (CGTA)"), 
file=open(fasta_filename+".csv","w"))
print ("gene, total, bins,", file=open(fasta_filename+"_bins.csv","w"))

# the following variables let you set the binsize to a fixed # nucleotides 
or a # of the total.
# if the bin_percent is 0 it uses a fixed binsize.  
# If bin_percent is nonzero it takes that as a % of the gene.  Each gene 
will be different binsize in that case
binsize = 10
bin_percent = 0

num_c = 0
num_g = 0
num_t = 0
num_a = 0
charnum = 0
genes_processed = 0
bins = []   # create a list of bins
for line in input_file:
    line = line.upper()
    line = line.rstrip('\n')  # this removes the newline character in the 
string
    if line[0] == '>':   
        total = num_c+num_g+num_t+num_a
        if total >= 10:   # means we have been reading a gene sequence
            numbins = charnum//binsize
            print ("charnum, numbins",charnum,numbins)
            print ("This is the bins", bins[0:numbins])
            if (numbins >0):
                y = numpy.array(bins[0:numbins])
                y = y*100/(binsize) # Use this line if you want the bin 
graph to be % of GC instead of total nucleotides
                x = numpy.arange(numbins)
                plt.bar(x,y)
                plt.show()
                genes_processed += 1
                print (gene,total,*y,sep=', ', 
file=open(fasta_filename+"_bins.csv","a"))
            print(fasta_filename," bins=",bins[0:numbins])
#            print("Base=",char, 
"bin=",bins[charnum//5],"charnum=",charnum,"charnum//5 =",charnum//5)
            print ('number of nucleotides ( C G T A):', num_c, num_g, 
num_t, num_a)
            print ('Total number of nucleotides: ',total)
            print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
                   
format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'),"\n")
            print 
('{}{}{}{}{}{}{}'.format(gene,",",num_c,",",num_g,",",total), 
file=open(fasta_filename+".csv","a"))
            print ('number of nucleotides ( C G T A):', num_c, num_g, 
num_t, num_a, file=open(fasta_filename+".tab", "a"))
            print ('Total number of nucleotides: ',total, 
file=open(fasta_filename+".tab", "a"))
            print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
                   
format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'), 
file=open(fasta_filename+".tab", "a"))
        gene = line[1:] 
        num_c = 0
        num_g = 0
        num_t = 0
        num_a = 0
        total =0
        charnum = 0  
        bins = [0]*1000 # reinitialize the bins to empty 1000 elements
        print("Gene: ",gene)
    else:  # gets here when we have a line of nucleotides for a gene
        line = line[::-1] 
        num_nucleotides = len(line)
        if (bin_percent > 0):
            binsize = (len(line)*bin_percent)//100 
            if binsize > 0 :
                if len(line)%binsize != 0 :    # means we need an extra 
bin at the end for overflow
                    binsize += 1
        if (binsize != 0):
            print("line length binsize bin_percent ",len(line), binsize, 
bin_percent)
            for char in line:
                if char == 'C':
                    num_c +=1
                    bins[charnum//binsize] += 1
                elif char == 'G':
                    num_g +=1
                    bins[charnum//binsize] += 1
                elif char == 'T':
                    num_t +=1
                elif char == 'A':
                    num_a +=1    
                else:
                    print("Improper base pair in input file", ord(char))
    #            print("Base=",char, 
"bin=",bins[charnum//5],"charnum=",charnum,"charnum//5 =",charnum//5)
                charnum += 1
total = num_c+num_g+num_t+num_a                
if total >= 10:   # means we have been reading a gene.
    numbins = charnum//binsize
        
# DO a quick bargraph of the bins
    y = numpy.array(bins[0:numbins])
    y = y*100/(binsize) # Use this line if you want the bin graph to be % 
of GC instead of total nucleotides
    x = numpy.arange(numbins)
    plt.bar(x,y)
    plt.show()
    genes_processed += 1
    print (gene,total,*y,sep=', ', 
file=open(fasta_filename+"_bins.csv","a"))
    print ("charnum, numbins",charnum,numbins)
    print ("This is the bins", bins[0:numbins])
    print ('number of nucleotides ( C G T A):', num_c, num_g, num_t, 
num_a)
    print ('Total number of nucleotides: ',total)
    print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
           
format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'),"\n")
    print ('{}{}{}{}{}{}{}'.format(gene,",",num_c,",",num_g,",",total), 
file=open(fasta_filename+".csv","a"))

    print ('number of nucleotides ( C G T A):', num_c, num_g, num_t, 
num_a, file=open(fasta_filename+".tab", "a"))
    print ('Total number of nucleotides: ',total, 
file=open(fasta_filename+".tab", "a"))
    print ('% of total: ( C G T A):',format ( 
100*num_c/total,'.2f'),format(100*num_g/total, '.2f'),\
           format(100*num_t/total,'.2f'),format(100*num_a/total,'.2f'), 
file=open(fasta_filename+".tab", "a"))
    print ("Total number of Genes processed:   ", genes_processed)


