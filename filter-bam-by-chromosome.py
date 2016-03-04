import sys
import os
from subprocess import call


#sys.argv[1] is a file with a list of chromosomes to keep in a bam (chr*** format)
#the list needs to be formated with one chromosome per line
#sys.argv[2] is the original bam file that is to be filetered out
#sys.argv[3] is only required if using fixBamHeader; a one column list of all the header patterns to manipulate


def filterBam(pathToSamtools, pathToBamFile):
	#appends results for each chromosome
	output=open('newBam_chromsomeSpecific_'+str(sys.argv[2]), 'a')
	#change directory into samtools working directory
	os.chdir(pathToSamtools)
	with open(sys.argv[1]) as input:
		for line in input:
			line=line.rstrip('\n')
			#call samtools from samtools directory
			call(['samtools', 'view', '-b', str(pathToBamFile)+str(sys.argv[2]), str(line)], stdout=output)

def fixBamHeader(pathToSamtools, pathToBamFile):
	finalFormat=open('reformatted-header-'+str(sys.argv[2])+'.bam', 'w')
	#these two files are temporary files that get deleted after the BAM is reformatted
	header=open('originalHeader.sam', 'w')
	temp=open('tempHeader.sam', 'w')
	
	os.chdir(pathToSamtools)
	print "Extracting original BAM header..."
	call(['samtools', 'view', '-H', str(pathToBamFile)+'newBam_chromsomeSpecific_'+str(sys.argv[2])], stdout=header)
	with open(sys.argv[3]) as input:
		for line in input:
			line=line.rstrip('\n')	
		call(['sed', '-s', '/'+str(line)+'/d', '/mnt/originalHeader.sam'], stdout=temp)

	print "adding new header to new BAM..."
	os.chdir(pathToSamtools)
	call(['samtools', 'reheader', '/mnt/tempHeader.sam', str(pathToBamFile)+'newBam_chromsomeSpecific_'+str(sys.argv[2])], stdout=finalFormat)
	print "Finished reformatting header, cleaning up temporary files..."
	os.chdir(pathToBamFile)
	call(['rm', '-r', 'tempHeader.sam'])
	call(['rm', '-r', 'originalHeader.sam'])

	print "Job Complete!"

if __name__=='__main__':
	pathToSamtools='/home/ubuntu/TOOLS/samtools-0.1.19'
	pathToBamFile='/mnt/'
	#filterBam(pathToSamtools, pathToBamFile);
	fixBamHeader(pathToSamtools, pathToBamFile);