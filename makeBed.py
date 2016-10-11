import sys

def main():
	temp=[]
	
	with open(sys.argv[1]) as input:
		for line in input:
			data=line.split('\t')
			temp.append(data)

	f=open(str(sys.argv[1][:len(sys.argv[1])-6])+'.bed', 'w')
	f2=open(str(sys.argv[1][:len(sys.argv[1])-6])+'.bed.log', 'w')
	f2.write('ERROR! Following sequences not formatted properly:'+'\n')
	for i in range(0, len(temp)):
		if str(temp[i][0]) != '.' and float(temp[i][1])<float(temp[i][5]):
			f.write(str(temp[i][0])+'\t'+str(temp[i][1]+'\t'+str(temp[i][5]))+'\n')
		else:
			f2.write('\t'.join(temp[i])+'\n')


if __name__=='__main__':
	main();