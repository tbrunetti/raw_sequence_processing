import sys
import os
from multiprocessing import Pool
import time
import csv

#sys.argv[1]=capture set name (only used for title of output file)
#sys.argv[2]=read/run name to match against capture (just used for name of output file)
#sys.argv[3]=bed file of capture regions
#sys.argv[4] and beyond=bed file of reads
			#split <file> -n <int chunks>
keyNotFound=open('Cannot_match_to_capture_reads.txt', 'w')
finalResults=[]
def makeCapture():
	print "making capture region libary..."
	#key=chromosome in bed file
	#value=list of tuples (start nt, end nt) of capture region in bed from bed file
	captureSites={}
	f=open(sys.argv[3], 'r')
	for captureRegion in f.xreadlines():
		captureRegion=captureRegion.rstrip()
		captureRegion=captureRegion.split('\t')
		#checks if chromosome key has already been made and adds tuple
		if captureRegion[0] in captureSites:
			captureSites[captureRegion[0]]=captureSites[captureRegion[0]]+[(captureRegion[1], captureRegion[2])] 
		#if chromosome key had not been made
		else:
			captureSites[captureRegion[0]]=[(captureRegion[1], captureRegion[2])]

	return captureSites

def fileRead(captureSites, textfileOfReads):
	print "Worker ID"+str(os.getpid())+' has received a new job with job name: '+str(textfileOfReads)
	results=[]
	with open(textfileOfReads, 'r') as input:
		for line in input:
			line=line.rstrip()
			line=line.split('\t')
			#call function selectReads to determine if a line of bed file is in range
			inRange=selectReads(captureSites, line)
			if inRange!='None':
				results.append(inRange)
	return results

def selectReads(captureSites, line):
	#try and except in order to catch error resulting in chromosome not in capture regions
	try:
		for tuples in range(len(captureSites[line[0]])):
			readStatus=checkRange(int(captureSites[line[0]][tuples][0]), int(captureSites[line[0]][tuples][1]), int(line[1]), int(line[2]));
			if readStatus==True:
				return line
	except KeyError:
		print "KeyError, chromosome does not exist in capture set, returning 'None'"
		keyNotFound=open('Cannot_match_to_capture_reads.txt', 'a')
		keyNotFound.write(str(line)+'\n')
		return 'None'


#if return True, add read to list, else skip read
def checkRange(capStart, capEnd, readStart, readEnd):	
	return max(capStart, readStart)<=min(capEnd, readEnd)


#concatenates reults as they finish
def retrieveResults(results):
	print "results are being received at "+ str(time.ctime())
	finalResults.extend(results)	

if __name__=='__main__':
	#numbers of workers to uses
	workers=Pool(processes=5)
	#onTargetReads=open(str(sys.argv[2])+'-reads-overlapping-'+str(sys.argv[1])+'-capture-region-'+str(time.strftime("%Y%m%d"))+'.bed', 'w')
	#calls function makeCapture to make capture library regions
	captureSites=makeCapture()
	for i in range(4, len(sys.argv)):
		address=os.getcwd()+'/'+str(sys.argv[i])
		workers.apply_async(fileRead, kwds={"captureSites":captureSites, "textfileOfReads":address}, callback=retrieveResults)
	workers.close()
	workers.join()
	#final results will write to file created belows
	print "The total number of sequences that map to a capture regions are "+str(len(finalResults))	
	print "Writing final results to file"
	with open(str(sys.argv[2])+'-reads-overlapping-'+str(sys.argv[1])+'-capture-region-'+str(time.strftime("%Y%m%d"))+'.bed', 'w') as f:
		csvWriter=csv.writer(f)
		csvWriter.writerows(finalResults)

	#for i in range(len(finalResults)):
	#	onTargetReads.write(str(finalResults)[i])
