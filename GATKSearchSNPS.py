#! /usr/bin/env python
# -*- coding:Utf-8 -*-
#Author: Pier-Luc Plante
#License:GPLV3
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You have received a copy of the GNU General Public License
along with this program (gpl-3.0.txt).
see <http://www.gnu.org/licenses/>

"""

"""
This script is created to be part of SNPs detection pipeline.
It will call low frequecies variant based on a minimum % of variant.
python GATKSearchSNPS.py Reference.fasta GATK.out 
"""

import sys
from time import localtime, strftime

#Minimum value of coverage to pass from uncertain to Observed or Variant
cut_Off_Uncertainty=5
#The minimum percentage of variant in the population at a given position
variantCall=1
#Class created to be part of the dictionnary. Only an assembly of int, str and char.
class LineOfTab(object):
	position=0		
	numA=0
	numT=0
	numG=0
	numC=0
	total=0
	ref=''
	now=''
	type=""




if len(sys.argv)==0:
	print(__doc__)
	sys.exit(1)

################################################################################
### first step: calculate lenght of ref to create a dict of the good lenght. ###
################################################################################


#print("START TO IMPORT REF SEQ")	#for debogue
longOfSeq=0
seqRef=""
for lines in open(sys.argv[1]):
	if lines[0]!='>':
		longOfSeq=len(lines)-1+longOfSeq
		seqRef=seqRef+lines[0:len(lines)-1]
i=0
tabDict={}
while i<longOfSeq:
	tabDict[i]=LineOfTab()
	tabDict[i].position=i+1
	tabDict[i].ref=seqRef[i]
	i+=1

seqRef=""		#"free" seqRef memory? does it really work?

#print("Ref sequence is now in memory!")	#for debogue
################################################################################
#### Second step: Read the input from GATK file and put it in the dictionnary ###
################################################################################

gatk=open(sys.argv[2],'r');
line=gatk.readline();
if line.split()[0]!="Locus":
        print("Check GATK file");
        sys.exit(1);
while (1):
        line=gatk.readline();
        if line=="":
                break;
        else:
                position=int(line.split()[0].split(':')[1])-1;
                total=line.split()[1];
                a=int(line.split()[4].split(':')[1]);
                c=int(line.split()[5].split(':')[1]);
                t=int(line.split()[7].split(':')[1]);
                g=int(line.split()[6].split(':')[1]);
                tabDict[position].numA=a;
                tabDict[position].numC=c;
                tabDict[position].numT=t;
                tabDict[position].numG=g;
                tabDict[position].total=total;


#################################################
# start of the dict completion (type and total) #
#################################################
i=0
#print("start of the dict completion")	#for debogue
while i < len(tabDict):
	tabDict[i].total=tabDict[i].numA+tabDict[i].numG+tabDict[i].numC+tabDict[i].numT
	#fill the now attribut
	if tabDict[i].total==0:
		tabDict[i].now=tabDict[i].ref
	elif (tabDict[i].numA>tabDict[i].numT and tabDict[i].numA>tabDict[i].numG and 
	tabDict[i].numA>tabDict[i].numC and tabDict[i].total!=0):
		tabDict[i].now='A'
	elif (tabDict[i].numT>tabDict[i].numA and tabDict[i].numT>tabDict[i].numG and 
	tabDict[i].numT>tabDict[i].numC and tabDict[i].total!=0):
		tabDict[i].now='T'
	elif (tabDict[i].numC>tabDict[i].numT and tabDict[i].numC>tabDict[i].numG and 
	tabDict[i].numC>tabDict[i].numA and tabDict[i].total!=0):
		tabDict[i].now='C'
	elif (tabDict[i].numG>tabDict[i].numT and tabDict[i].numG>tabDict[i].numA and
	tabDict[i].numG>tabDict[i].numC and tabDict[i].total!=0):
		tabDict[i].now='G'
	else:
		tabDict[i].now='N'
	#fill the type attribut
	if tabDict[i].total==0:
		tabDict[i].type="Reference"
	elif tabDict[i].total < cut_Off_Uncertainty and tabDict[i].ref==tabDict[i].now:
		tabDict[i].type="Reference low coverage"
	elif tabDict[i].total < cut_Off_Uncertainty and tabDict[i].ref!=tabDict[i].now:
		tabDict[i].type="Variant low coverage"
	elif tabDict[i].total >= cut_Off_Uncertainty and tabDict[i].ref==tabDict[i].now:
		tabDict[i].type="Observed"
	elif tabDict[i].total >= cut_Off_Uncertainty and tabDict[i].ref!=tabDict[i].now:
		tabDict[i].type="Variant"
	else:
		tabDict[i].type="Erreur"
	i+=1
	#print("position"+str(i-1)+" is completed in the dict")	#for debogue

##############################
# end of the dict completion #
##############################

#################
# print results##
#################

i=0
print("Pos\tA\tT\tC\tG\tTotal\tReference\tNow\tType")
#variantCall=int(sys.argv[2]);
##variantCall=2.5
#For each position, we determine if the line is a low frequency variant.
while i<len(tabDict):
	actg=[tabDict[i].numA, tabDict[i].numT, tabDict[i].numC, tabDict[i].numG];
	actg.sort();
	numberOfMinimumVariant=(tabDict[i].total*variantCall)/100;
	if(actg[2]>numberOfMinimumVariant and tabDict[i].total>100):
		print(str(tabDict[i].position)+"\t"+str(tabDict[i].numA)+"\t"+str(tabDict[i].numT)+
		"\t"+str(tabDict[i].numC)+"\t"+str(tabDict[i].numG)+"\t"+str(tabDict[i].total)+
		"\t"+str(tabDict[i].ref)+"\t"+str(tabDict[i].now)+"\t"+str(tabDict[i].type))
	i+=1


