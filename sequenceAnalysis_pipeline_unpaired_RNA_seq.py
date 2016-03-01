import sys
from subprocess import call

#sys.argv[x]=all names of output files from bowtie2 alignment minus .sam ending
def main():

	
	for x in range (1, len(sys.argv)):
	
		#converts sam file to bam file for each argument
		#DO NOT put .sam ending in argument!
		print "converting sam to bam"
		call(["./samtools-1.2/samtools" , "view",  "-b",  "-S",  "-o",  str(sys.argv[x])+'.bam',  str(sys.argv[x])+'.sam'])
		print "FINISHED!, Now sorting..."
		
		#sorts bam file
		call(["./samtools-1.2/samtools",  "sort",  str(sys.argv[x])+'.bam',  'sorted'+str(sys.argv[x])])
		print "Sorting Complete...Converting to bed file"+'\n'
		
		f3=open('final-RNAseqReads-'+str(sys.argv[x])+'.bed', 'w')
		#sort the bed file by default parameters
		call(["./bedtools2/bin/bamToBed",  "-i",  'sorted'+str(sys.argv[x])+'.bam'], stdout=f3)

		call(["mv", str(sys.argv[x])+'.bam', '/data/users/tbrunetti/tempFiles'])
		call(["mv", 'sorted'+str(sys.argv[x])+'.bam', '/data/users/tbrunetti/tempFiles'])
		
		print "Job Complete!"

if __name__=='__main__':
	main();