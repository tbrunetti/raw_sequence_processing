import sys
from subprocess import call

#sys.argv[x]=all names of output files from bowtie2 alignment minus .sam ending
def main():

	f=open('complexity_scores.txt', 'a')
	
	for x in range (1, len(sys.argv)):
	
		#converts sam file to bam file for each argument
		#DO NOT put .sam ending in argument!
		print "converting sam to bam"
		call(["./samtools-1.2/samtools" , "view",  "-b",  "-S",  "-o",  str(sys.argv[x])+'.bam',  str(sys.argv[x])+'.fastq.sam'])
		print "FINISHED!, Now sorting..."
		
		#sorts bam file
		call(["./samtools-1.2/samtools",  "sort",  str(sys.argv[x])+'.bam',  'sorted'+str(sys.argv[x])])
		print "Sorting Complete"+'\n'+'Removing duplicate reads'
		
		#removes duplicates from a sorted bam file
		call(["./samtools-0.1.19/samtools", "rmdup",  'sorted'+str(sys.argv[x])+'.bam', 'noDup-sorted'+str(sys.argv[x])+'.bam'])
		print "Complete! sorting bam by name"
		
		#sort non-duplicated bams by name
		call(["./samtools-1.2/samtools",  "sort",  "-n",  'noDup-sorted'+str(sys.argv[x])+'.bam', 'sortedByName-noDup-'+str(sys.argv[x])])
		print "Converting to -bedpe"
		
		#convert sorted bam by name to bedpe
		f2=open('sortedByName-noDup-'+str(sys.argv[x])+'.bedpe', 'w')
		
		call(["./bedtools2/bin/bamToBed",  "-bedpe",  "-i",  'sortedByName-noDup-'+str(sys.argv[x])+'.bam'], stdout=f2)
		
		print "Converting to bed file"

		#convert bedpe to bed and remove unmapped regions
		call(["python", "makeBed.py", 'sortedByName-noDup-'+str(sys.argv[x])+'.bedpe'])

		call(['wc', '-l', 'sortedByName-noDup-'+str(sys.argv[x])+'.bed'], stdout=f)
		print "Final sort in process"
		
		f3=open('finalSort-noDup-'+str(sys.argv[x])+'.bed', 'w')
		#sort the bed file by default parameters
		call(["./bedtools2/bin/sortBed",  "-i",  'sortedByName-noDup-'+str(sys.argv[x])+'.bed'], stdout=f3)

		call(["mv", str(sys.argv[x])+'.bam', '/data/users/tbrunetti/tempFiles'])
		call(["mv", 'sorted'+str(sys.argv[x])+'.bam', '/data/users/tbrunetti/tempFiles'])
		call(["mv", 'noDup-sorted'+str(sys.argv[x])+'.bam', '/data/users/tbrunetti/tempFiles'])
		call(["mv", 'sortedByName-noDup-'+str(sys.argv[x])+'.bam', '/data/users/tbrunetti/tempFiles'])
		call(["mv", 'sortedByName-noDup-'+str(sys.argv[x])+'.bedpe', '/data/users/tbrunetti/tempFiles'])
		call(["mv", 'sortedByName-noDup-'+str(sys.argv[x])+'.bed', '/data/users/tbrunetti/tempFiles'])

		print "Job Complete!"

if __name__=='__main__':
	main();