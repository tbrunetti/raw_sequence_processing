library(edgeR)
library(locfit)
#name of all samples
Label<-c('input', 'veh1', 'veh2', 'veh3', 'veh4', 'dht1', 'dht2', 'dht3', 'dht4')
#genotype of all samples
Genotype<-c('LNCaP', 'LNCaP', 'LNCaP', 'LNCaP', 'LNCaP', 'LNCaP', 'LNCaP', 'LNCaP', 'LNCaP')
#treatments applied to each sample
Treatment<-c('none', 'veh', 'veh', 'veh', 'veh', 'dht', 'dht', 'dht', 'dht')
#puts everything into a dataframe
df<-data.frame(Label, Genotype, Treatment)


#extracts name of regions
names<-new.edgeR.norms$region.ID
#assignes region name to rows
row.names(new.edgeR.norms)<-names
#removes region name column from matrix
new.edgeR.norms<-new.edgeR.norms[-1]

#make a DGEList for sample count comparisons and labe appropriately, automatically will calculate "$sample" dataset
regionCounts<-DGEList(counts=new.edgeR.norms, group=df$Genotype)
colnames(regionCounts)<-df$Label
#outputs the dimesions of DGEList, should be the number of regions x number of samples
dim(regionCounts)

#--------------------------------read filtering and normalization--------------------------------------
#calculates the counts per million in each sample of regionCounts DGEList object
CPM<-cpm(regionCounts)
#only keep a region where CPM is greater than one and is in at least two samples (CPM >1 means at least 5-7 reads in the sample)
keep<-rowSums(CPM>1)>=2
regionCounts<-regionCounts[keep, ]
#outputs number of regions remaining x number of samples after filtering
dim(regionCounts)
head(regionCounts$counts)

#normalize
regionCounts<-calcNormFactors(regionCounts)
#outputs the normalization factors for each library and total library size for each sample and group
regionCounts$samples

#creation of design matrix to represent experimental design across samples
fac<-paste(df$Genotype, df$Treatment, sep=".")
fac<-factor(fac)
design<-model.matrix(~0+fac)
design

#estimating dispersion using weighted likelood empirical Bayes
#calculates common.dispersion, trended.dispersion, trend.method, AveLogCPM, span, tagwise.disperion, prior.df, prior.n
regionCounts<-estimateDisp(regionCounts, design)

#Biological coefficient of variation (BCV) is the square root of dispersion
#I believe high BCV corresponds to higher dispersion
#BCV plot to shows regionwise/genewise, common, and trended dispersions as a funciton of average logCPM
plotBCV(regionCounts)

#find diffentially expressed regions using a negative binomial general linear model using gene/region specific dispersions estimated from above
fit<-glmFit(regionCounts, design)
#calculate log-likelihood ratio statistics for comparisons of interest 
#contrast specifies which groups to compare, from design matrix, here group 2 and 3 means expGroup3-expGroup2=0

#vehicle-input
logRatioStats<-glmLRT(fit, contrast=c(0, -1, 1))

#dht-vehicle
logRatioStats<-glmLRT(fit, contrast=c(1, 0, -1))


#get results for the most significant genes/regions
topTags(logRatioStats)
#to get even more specific results: n=# of samples, sum is total genes/regions that have FDR lower than 0.01
tp<-topTags(logRatioStats, n=Inf)
sum(tp$table$FDR<0.1)

