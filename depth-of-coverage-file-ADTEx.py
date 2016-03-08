import sys
import os
from subprocess import call

#sys.argv[1] = bam file with duplicates removed
#sys.argv[2] = bedfile of capture panel`
#sys.argv[3] = only required if using formatDOC(pathToBam), single column text file of chromosome to keep in analysis
def makeDOC(pathToBedtools, pathToBAM, pathToBed):
	depthOfCoverage=open(str(pathToBAM)+str(sys.argv[1][:-4])+'-DOC-file.txt', 'w')
	os.chdir(pathToBedtools)
	call(['./coverageBed', '-abam', str(pathToBAM)+str(sys.argv[1]), '-b', str(pathToBed)+str(sys.argv[2]), '-d'], stdout=depthOfCoverage)

def formatDOC(pathToBAM):
	os.chdir(pathToBAM)
	chromosomesToKeep=[]
	formattedDOC=open(str(sys.argv[1][:-4])+'-DOC-file-formatted.txt', 'w')
	with open(sys.argv[3]) as input:
		for line in input:
			chromosomesToKeep.append(line.rstrip('\n'))
	
	with open(str(sys.argv[1][:-4])+'-DOC-file.txt') as input:
		for line in input:
			line=line.split('\t')
			del line[3]
			if line[0] in chromosomesToKeep:
				formattedDOC.write('\t'.join(line))
			else:
				print line[0]

if __name__=='__main__':
	pathToBedtools='/home/ubuntu/TOOLS/bedtools2/bin/'
	pathToBAM='/mnt/'
	pathToBed='/mnt/'
	makeDOC(pathToBedtools, pathToBAM, pathToBed);
	formatDOC(pathToBAM);