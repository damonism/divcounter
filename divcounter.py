#-*- coding: utf-8 -*-

import urllib2
import urllib
import re
import json
#import string
from datetime import datetime
from bs4 import BeautifulSoup

verbose = True
baseUrl = 'http://parlinfo.aph.gov.au/parlInfo/search/display/display.w3p;query=Id%3A'

def verbosePrinter(text):
	"""Set verbose = True or False to turn the dubugging text on or off."""
	
	if verbose:
		print '#DEBUG#:', text
		return
	else:
		return

def senators_in_groups_by_date(date_of_division):
	
	parliament44_start = datetime(2013, 11, 12)
	parliament44_end = datetime(2016, 12, 30)
	
	# 44th Parliament
	if date_of_division > parliament44_start and date_of_division < parliament44_end:
		
		# Default list of senators in the 44th Parliament
		dict_senators_in_groups = {
				'Govt': set(
				            ['Birmingham', 'Abetz', u'Back', u'Edwards', u'Mason', 'Ronaldson', u'Bernardi', u'Fawcett', u'Ruston', u'Brandis', u'Fierravanti-Wells', u'Ryan', u'Fifield', u'Seselja', u'Bushby',  u'Johnston', u'Sinodinos', u'Canavan', u'Colbeck', u'Reynolds', 'Cash', 'Cormann', 'Heffernan', 'Parry', 'Payne', 'Smith', u'McKenzie', u'Nash', u'Williams', 'Macdonald', u'Scullion', u'McGrath', u'O\u2019Sullivan']
				            ),
				'Opp': set(
				           [u'McEwen', u'Brown', u'Bullock', u'Gallacher', u'Moore', u'Gallagher', u'Singh', u'Cameron', u'Ketter', u'Urquhart', u'Carr', u'Lines', u'Polley', u'Ludwig', u'Wong', u'Collins', u'Marshall', 'Bilyk', 'Conroy', 'Dastyari', 'Lundy', 'McLucas', 'Peris', 'Sterle', u'O\u2019Neill']
				           ),
				'AG': set(
				          ['Di Natalie', 'Rhiannon', 'Ludlam', 'Whish-Wilson', 'Waters', 'Siewert', 'Milne', 'Wright', 'Hanson-Young', 'Rice']
				          ),
				'FFP': set(
				           ['Day']
				           ),
				'PUP': set(
				           ['Wang', 'Lambie', 'Lazarus']
				           ),
				'LD': set(
				          ['Leyonhjelm']
				          ),
				'AMEP': set(
				            ['Muir']
				            ),
				'IndX': set(
				            ['Xenophon']
				            ),
				'DLP': set(
				            ['Magigan']
				            )
				}
		
		# Additions and removals of senators and groups in the 44th Parliament
		# Info from: http://www.aph.gov.au/Senators_and_Members/Senators/Senate_Composition
		# No need to change anything for Senator Madigan (left LDP on 4/9/2014)
		# Senator Lambie leaves PUP on 24/11/2014
		if date_of_division > datetime(2014, 11, 24):
			dict_senators_in_groups['IndL'] = set('Lambie')
			dict_senators_in_groups['PUP'].remove('Lambie')
		# Senator Lazarus leaves PUP on 16/03/2015
		if date_of_division > datetime(2015, 3, 16):
			dict_senators_in_groups['IndLaz'] = set('Lazarus')
			dict_senators_in_groups['PUP'].remove('Lazarus')
		# FIXME: Still need to add the others

	return dict_senators_in_groups

def count_by_group(list_of_ayes, list_of_noes, date_of_division):
	"""Takes a list of AYES senators and NOES senators and returns a dict of party votes"""

	groupsList = senators_in_groups_by_date(date_of_division)
	division_votes_by_group = {}
		
	for name, group in groupsList.iteritems():
		if (group.isdisjoint(list_of_noes) and group.isdisjoint(list_of_ayes)):
			division_votes_by_group[name] = '-'
		elif group.isdisjoint(list_of_noes):
			division_votes_by_group[name] = 'Yes'
		elif group.isdisjoint(list_of_ayes):
			division_votes_by_group[name] = 'No'
		else:
			division_votes_by_group[name] = 'Split'

	return division_votes_by_group


def getParlInfoId(id):
	# Build the URL based on the System ID.

	try:
		url = urllib2.urlopen(baseUrl + urllib.quote('\"' + id + '\"'))
	except URLError as e:
		print e.reason
				
	content = url.read()
	soup = BeautifulSoup(content)
	return soup

def pageScraper(listOfIds):
	return True

	#
	# Takes a list of Ids outputted by divisionsSearch(), then for each of them
	# calls divisionsFromId to get back a dict with the names of each of the
	# members who voted AYES and NOES in the division along with the metadata from
	# the ParlInfo segment. Then determines the ways each group voted with
	# membersIntoGroups().
	#

	# First, get a list back of dicts of division data.
	#divisionsDataList = []
	#for id in listOfIds:
		#verbosePrinter('pageScraper: ' + id)
		#divisionsDataList.append(divisionsFromId(id))

	#return divisionsDataList

	# Next, determine the aggregate vote of each group and add to the end
	# of the list.
	#divisionsGroups = []
	#for divisionData in divisionsDataList:
	#    divisionsGroups.append(membersIntoGroups(divisionData))

	#return divisionsGroups

def isNumber(number):
	"""If it isn't a number, return 0, rather than having the script die."""

	if number.isdigit():
		return int(number)
	else:
		return int(0)

def divisionsFromId(id):
	#
	# Get the Senate Journal page from ParlInfo with Beautiful Soup and parse for divisions
	#

	#url = urllib2.urlopen("http://parlinfo.aph.gov.au/parlInfo/search/display/display.w3p;query=Id%3A%22chamber%2Fjournals%2F091e576f-461d-48eb-81fc-15612e3b8693%2F0055%22")
	#url = urllib2.urlopen('http://parlinfo.aph.gov.au/parlInfo/search/display/display.w3p;query=Id%3A%22chamber%2Fjournals%2F8cf7f440-8fe3-4b53-8d97-cd79dcc54fcb%2F0056%22') # 9 Feb 2015

	verbosePrinter('divisionsFromId: ' + id)

	soup = getParlInfoId(id)

	# Metadata from the box at the top of each ParlInfo page
	divisionDate = datetime.strptime(soup.select(".mdItem")[3].contents[0], '%d-%m-%Y') # Date of the sitting
	divisionItemNum = isNumber(soup.select(".mdItem")[1].contents[0].split(None, 1)[0]) # Item number
	divisionBill = soup.select(".mdItem")[1].contents[0].split(None, 1)[1] # Bill name
	divisionBill = divisionBill.replace(u'\u2014', '-') # Bill name without the UniCode dash
	divisionHouse = soup.select(".mdItem")[4].contents[0] # House (ie., 'Senate')
	divisionParl = int(soup.select(".mdItem")[5].contents[0]) # Parliament Number
	divisionJoural = int(soup.select(".mdItem")[6].contents[0]) # Journal Number
	divisionPage = isNumber(soup.select(".mdItem")[7].contents[0]) # Page
	divisionParlInfoId = soup.select(".mdItem")[9].strong.contents[0] # ParlInfo ID
	divisionUrl = baseUrl + urllib.quote('\"' + id + '\"') # URL of Journal segment

	# Find everything with a HTML clas of 'Division[Head|List]' and stick it in divisionData
	divisionData = soup.find_all(class_ = ["DivisionHead", "DivisionList"])

	divisionsNumberToday = 0 # This actually should be divisions this segment
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
			divisionsMetaData = {
			'date': divisionDate,
			'house': divisionHouse,
			'item': divisionItemNum,
			'number': divisionsNumberToday,
			'bill': divisionBill,
			'journal': divisionJoural,
			'page': divisionPage,
			'parl': divisionParl,
			'id': divisionParlInfoId,
			'url': divisionUrl,
			'ayes': divisionAyesNumber}
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
	
	verbosePrinter('Divisions in segment: ' + str(divisionsNumberToday))

	# What sort of division was it? This still needs a bit of work.
	# Here are the various strings I've seen:
	# 'That this bill be now read a second time.'
	# 'Question—That the amendment be agreed to—put.'
	# 'Main question, as amended, put.'
	# 'Question—That Schedule 1, as amended, be agreed to—put.'
	# 'That this bill be now read a third time.'
	# 'Question—That Senator Fifield’s amendment to Senator Siewert’s proposed amendment be agreed to—put.'
	# 'Question—That the amendment in respect of nos 1 and 2 be agreed to—put.'
	# 'Question—That Schedule 1, Part 1 stand as printed—put. <-- This may be technically an amendment.
	# 
	# This one is too greedy: 	'Question2': u'Question(?:\u2014(.*)\u2014)\s*put\.'

	# This section below here doesn't work for some reason.

	divisionTypeSearch = {
	'First reading': u'bills*\s*be\s*now\s*read\s*a\s*first',
	'Second reading':u'bills*\s*be\s*now\s*read\s*a\s*second',
	'Third reading': u'bills*\s*be\s*now\s*read\s*a\s*third',
	'Amendment': u'(proposed\s*amendments*\s*be\s*agreed\s*to\u2014put\.|Question\u2014That.* as\s*amended,\s*be\s*agreed\s*to\u2014put\.|Question\u2014That\s*the\s*amendments*.*be\s*agreed\s*to\u2014put\.|questions*,\s*as\s*amended,\s*put\.)',
	'Stand as printed': u'stand\s*as\s*printed\u2014put\.',
	'SSO': 'moved\u2014That\s*so\s*much\s*of\s*the\s*standing\s*orders\s*be\s*suspended'
	}

	# Get all of the relevant text from the page to search division type
	# The only obvious way to do this is to dump out all of the potentially
	# relevant text and go through each line to see if it matches one of our
	# regular expressions.
	segmentDivisionTypes = []
	divisionText = soup.select('.JNP1')

	for eachLine in divisionText:
		for divType, divSearch in divisionTypeSearch.iteritems():
			if re.search(divSearch, unicode(eachLine), re.UNICODE):
				verbosePrinter(divType + ': ' + str(eachLine))
				segmentDivisionTypes.append(divType)
	
	if len(segmentDivisionTypes) == divisionsNumberToday:
		for divisionNumber in divisionsTable.iterkeys():
			divisionsTable[divisionNumber]['metadata']['type'] = segmentDivisionTypes[divisionNumber - 1]
	else:
		for divisionNumber in divisionsTable.iterkeys():
			divisionsTable[divisionNumber]['metadata']['type'] = 'Unknown'
	
	#print segmentDivisionTypes

	return divisionsTable

def membersIntoGroups(divisionAyes, divisionNoes):
	#
	# Map the senators back to their groups and print out the group vote.
	# Input is a divisionsTable of a segment with one or more divisions.
	#
	# FIXME: At the moment this is disconnected from the rest of the script!
	#

	groupVotes = {}

	for name, group in groupsList.iteritems():
		if (group.isdisjoint(divisionNoes) and group.isdisjoint(divisionAyes)):
			groupVotes[name] = '-'
		elif group.isdisjoint(divisionNoes):
			groupVotes[name] = 'Yes'
		elif group.isdisjoint(divisionAyes):
			groupVotes[name] = 'No'
		else:
			groupVotes[name] = 'Split'

	return groupVotes

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

	verbosePrinter('Found ' + str(numResults) + ' journal segments on ' + str(numPages) + ' pages.')

	# The System ID is identified with the 'sumMeta' class in the file
	searchData = soup.find_all(class_ = 'sumMeta')

	for each in searchData:
		searchLine = each.contents[0].split()[7]
		#   for pageId in soup.select('.sumMeta')[50].contents[0].split()[7]:
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
	# FIXME: None of these work any more because I've killed the pageScraper function!
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

def json_serial(obj):
	"""JSON serializer for objects not serializable by default json code"""
	
	if isinstance(obj, datetime):
		serial = obj.isoformat()
		return serial
	raise TypeError ("Type not serializable")

def date_hook(json_dict):
	"""Turn JSON dates back into python datetime objects"""
	for (key, value) in json_dict.items():
		try:
			json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
		except:
			pass
	return json_dict

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

def main():

	startDate = '25/03/2015'
	endDate = '26/03/2015'

	# Get the list of IDs of divisions in the date range from ParlInfo
	divisionIdList = divisionSearch(startDate, endDate)

	# Get the full list of individual votes.
	divisionsDataList = []
	for divisionId in divisionIdList:
		divisionsDataDict = divisionsFromId(divisionId)
		for segmentNumber in divisionsDataDict.iterkeys():
			divisionsDataList.append(divisionsDataDict[segmentNumber])
	
	print divisionsDataList

	# Get the party/group votes
	# Note, this has been put in as a separate step because ocasionally either the vote counter
	# or the grouper will crash, brining the whole process to a halt. 
	divisionsGroupsList = []
	for divisionsData in divisionsDataList:
		groupDict = {}
		groupDict.update(count_by_group(divisionsData['AYES'], 
		                                divisionsData['NOES'], 
		                                divisionsData['metadata']['date']))
		groupDict['metadata'] = divisionsData['metadata']
		groupDict['ayes'] = divisionsData['AYES']
		groupDict['noes'] = divisionsData['NOES']
		divisionsGroupsList.append(groupDict)

	# Sort by date, and then item (not sure if 'item' is that useful to sort on though)
	divisionsGroupsList.sort(key=lambda x: (x['metadata']['date'], x['metadata']['item']))
	
	# Save the results into a JSON file
	filename = "divisions-{}{}{}-{}{}{}.json".format(startDate.split('/')[2], startDate.split('/')[1], startDate.split('/')[0], endDate.split('/')[2], endDate.split('/')[1], endDate.split('/')[0])
	with open(filename, 'w') as outfile:
		json.dump(divisionsGroupsList, outfile, default=json_serial)
		verbosePrinter("Saved JSON file.")
	
	# To import the JSON file into a python object:
	# with open("divisions-20150325-20150326.json") as json_file:
	#   json_data = json.load(json_file, object_hook=date_hook)

	#for eachLine in divisionsGroupsList:
	#	print eachLine, "\n"

	#global divisionsGroupsList 

	print 'done.'

if __name__ == "__main__":
	main()
