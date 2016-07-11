# raw_sequence_processing

The scripts and programs listed in this repository are to designed to used on raw data sequencing or partially processed data (SAMs, BAMs).  Most of the functionality of the programs listed aid in data filtering and cleaning.



##indel_base_recalibration.py
-----------------------------
This mini pipeline will read in BAM files and perform indel realignment and base quality recalibration on individual samples.  


####Software Requirements
-------------------------
* chunkypipes (http://chunky-pipes.readthedocs.io/en/stable/getting_started.html)
* GATK suite (https://www.broadinstitute.org/gatk/)


####User Generated File Requirements
------------------------------------
* reference genome in a karyotypically sorted into a single FASTA file, as well as corresponding dictionary and .fai file located in the same directory
* directory of sorted and indexed BAM files to be analyzed


####Installation and Configuration
----------------------------------
Assuming chunkypipes has been installed correctly, download indel_base_recalibration.py and run the following:

```
chunky install indel_base_recalibration.py
chunky configure indel_base_recalibration.py
```
Type in the paths to the prompts that are asked.  The commands listed above only need to be performed once, unless the designated paths or code has changed, in which case, it  needs to be re-installed and re-configured.

####Running indel_base_recalibration.py
---------------------------------------
There are a few options the user can designate upon running, however, to run the minimal most basic form, run the following:
```
chunky run indel_base_recalibration.py -inputDirectory </path/to/input/BAMS/> -outputDirectory </path/to/results/output/>
```

It is strongly advised to add the -knownIndels option, however, to get the most accurate realignment and calibration.  The known indels file must be a VCF.  Most users can download the appropriate genome VCF of known snps from dbSNP or the 1000 genomes project.
```
chunky run indel_base_recalibration.py -inputDirectory </path/to/input/BAMS/> -outputDirectory </path/to/results/output/> -knownIndels </path/to/dbSNP/1000genome/knownSNPs.vcf>
```
