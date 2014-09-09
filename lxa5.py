# -*- coding: <utf-16> -*- 
unicode = True
import codecs



 
# This program looks for extended signatures, which are regular subgraphs among words, where the edges are
# (high-freq) Delta-Right pairs of words, and where a word may be *split differently* (without penalty!) 
# in different Delta-Right pairs: e.g., "moves" is part of the pair (move/move-s) and also of the pair
# (mov-es/mov-ing).
# 	Prototyping for bootstrapping of Lxa5
# 	Accepts name of input file as command-line argument.
#--------------------------------------------------------------------##
#		Main program begins on line 174
#--------------------------------------------------------------------##

import time
import datetime
import operator
import sys
import os
import codecs # for utf8
import string
import copy
from collections import defaultdict
from lxa_module import *

#--------------------------------------------------------------------##
#		user modified variables
#--------------------------------------------------------------------##
NumberOfCorrections = 100
g_encoding =  "asci"  # "utf8"
 

short_filename 		= "browncorpus"
out_short_filename 	= "browncorpus"
language		= "english"

datafolder    		= "../../data/"        # '../data/'     #"../../data/" 
ngramfolder   		= datafolder + language + "/ngrams/"
outfolder     		= datafolder + language + "/lxa/"
infolder 		= datafolder + language + '/dx1_files/'	

infilename 			= infolder  + short_filename     + ".dx1"
stemfilename 			= infolder  + short_filename     + "_stems.txt"
outfile_Signatures_name 	= outfolder + out_short_filename + "_Signatures.txt"  
outfile_SigTransforms_name 	= outfolder + out_short_filename + "_SigTransforms.txt"
outfile_FSA_name		= outfolder + out_short_filename + "_FSA.txt"
outfile_FSA_graphics_name	= outfolder + out_short_filename + "_FSA_graphics.png"
outfile_log_name 		= outfolder + out_short_filename + "_log.txt"

#outfileSigTransformsname = decorateFilenameWithIteration( SigTransforms_filename, outfolder, ".txt")
#partial_filename = language + "_"+  out_short_filename + "_extendedsigs"
#outfilename = decorateFilenameWithIteration (partial_filename, outfolder, ".txt")

if g_encoding == "utf8":
	Signatures_outfile = codecs.open(outfile_Signatures_name,    encoding =  "utf-8", mode = 'w',)
	SigTransforms_outfile = codecs.open(outfile_SigTransforms_name, encoding =  "utf-8", mode = 'w',)
	print "yes utf8"
else:
	#outfile = open(outfilename,mode='w') 
	Signatures_outfile = open (outfile_Signatures_name, mode = 'w')
	SigTransforms_outfile = codecs.open(outfile_SigTransforms_name, encoding =  "utf-8", mode = 'w',)
	FSA_outfile = open (outfile_FSA_name, mode = 'w')

#outfile = open (outfilename,"w")

log_file = open(outfile_log_name, "w")


if len(sys.argv) > 1:
	print sys.argv[1]
	infilename = sys.argv[1] 
if not os.path.isfile(infilename):
	print "Warning: ", infilename, " does not exist."
if g_encoding == "utf8":
	infile = codecs.open(infilename, g_encoding = 'utf-8')
else:
	infile = open(infilename) 


#----------------------------------------------------------#
 

  
MinimumStemLength 	= 5
MaximumAffixLength 	= 3
MinimumNumberofSigUses 	= 10

print >>log_file, "Language: ", language
print >>log_file, "Minimum Stem Length", MinimumStemLength, "\nMaximum Affix Length", MaximumAffixLength, "\n Minimum Number of Signature uses: ", MinimumNumberofSigUses
print >>log_file, "Date:", 

	# This is just part of documentation:
	# Signatures is a map: its keys are signatures.  Its values are *sets* of stems. 
	# StemToWord is a map; its keys are stems.       Its values are *sets* of words.
	# StemToSig  is a map; its keys are stems.       Its values are individual signatures.
	# WordToSig  is a Map. its keys are words.       Its values are *lists* of signatures.
	# StemCounts is a map. Its keys are words. 	 Its values are corpus counts of stems.

suffix_languages = ["english", "french", "hungarian", "turkish", "test"]
prefix_languages = ["swahili"]

if language in suffix_languages:
	side = "suffixal"
	FindSuffixesFlag = True

if language in prefix_languages:
	side = "prefixal"
	FindSuffixesFlag = False

#--------------------------------------------------------------------##
#		read wordlist (dx1)
#--------------------------------------------------------------------##

filelines= infile.readlines()
WordCounts={}
 
for line in filelines:
	pieces = line.split(' ')	 
	word=pieces[0] 	
	if word == '#':
		continue
	word = word.lower()		 
	if (len(pieces)>1):
		WordCounts[word] = int( pieces[1] )
	else:
		WordCounts[word]=1


wordlist = WordCounts.keys()
wordlist.sort()

#-------------------------------------------------------------------------------------------------------# 
#-------------------------------------------------------------------------------------------------------#
# 					Main part of program		   			   	#
#-------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------#

SigToTuple		= {}		# key: bisig     value: ( stem, word1, word2, bisig )
Signatures 		= {}
WordToSig		= {}
StemToWord 		= {}
StemCounts		= {}
StemToSig 		= {}
numberofwords 	= len(wordlist)
 
#--------------------------------------------------#
# 		Read files			   #
#--------------------------------------------------#  

StemFileExistsFlag	= False
if os.path.isfile(stemfilename):
	print "stem file is named: ", stemfilename
	print "stem file found"
	StemFileExistsFlag = True
	stemfile=open(stemfilename)
	filelines = stemfile.readlines()
	for line in filelines:		
		pieces=line.split()
		stem = pieces[0]			 
		StemCounts[stem] = 1 #  pieces[1]	
		StemToWord[stem] = set()
		for i in range (2, len(pieces)):
			word = pieces[i]
			#if not FindSuffixesFlag:
			#	word = word[::-1]
			StemToWord[stem].add(word)		
else:
	print "stem file not found"
	SigToTuple = MakeBiSignatures(wordlist, SigToTuple, FindSuffixesFlag)
	for sig in SigToTuple.keys():
		if len( SigToTuple[sig] ) < MinimumNumberofSigUses:		 
			del SigToTuple[sig]
		else:		 
			for stem, word1, word2, bisigstring in SigToTuple[sig]:				
				if not stem in StemToWord:
					StemToWord[stem] = set()
				StemToWord[stem].add(word1)
				StemToWord[stem].add(word2)		 
	print "Completed filtering out pairs used only a few times."

for stem in StemToWord:
	StemCounts[stem] = 0
	for word in StemToWord[stem]:
		StemCounts[stem]+= WordCounts[word]

if (not StemFileExistsFlag): # we use this to create a one-time list of stems with their words
	if g_encoding == "utf8":
		stems_outfile = codecs.open(stemfilename,encoding="utf-8",mode="w")
	else:
		stems_outfile= open (stemfilename,"w")

	for stem in StemToWord.keys():			 
		print >>stems_outfile, stem,	StemCounts[stem],	 
		for word in StemToWord[stem]:
			print >>stems_outfile, word,
		print >>stems_outfile

#-----------------------------------------------------------------------------------------------------------------#	
#	1. Make signatures, and WordToSig dictionary, and Signature dictionary-of-stem-lists, and StemToSig dictionary
#-----------------------------------------------------------------------------------------------------------------#	
print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
print "1.                Make signatures 1" 
print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#---------------------------------------------------------------------------------#	
#	1a. Declare a linguistica-style FSA
#---------------------------------------------------------------------------------#

splitEndState = True
morphology= FSA_lxa(splitEndState)
#print "Value of morphology.splitEndState :", morphology.splitEndState

#---------------------------------------------------------------------------------#	
#	1b. Find signatures, and put them in the FSA also.
#---------------------------------------------------------------------------------# 

StemToWord, Signatures, WordToSig, StemToSig =  MakeSignatures_1(StemToWord, StemToSig, FindSuffixesFlag, morphology, Signatures_outfile, ) 

# Investigation showed that "End" was the only accepting state
indicesToCheck = set()
indicesToCheck = {1, 2, 3, 4, 20, 21, 30}
for state in morphology.States:
	if state.index in indicesToCheck:
		print "state", state.index, "\tacceptingStateFlag: ", state.acceptingStateFlag
		
		#NOTE. At this point (i.e, directly after MakeSignatures_1)  States[k].index == k,  
		#      but not further on (after merges)
print
	
#---------------------------------------------------------------------------------#	
#	1c. Print the FSA to file.
#---------------------------------------------------------------------------------#  

print "line 220", outfile_FSA_name

morphology.printFSA(FSA_outfile) 

 
#-------------- Added Sept 24 for Jackson's program -----------------------------#
if True:
	printSignatures(Signatures, WordToSig, StemCounts, Signatures_outfile, g_encoding, FindSuffixesFlag)

 
#-------------------------------------------------------------------------------------------------------------------------------------#	
# 5. Look to see which signatures could be improved, and score the improvement quantitatively with robustness.
# Then we improve the one whose robustness increase is the greatest.
#-------------------------------------------------------------------------------------------------------------------------------------#	

print >>Signatures_outfile, "***"
print >>Signatures_outfile, "*** 5. Finding robust suffixes in stem sets\n\n"


#---------------------------------------------------------------------------------#	
#	5a. Find morphemes within edges: how many times? NumberOfCorrections
#---------------------------------------------------------------------------------# 

for loopno in range( NumberOfCorrections):
	#-------------------------------------------------------------------------#	
	#	5b. For each edge, find best peripheral piece that might be 
	#           a separate morpheme.
	#-------------------------------------------------------------------------# 	
	morphology.find_highest_weight_affix_in_an_edge ( Signatures_outfile, FindSuffixesFlag)

#---------------------------------------------------------------------------------#	
#	5c. Print graphics based on each state.
#---------------------------------------------------------------------------------# 
if True:
	for state in morphology.States:	
		graph = morphology.createPySubgraph(state) 	
	 	if len(graph.edges()) < 4:
	 		continue
		graph.layout(prog='dot')
		filename = outfolder + 'morphology' + str(state.index) + '.png'
		graph.draw(filename) 
		filename = outfolder + 'morphology' + str(state.index) + '.dot'
		graph.write(filename)
	 
 	
#---------------------------------------------------------------------------------#	
#	5d. Print FSA again, with these changes.
#---------------------------------------------------------------------------------# 

if True:
	morphology.printFSA(FSA_outfile)
 
#------------------------------------------------------------------------------------------#
class parseChunk:
	def __init__(self, morph, rString, edge= None):
		self.morph 		= morph
		self.edge 		= edge
		self.remainingString 	= rString
		if (edge):
			self.fromState = self.edge.fromState
			self.toState   = self.edge.toState
		else:
			self.fromState = None
			self.toState = None
	def Copy (self, otherChunk):
		self.morph 		= otherChunk.morph
		self.edge 		= otherChunk.edge
		self.remainingString 	= otherChunk.remainingString
 
 



 
#------------------------------------------------------------------------------------------#
localtime1 = time.asctime( time.localtime(time.time()) )
print "Local current time :", localtime1

morphology.dictOfLists_parses = morphology.parseWords(wordlist)

localtime2 = time.asctime( time.localtime(time.time()) )
#print "Time to parse all words: ", localtime2 - localtime1  #subtraction doesn't work for strings!
print "Local time after parse :", localtime2


#------------------------------------------------------------------------------------------#

 
print >>FSA_outfile, "Finding common stems across edges."
HowManyTimesToCollapseEdges = 9
for loop in range(HowManyTimesToCollapseEdges): 
 	print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	print  "Loop number", loop
 	print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	(commonEdgePairs,  EdgeToEdgeCommonMorphs) = morphology.findCommonStems()
 
	if len( commonEdgePairs ) == 0:
		print "There are no more pairs of edges to consider."
		break
	edge1, edge2 = commonEdgePairs[0]
	state1 = edge1.fromState
	state2 = edge2.fromState
	state3 = edge1.toState
	state4 = edge2.toState
	print "\n\nWe are considering merging edge ", edge1.index,"(", edge1.fromState.index, "->", edge1.toState.index, ") and  edge", edge2.index, "(", edge2.fromState.index, "->", edge2.toState.index , ")"
	 
	print "Printed graph", str(loop), "before_merger"
	graph = morphology.createDoublePySubgraph(state1,state2) 	
	graph.layout(prog='dot')
	filename = outfolder + out_short_filename + str(loop) + '_before_merger' + str(state1.index) + "-" + str(state2.index) + '.png'
	graph.draw(filename) 

	if state1 == state2:
		print "The from-States are identical"
		state_changed_1 = state1
		state_changed_2 = state2
		morphology.mergeTwoStatesCommonMother(state3,state4)
		morphology.EdgePairsToIgnore.append((edge1, edge2))

	elif state3 == state4:
		print "The to-States are identical"
		state_changed_1 = state3
		state_changed_2 = state4	 
		morphology.mergeTwoStatesCommonDaughter(state1,state2) 
		morphology.EdgePairsToIgnore.append((edge1, edge2))

	elif morphology.mergeTwoStatesCommonMother(state1,state2):
		print "Now we have merged two sister edges from line 374 **********"
		state_changed_1 = state1
		state_changed_2 = state2
		morphology.EdgePairsToIgnore.append(edge1, edge2)

	
	elif   morphology.mergeTwoStatesCommonDaughter((state3,state4))  : 
		print "Now we have merged two daughter edges from line 377 **********"
		state_changed_1 = state3
		state_changed_2 = state4
		morphology.EdgePairsToIgnore.append((edge1, edge2))
		 
	graph = morphology.createPySubgraph(state1) 	
	graph.layout(prog='dot')
	filename = infolder + str(loop) +  '_after_merger_' + str(state_changed_1.index) +  "-" + str(state_changed_2.index) + '.png'
	print "Printed graph", str(loop), "after_merger"
	graph.draw(outfile_FSA_graphics_name) 
 

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
#		User inquiries about morphology
#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#

morphology_copy = morphology.MakeCopy()
print
print "Saving morphology FSA information to files for standalone access..."
morphology.saveFSA()    #audrey  2014_09_06

initialParseChain = list()
CompletedParses = list()
IncompleteParses = list()
word = "" 
while True:
	print
	word = raw_input('Inquiry about a word: ')
	if word == "exit":
		break
	elif word == "State":
		while True:
			stateidx = raw_input("State index:")
			if stateidx == "" or stateidx == "exit":
				break
			stateidx = int(stateidx)	
			for state in morphology.States:      
				if state.index == stateidx:  
					break	
			#####state = morphology.States[stateidx]   
			for edge in state.getOutgoingEdges():
				print "   Edge index", edge.index 
				i = 0
				for morph in edge.labels:
					print "%12s" % morph,
					i+=1
					if i%6 == 0: print
					elif i==len(edge.labels): print
			print "\n\n"		
			continue
		
		if False:     # THIS SECTION REPLACED BY ABOVE  audrey  2014_09_07    state.index (not stateno) matches the graph
			stateno = raw_input("State number:")
			if stateno == "" or stateno == "exit":
				break
			stateno = int(stateno)	
			for state in morphology.States:
				if state.index == stateno:
					break	
			state = morphology.States[stateno]   
			print "state.index:  ", state.index   #audrey  2014_09_07  N.B. For this state (from preceding line), state.index != stateno
			for edge in state.getOutgoingEdges():
				print "Edge number", edge.index 
				i = 0
				for morph in edge.labels:
					print "%12s" % morph,
					i+=1
					if i%6 == 0: print 
			print "\n\n"		
			continue
			
	elif word == "Edge":
		while True:
			edgeidx = raw_input("Edge index:")
			if edgeidx == "" or edgeidx == "exit":
				break
			edgeidx = int(edgeidx)
			for edge in morphology.Edges:
				if edge.index == edgeidx:
					break
			#print "From state", morphology.Edges[edgeidx].fromState.index, "To state", morphology.Edges[edgeidx].toState.index
			print "   From state", edge.fromState.index, "To state", edge.toState.index
			i=0
			for morph in edge.labels:
				print "%12s" % morph,
				i+=1
				if i%6 == 0: print
				elif i==len(edge.labels): print				
			print "\n\n"
			continue
		
		if False:     # THIS SECTION REPLACED BY ABOVE  audrey  2014_09_07    edge.index (not edgeno) matches the graph
			edgeno = raw_input("Edge number:")
			if edgeno == "" or edgeno == "exit":
				break
			edgeno = int(edgeno)
			for edge in morphology.Edges:
				if edge.index == edgeno:
					print "edge.index; ", edge.index
					break
			print "From state", morphology.Edges[edgeno].fromState.index, "To state", morphology.Edges[edgeno].toState.index
			for edge in morphology.Edges:
				if edge.index == int(edgeno):
					morphlist = list(edge.labels)
			for i in range(len( morphlist )):
				print "%12s" % morphlist[i],
				if i%6 == 0:
					print	
			print "\n\n"
			continue
			
	elif word == "graph":
		while True:
			stateno = raw_input("Graph state number:")
			
	else:
		del CompletedParses[:]
		del IncompleteParses[:]
		del initialParseChain[:]
		startingParseChunk = parseChunk("", word)
		print "startingParseChunk.morph: ", startingParseChunk.morph
		startingParseChunk.toState = morphology.startState
		print "startingParseChunk.toState.index: ", startingParseChunk.toState.index

		initialParseChain.append(startingParseChunk)
		print "initialParseChain: ", initialParseChain
		IncompleteParses.append(initialParseChain)
		print "IncompleteParses: ", IncompleteParses
		while len(IncompleteParses) > 0 :
			print
			print "length of IncompleteParses: ", len(IncompleteParses)
			#CompletedParses, IncompleteParses = morphology.lparse(CompletedParses, IncompleteParses)
			CompletedParses, IncompleteParses = morphology.lparseForTracking(CompletedParses, IncompleteParses)
		if len(CompletedParses) == 0: print "no analysis found." 
		else: print
	 
		for parseChain in CompletedParses:
			for thisParseChunk in  parseChain:			
				if (thisParseChunk.edge):				 
					print "\t",thisParseChunk.morph,  
			print 
		print

		for parseChain in CompletedParses:
			print "\tStates: ",
			for thisParseChunk in  parseChain:			
				if (thisParseChunk.edge):				 
					print "\t",thisParseChunk.fromState.index, 
			print "\t",thisParseChunk.toState.index 	 
		print 

		for parseChain in CompletedParses:
			print "\tEdges: ",
			for thisParseChunk in  parseChain:			
				if (thisParseChunk.edge):				 
					print "\t",thisParseChunk.edge.index,
			print
		print "\n\n"



#---------------------------------------------------------------------------------------------------------------------------#
# We create a list of words, each word with its signature transform (so DOGS is turned into NULL.s_s, for example)

if True:
	printWordsToSigTransforms(Signatures, WordToSig, StemCounts, SigTransforms_outfile, g_encoding, FindSuffixesFlag)
 

#---------------------------------------------------------------------------------------------------------------------------#  
#---------------------------------------------------------------------------------#	
#	Close output files
#---------------------------------------------------------------------------------# 
  
FSA_outfile.close()
Signatures_outfile.close() 
SigTransforms_outfile.close() 

#---------------------------------------------------------------------------------#	
#	Logging information
#---------------------------------------------------------------------------------# 

localtime = time.asctime( time.localtime(time.time()) )
print "Local current time :", localtime

numberofwords = len(wordlist)
logfilename = outfolder + "logfile.txt"
logfile = open (logfilename,"a")

print >>logfile,  outfile_Signatures_name.ljust(60), '%30s wordcount: %8d data source:' %(localtime, numberofwords ), infilename.ljust(50) 

#--------------------------------------------------#

