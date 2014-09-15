import pickle
from fsa import *

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
#		User inquiries about morphology
#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#

#morphology_copy = morphology.MakeCopy()
#morphology.saveFSA()    #audrey  2014_09_06

print "Loading morphology FSA information from files ..."
forParseOnly  = True
splitEndState = True
morphology = FSA_lxa(splitEndState)
morphology.loadFSA(forParseOnly)


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
			print "state.index:  ", state.index   #audrey  2014_09_07  N.B. For this state (from preeding line), state.index != stateno
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
		#print "startingParseChunk.morph: ", startingParseChunk.morph
		startingParseChunk.toState = morphology.startState
		print "startingParseChunk.toState.index: ", startingParseChunk.toState.index

		initialParseChain.append(startingParseChunk)
		#print "initialParseChain: ", initialParseChain
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
