from bs4 import BeautifulSoup
import urllib2
import urllib
import string
from datetime import datetime, date, time

#
# Assign the senators to parties and groupings
#

# Members of each party
membersALP = [u'McEwen', u'Brown', u'Bullock', u'Gallacher', u'Moore', u'Gallagher', u'Singh', u'Cameron',u'O\u2019Neill', u'Ketter', u'Urquhart', u'Carr', u'Lines', u'Polley', u'Ludwig', u'Wong', u'Collins', u'Marshall', 'Bilyk', 'Conroy', 'Dastyari', 'Lundy', 'McLucas', 'Peris', 'Sterle']
membersLP = ['Birmingham', 'Abetz', u'Back', u'Edwards', u'Mason', u'Ronaldson', u'Bernardi', u'Fawcett', u'Ruston', u'Brandis', u'Fierravanti-Wells', u'Ryan', u'Fifield', u'Seselja', u'Bushby',  u'Johnston', u'Sinodinos', u'Canavan', u'Colbeck', u'Reynolds', 'Cash', 'Cormann', 'Heffernan', 'Parry', 'Payne', 'Smith']
membersNP = [u'McKenzie', u'Nash', u'Williams', 'Macdonald', u'O\u2019Sullivan']
membersCLP = [u'Scullion']
membersLNP = [u'McGrath']
membersGreens = ['Di Natalie', 'Rhiannon', 'Ludlam', 'Whish-Wilson', 'Waters', 'Siewert', 'Milne', 'Wright', 'Hanson-Young', 'Rice']
membersLDP = ['Leyonhjelm']
membersPUP = ['Wang']
membersNXT = ['Xenophon']
membersAMEP = ['Muir']
membersFFP = ['Day']
membersLaz = ['Lazarus']
membersLam = ['Lambie']
membersMad = ['Madigan']

# groupsList is what all of the operations iterate over. New groups must be added here.
# Group names as per Senate StatsNet
groupsList = {
              'Govt': set(membersLP + membersCLP + membersLNP + membersNP), 
              'Opp': set(membersALP), 
              'AG': set(membersGreens), 
              'FFP': set(membersFFP), 
              'PUP': set(membersPUP), 
              'LD': set(membersLDP), 
              'AMEP': set(membersAMEP), 
              'IndX': set(membersNXT), 
              'IndM': set(membersMad), 
              'IndL': set(membersLam)
              }

verbose = True

def verbosePrinter(text):
	if verbose:
		print '#DEBUG#:', text
		return
	else:
		return


def getParlInfoId(id):
	# Build the URL based on the System ID.
	baseUrl = 'http://parlinfo.aph.gov.au/parlInfo/search/display/display.w3p;query=Id%3A'
	url = urllib2.urlopen(baseUrl + urllib.quote('\"' + id + '\"'))
	content = url.read()
	soup = BeautifulSoup(content)
	return soup

def pageScraper(id):
	#
	# Get the Senate Journal page from ParlInfo with Beautiful Soup and parse for divisions
	#

	#url = urllib2.urlopen("http://parlinfo.aph.gov.au/parlInfo/search/display/display.w3p;query=Id%3A%22chamber%2Fjournals%2F091e576f-461d-48eb-81fc-15612e3b8693%2F0055%22")
	#url = urllib2.urlopen('http://parlinfo.aph.gov.au/parlInfo/search/display/display.w3p;query=Id%3A%22chamber%2Fjournals%2F8cf7f440-8fe3-4b53-8d97-cd79dcc54fcb%2F0056%22') # 9 Feb 2015

	soup = getParlInfoId(id)
	
	def isNumber(number):
		# The program dies if the metadata items are missing and you try to turn them into a number
		if number.isdigit():
			return int(number)
		else:
			return 'Missing'

	# Metadata from the box at the top of each ParlInfo page
	divisionDate = datetime.strptime(soup.select(".mdItem")[3].contents[0], '%d-%m-%Y') # Date of the sitting
	divisionBill = soup.select(".mdItem")[1].contents[0] # Bill name
	divisionHouse = soup.select(".mdItem")[4].contents[0] # House (ie., 'Senate')
	divisionParl = int(soup.select(".mdItem")[5].contents[0]) # Parliament Number
	divisionJoural = int(soup.select(".mdItem")[6].contents[0]) # Journal Number
	divisionPage = isNumber(soup.select(".mdItem")[7].contents[0]) # Page
	divisionParlInfoId = soup.select(".mdItem")[9].strong.contents[0] # ParlInfo ID

	# Find everything with a HTML clas of 'Division[Head|List]' and stick it in divisionData
	divisionData = soup.find_all(class_ = ["DivisionHead", "DivisionList"])

	divisionsNumberToday = 0 # This actually should be divisions this segment
#	divisionsTable = []
	divisionsMetaData ={}
	divisionsTable = {}

	#
	# Grab the division tables from ParlInfo and put them in an array
	#

	for each in divisionData:
		thisLine = each.contents[0].lstrip(' ')
		if "AYES" in thisLine:
			divisionsNumberToday = divisionsNumberToday + 1
			divisionAyesNumber = int(thisLine.split()[1])
			personVote = "AYE"
			divisionsMetaData = {'date': divisionDate, 'number': divisionsNumberToday, 'bill': divisionBill, 'journal': divisionJoural, 'page': divisionPage, 'parl': divisionParl, 'id': divisionParlInfoId, 'ayes': divisionAyesNumber}
			divisionsTable[divisionsNumberToday] = {}
			divisionsTable[divisionsNumberToday]['metadata'] = divisionsMetaData
			divisionsTable[divisionsNumberToday]['AYES'] = list()
			divisionsTable[divisionsNumberToday]['NOES'] = list()
		elif "NOES" in thisLine:
			divisionNoesNumber = int(thisLine.split()[1])
			personVote = "NO"
			divisionsMetaData['noes'] = divisionNoesNumber
		elif not "Senators" in thisLine:
			thisLine = thisLine.replace("\n", "")
			thisLine = thisLine.replace("(Teller)", "")
			# BeautifulSoup adds a Unicode non-breaking space for empty cells that needs to be removed.
			if not u'\xa0' in thisLine:
				if personVote == "AYE":
					divisionsTable[divisionsNumberToday]['AYES'].append(thisLine)
				elif personVote == "NO":
					divisionsTable[divisionsNumberToday]['NOES'].append(thisLine)

	#
	# Map the senators back to their groups and print out the group vote
	#

	for divNumber in divisionsTable.iterkeys():
		#print '\n', divisionsTable[divNumber]['metadata']['bill'], '- Division', divNumber, "on", divisionsTable[divNumber]['metadata']['date'], '(Ayes: ', divisionsTable[divNumber]['metadata']['ayes'], ', Noes: ', divisionsTable[divNumber]['metadata']['noes'], '):'
		groupVotes = {}
		for name, group in groupsList.iteritems():
			# These are testing if a group isn't in a vote -- might not be very robust. Consider fixing.
			if (group.isdisjoint(divisionsTable[divNumber]['NOES']) and group.isdisjoint(divisionsTable[divNumber]['AYES'])):
				groupVotes[name] = '-'
				#print name, "-"
			elif group.isdisjoint(divisionsTable[divNumber]['NOES']):
				groupVotes[name] = 'Yes'
				#print name, "Yes"
			elif group.isdisjoint(divisionsTable[divNumber]['AYES']):
				groupVotes[name] = 'No'
				#print name, "No"
			else:
				groupVotes[name] = 'Split'
			divisionsTable[divNumber]['Group'] = groupVotes
	
	return divisionsTable

def divisionSearch(dateStart, dateEnd):
	#
	# Dump out a list of all of the System IDs of the divisions (by a search for 'AYES' in content)
	# so they can be passed to the function to get the division results.
	#

	# Return resultsNumber results (200 max possible), sorted earliest first (mainly here for debugging)
	resultsNumber = 200
	
	# dateStart and dateEnd are in the format dd/mm/yyyy
	urlDates = urllib.quote(dateStart + " >> " + dateEnd)
	searchUrl = 'http://parlinfo.aph.gov.au/parlInfo/search/summary/summary.w3p;adv=yes;orderBy=date-eLast;page=0;query=Content%3AAYES%20Date%3A' + urlDates + '%20Dataset%3Ajournals,journalshistorical;resCount=' + str(resultsNumber)
	
	verbosePrinter('Searching for divisions from ' + dateStart + ' to ' + dateEnd)
	url = urllib2.urlopen(searchUrl)
	content = url.read()
	soup = BeautifulSoup(content)
	results = []

	# Total number of results returned in the query
	numResults = int(soup.select('.resultsSummary')[0].contents[1].split()[2])
	numPages = int(numResults/resultsNumber) + 1
	
	verbosePrinter('Found ' + str(numResults) + ' results on ' + str(numPages) + ' pages.')
	
	# The System ID is identified with the 'sumMeta' class in the file
	searchData = soup.find_all(class_ = 'sumMeta')
	
	for each in searchData:
		searchLine = each.contents[0].split()[7]
		#	for pageId in soup.select('.sumMeta')[50].contents[0].split()[7]:	
		results.append(searchLine)

	currentPage = 0
	
	while numPages > 1:
		verbosePrinter('Reading page ' + str(currentPage))
		# If there are more than resultsNumber results, we grab them from here.
		currentPage = currentPage + 1

		# The page number can be advanced by appending ';page=n' to the end of the URL
		url = urllib2.urlopen(searchUrl + ';page=' + str(currentPage))
		content = url.read()
		soup = BeautifulSoup(content)

		searchData = soup.find_all(class_ = 'sumMeta')
		
		for each in searchData:
			searchLine = each.contents[0].split()[7]
			results.append(searchLine)
		
		numPages = numPages - 1
	
	return results	

def resultsPrinter(startDate, endDate, printType):

	#
	# This function is just for testing - it gets each of the results and just prints them out.
	# printType 1 is a table. Anything else is a CSV display
	#

	results = divisionSearch(startDate, endDate)
	
	if printType == 1:
		
		# Print out a table
		print '\nResults:', len(results), 'divisions between', startDate, 'and', endDate, 'found.' 
		for each in results:
			outputData = pageScraper(each)
			for n in outputData.iterkeys():
				print '\n%s: %s (division %s)' % (outputData[n]['metadata']['date'].strftime('%d-%m-%Y'),  outputData[n]['metadata']['bill'], outputData[n]['metadata']['number'])
				for party in groupsList.iterkeys():
				#print '%s:\t%s' (party, outputData[n]['Group'][party])
					print party, ":", outputData[n]['Group'][party]

	elif printType == 2:
		
		# Just dump the raw data structures to screen
		for each in results:
			outputData = pageScraper(each)
			print outputData
			
	elif printType == 3:
		
		# Print CSV to screen 
		print 'number,date,bill,division,id,%s' % ','.join(groupsList.keys())
		lineNumber = 1
		for each in results:
			outputData = pageScraper(each)
			for n in outputData.iterkeys():
				outputLine = str(lineNumber) + ',' + outputData[n]['metadata']['date'].strftime('%d-%m-%Y') + ',' + outputData[n]['metadata']['bill'] + ',' + str(outputData[n]['metadata']['number']) + ',' + outputData[n]['metadata']['id']
				for party in groupsList.iterkeys():
					outputLine = outputLine + ',' + outputData[n]['Group'][party]
			lineNumber = lineNumber + 1
			print outputLine
			
	elif printType == 4:
		
		# Put all of the data into one big table
		allDivisions = []
		thisResult = []
		counter = 0
		for each in results:
			outputData = pageScraper(each)
			#print "."
			for n in outputData.iterkeys():
				thisResult = [outputData[n]['AYES'], outputData[n]['NOES'], outputData[n]['Group'], outputData[n]['metadata']]
				#print thisResult
				allDivisions.append(thisResult)
				counter = counter + 1
				print counter
				#divisionDate = outputData[n]['metadata']['date'].strftime('%Y-%m-%d')
				#allDivisionsKey = outputData[n]['metadata']['date'].strftime('%d-%m-%Y') + '-' + divisionCounter
				#outputLine = (outputData[n]['metadata']['date'].strftime('%d-%m-%Y') + ',' + outputData[n]['metadata']['bill'] + ',' + outputData[n]['metadata']['number'])
			#print outputData
		print "Done."
		return allDivisions

	elif printType == 5:
		
		# Save to a CSV file 
		f = open('divcount.csv','w')
		f.write('number,date,bill,division,id,%s\n' % ','.join(groupsList.keys()))
		lineNumber = 1
		for each in results:
			outputData = pageScraper(each)
			for n in outputData.iterkeys():
				outputLine = str(lineNumber) + ',' + outputData[n]['metadata']['date'].strftime('%d-%m-%Y') + ',\"' + outputData[n]['metadata']['bill'] + '\",' + str(outputData[n]['metadata']['number']) + ',' + outputData[n]['metadata']['id']
				for party in groupsList.iterkeys():
					outputLine = outputLine + ',' + outputData[n]['Group'][party]
				verbosePrinter(outputLine)
				outputLine = outputLine + '\n'
				lineNumber = lineNumber + 1
				f.write(outputLine.encode('utf8'))
		
		f.close()

	else:
		
		# Do nothing.	
		return
		
# 
# This works by finding ParlInfo System IDs. They look like: 
# 'chamber/journals/8cf7f440-8fe3-4b53-8d97-cd79dcc54fcb/0056'
# 

# 
# Still to do
# - [DONE!] Handle more than one page of results
# - Try and determine the type of division happening
# - Account for different party compositions at different times
# - Division number by day
# - Put a bit of error-detection in the page-loading function
# - The UTF8 Encoded dashes in bill names end up unreadable in Excel. Replace with
#   an actual ASCII dash.
# - When it crashes, tell us the ID of the segment it crashed on. 
#

# 
# Functions:
#
# pageScraper(Id)
# divisionSearch(startDate, endDate)
#

#result = resultsPrinter('10/03/2015', '20/03/2015', 5)
result = resultsPrinter('01/01/2014','31/12/2014', 5)
#result = resultsPrinter('12/11/2013','26/03/2015', 5) # The current parliament
#result = divisionSearch('01/01/2015', '30/04/2015')
#print result
