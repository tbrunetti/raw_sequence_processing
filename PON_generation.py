import os
from chunkypipes.components import *
import subprocess

class Pipeline(BasePipeline):
	
	def dependencies(self):
		return []

	def description(self):
		return 'Creates a panel of normals from BAM files'

	def configure(self):
		return {
			'GATK':{
				#assuming java compiler and file is within path scope, write "java -jar GenomeAnalysisTK.jar"
				'path': 'Full path to GATK jar file',
				'reference': 'Full path to reference genome in fasta format',
				'inputBAM': 'Full path to directory of all BAM files to be analyzed',
				'dbSNP': 'Full path to dbSNP vcf',
				'cosmic': 'Full path to COSMIC vcf',
				'target_intervals': 'Full path to BED file of target regions',
				'output_VCF': 'Full path to directory of individual normal variant vcf files, no / at end, CANNOT BE SAME DIRECTORY OF BAM FILE LOCATION!'
				}	
			}

	def add_pipeline_args(self, parser):
		#TODO: add other arguments avaiable in case user wants to implement them, else set to default
		parser.add_argument('-o', required=True, help='path and name of final combined panel of normal VCF (formatted: /path/filename.vcf)')
		parser.add_argument('-minN', default='2', help='min number of vcf files in order to retain variant called for PON list')

	def run_pipeline(self, pipeline_args, pipeline_config):
		#creates the Software object call, althougth mutect==combineAllVariants
		#the -T parameter is different so only made for code readability
		mutect = Software('GATK', pipeline_config['GATK']['path'])
		combineAllVariants=Software('GATK', pipeline_config['GATK']['path'])
		#iterates through all BAMs can runs mutect object with appropriate paramters
		for bam in os.listdir(pipeline_config['GATK']['inputBAM']):
			#changes directory to location of BAM files so within scope
			os.chdir(pipeline_config['GATK']['inputBAM'])
			mutect.run(
				Parameter('-T', 'MuTect2'),
				Parameter('-R', pipeline_config['GATK']['reference']),
				Parameter('-I:tumor', bam),
				Parameter('--artifact_detection_mode'),
				Parameter('--dbsnp', pipeline_config['GATK']['dbSNP']),
				Parameter('--cosmic', pipeline_config['GATK']['cosmic']),
				Parameter('-L', pipeline_config['GATK']['target_intervals']),
				Parameter('-vcf', str(pipeline_config['GATK']['output_VCF']) + '/' + str(bam[:-4]) + '_mutectv2_call_stats' + '.vcf'),
				Parameter('--coverage_file', str(bam[:-4]) + '.coverage.wig.txt')
				)

		#calcuates the total number of BAM files analyzed
		getListOfFiles=subprocess.Popen(("ls", "-A"), stdout=subprocess.PIPE)
		numOfFiles=subprocess.check_output(('wc', '-l'), stdin=getListOfFiles)
		output=numOfFiles.stdout.read()
		print "The total number of normal samples that will make up PON is " + str(output)
		
		#creates a list of parameters that are only called once
		single_parameter_calls=[Parameter('-T', 'CombineVariants'),
				Parameter('-R', pipeline_config['GATK']['reference']),
				Parameter(pipeline_args['minN']),
				Parameter('--filteredAreUncalled'),
				Parameter('--filteredrecordmergetype', 'KEEP_IF_ANY_UNFILTERED'),
				Parameter('-L', pipeline_config['GATK']['target_intervals']),
				Parameter(pipeline_args['o'])]
		#add x number of -V parameters, depending on the number of VCF files generated above
		repetative_parameter_vcf=[Parameter('-V', vcf) for vcf in os.listdir(pipeline_config['GATK']['output_VCF'])]
		#combineAllVariants.run() combines all VCF files for each BAM file analyzed above to generate
		#one PON file
		combineAllVariants.run(
				#concatenate list and unpack each paramter as an individual argument
				*(single_parameter_calls+repetative_parameter_vcf)
				)