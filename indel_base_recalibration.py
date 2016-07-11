import os
from chunkypipes.components import *
import subprocess

class Pipeline(BasePipeline):

	def dependencies(self):
		return [];

	def description(self):
		return 'Indel realignment and base recalibration of individual BAM samples'

	def configure(self):
		return{
			'GATK':{
				'path': 'Full path to GATK jar file',
				'reference': 'Full path to single file FASTA, karyotypically sorted genome'
			}
		}

	def add_pipeline_args(self, parser):
		parser.add_argument('-inputDirectory', required=True, help='Full path to directory of BAM samples to analyze')
		parser.add_argument('-outputDirectory', required=True, help='Full path to final directory to store all results')
		parser.add_argument('--knownIndels', help='Full path to a VCF file with known indels i.e. 1000 genomes, dbSNP')
		parser.add_argument('--LODthresh', default=5.0, help='[FLOAT] min log odds ratio that will be consider for data cleaning/realigning')

	def run_pipeline(self, pipeline_args, pipeline_config):
		initiateGATK=Software('GATK', pipeline_config['GATK']['path'])
		
		#will find all targets that need indel realignment in a given bam file
		for bam in os.listdir(pipeline_args['inputDirectory']):
			if bam[-4:]=='.bam':
				print "Generating realignment targets for "+str(bam)
				initiateGATK.run(
					Parameter('-T', 'RealignerTargetCreator'),
					Parameter('-R', pipeline_config['GATK']['reference']),
					Parameter('-I', pipeline_args['inputDirectory']+bam),
					Parameter('-o', pipeline_args['outputDirectory']+str(bam[:-4])+'_forIndelRealigner.intervals'),
					Parameter('--known', pipeline_args['knownIndels']) if pipeline_args['knownIndels'] else Parameter()
					)

		#will realign indel regions on bam file; requires output from above, but can't be piped
		for bam in os.listdir(pipeline_args['inputDirectory']):
			if bam[-4:]=='.bam':
				print "Realigning  "+str(bam)
				initiateGATK.run(
					Parameter('-T', 'IndelRealigner'),
					Parameter('-R', pipeline_config['GATK']['reference']),
					Parameter('-I', pipeline_args['inputDirectory']+bam),
					Parameter('-targetIntervals', pipeline_config['GATK']['outputDirectory']+bam[:-4]+'_forIndelRealigner.intervals'),
					Parameter('-o', pipeline_args['outputDirectory']+bam[:-4]+'.indel.realigned.bam'),
					Parameter('-LOD', pipeline_args['LODthresh']),
					Parameter('-known', pipeline_args['knownIndels']) if pipeline_args['knownIndels'] else Parameter()
					)

		#recalculate base quality scores
		for realignIndelBam in os.listdir(pipeline_args['outputDirectory']):
			if realignIndelBam[-20:]=='.indel.realigned.bam':
				print "Recalculating base quality scores for "+str(realignIndelBam)
				initiateGATK.run(
					Parameter('-T', 'BaseRecalibrator'),
					Parameter('-R', pipeline_config['reference']),
					Parameter('-I', pipeline_args['outputDirectory']+realignIndelBam),
					Parameter('-knownSites', pipeline_args['knownIndels']),
					Parameter('-o', pipeline_args['outputDirectory']+realignIndelBam[:-4]+'.recal_BQSR_data.table')
					)

		#apply new quality scores to bam files
		for calibratedBam in os.listdir(pipeline_args['outputDirectory']):
			if calibratedBam[-20:]=='.indel.realigned.bam':
				print "Applying new base quality scores to "+str(calibratedBam)
				initiateGATK.run(
					Parameter('-T', 'PrintReads'),
					Parameter('-R', pipeline_config['GATK']['reference']),
					Parameter('-I', pipeline_args['outputDirectory']+calibratedBam),
					Parameter('-BQSR', pipeline_args['outputDirectory']+calibratedBam[:-4]+'.recal_BQSR_data.table'),
					Parameter('-o', pipeline_args['outputDirectory']+calibratedBam[0:9]+'.realigned.recalibrated.bam')
					)





