import os
from chunkypipes.components import *
import subprocess
import datetime
import re

class Pipeline(BasePipeline):

	def dependencies(self):
		return []
	def description(self):
		return 'Indel calls from tumor/normal pairs, single, or de novo indel of capture data'

	def configure(self):
		return{
			'scalpel_discovery':{
				'path':'Full path to scalpel discovery executable'
				},
			'scalpel_export':{
				'path':'Full path to scalpel export executable'
				},
			'ref_genome':{
				'path':'Full path to genome in fasta file, same one in which bams aligned'
				}
			}

	def add_pipeline_args(self, parser):
		parser.add_argument('-captureFile', required=True, help='Full path to capture panel location in BED format')
		parser.add_argument('-samplePairs', required=True, help='Full path to file with exact names of normal tumor BAM files Format: normal.bam,tumor.bam one pair per line OR name of .db files to analyze, one per line')
		parser.add_argument('-mode', required=True, help='discovery or export mode')
		parser.add_argument('-dirLoc', required=True, help='Full path to directory where all input is located')
		parser.add_argument('-outDir', required=True, help='Full path to output directory ending in /')
		parser.add_argument('--threads', default='1', help="[INT] number of procs/threads to use")
		parser.add_argument('--minVAFtumor', default='0.05', help='[FLOAT] minimum variant allele frequency from 0 - 1')
		parser.add_argument('--minCoverageT', default='4', help='[INT] minimum coverage of tumor sample')
		parser.add_argument('--minCoverageN', default='10', help='[INT] minimum coverage of normal sample')
	
	def run_pipeline(self, pipeline_args, pipeline_config):
		discovery=Software('scalpel_discovery', pipeline_config['scalpel_discovery']['path'])
		export=Software('scalpel_export', pipeline_config['scalpel_export']['path'])

		if pipeline_args['mode']=='discovery':
			with open(pipeline_args['samplePairs']) as bam_pairs:
				for line in bam_pairs:
					normal,tumor = line.rstrip('\n').split(',')
					# extract BID 
					bid = re.compile(r'(\d+-\d+)+')
					tumor_bid = re.search(bid, tumor).group(1)
					normal_bid = re.search(bid, normal).group(1)
					pathToOut = pipeline_args['outDir']+str(tumor_bid)+'_'+str(normal_bid)
					outDirectory = os.mkdir(pathToOut)
					discovery.run(
						Parameter('--somatic'),
						Parameter('--normal', pipeline_args['dirLoc']+normal),
						Parameter('--tumor', pipeline_args['dirLoc']+tumor),
						Parameter('--bed', pipeline_args['captureFile']),
						Parameter('--ref', pipeline_config['ref_genome']['path']),
						Parameter('--two-pass'),
						Parameter('--numprocs', pipeline_args['threads']),
						Parameter('--dir', str(pathToOut)),
						Parameter('--logs')
					)

		elif pipeline_args['mode']=='export':
			with open(pipeline_args['samplePairs']) as database_file:
				for line in database_file:
					filename = database_file.rstrip('\n')
					export.run(
						Parameter('--somatic'),
						Parameter('--db', pipeline_args['dirLoc']+filename),
						Parameter('--bed', pipeline_args['captureFile']),
						Parameter('--ref', pipeline_config['ref_genome']['path']),
						Parameter('--min-coverage-tumor', pipeline_args['minCoverageT']),
						Parameter('--min-coverage-normal', pipeline_args['minCoverageN']),
						Parameter('--min-vaf-tumor', pipeline_args['minVAFtumor'])
						)

		else:
			print "mode selected does not exist!"