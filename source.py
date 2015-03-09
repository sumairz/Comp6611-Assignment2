from bs4 import BeautifulSoup
import urllib
import sys
import os
import re
import psycopg2
import time

start = time.time()

con = None
con = psycopg2.connect(database='assignment2', user='postgres', password='') 
cur = con.cursor()
coreVal = "False"
priVal = "-1"
reportedDate = "-1"

fileCounter = 0;

pathName = "raw_chrome_issue/"

for file in os.listdir(pathName):
	if file.endswith(".txt"):
		print "\n"
		print " **** " + file + " **** "
		print "\n"
		
		f = open(pathName + file, 'r')
		soup = BeautifulSoup(f)		
		
		
		# Bug ID
		bug_id = file.split('.')
		bug_id = bug_id[0]
		
		
		# Getting Priority value
		for link in soup.findAll('a', attrs={'href': re.compile("label:Pri")}):
			if(priVal):
				priVal = link.get('href').split("-")
				if(len(priVal) > 1):
					priVal = priVal[1]
				else:
					priVal = '-1'
			else:
				priVal = '-1'
			
			# Checking core or non-core module
			if(priVal == 0):
				coreVal = True
			else:
				coreVal = False
					
		
		# Getting OS name
		osVal = ""
		for link in soup.findAll('a', attrs={'href': re.compile("label:OS")}):
			osVal = link.get('href').split("-")
			if(len(osVal) > 1):
				osVal = osVal[1]	
			else:
				osVal = '-1'
		
		if(osVal == "" or osVal == '-1'):
			osVal = 'Empty'
			
		os_val_query = cur.execute("Select id from operating_system WHERE name = '"+osVal+"'")
		rows_status_os = cur.fetchall()
			
		for row in rows_status_os:
			os_value = row[0]
		
		
		# Getting Author Name
		mydivs = soup.findAll("div", { "class" : "author" })
		if(mydivs):		
			author = BeautifulSoup(str(mydivs[0]))
			authorEmail = author.select('.userlink')[0].contents[0]
			dev_id = cur.execute("INSERT INTO owner(email) VALUES('"+authorEmail+"')")		
		
			dev_idd = cur.execute("Select max(id) from owner")
			rows = cur.fetchall()
			
			for row in rows:
				dev_idd = row[0]			
				
			# Getting Reported Date
			reportedDate = author.select('.date')[0].get('title')		
		else:
			dev_idd = '-1'
	
		
		
		
		
		# Getting Bug status
		myTD = soup.findAll("td", { "id" : "issuemeta" })
		if(myTD):
			table = BeautifulSoup(str(myTD[0]))
			status = 'Empty'
            
                        if(table.find('span')):
                                status = table.find('span').contents[0]
			
			status_val = cur.execute("Select id from status WHERE name = '"+status+"'")
			rows_status = cur.fetchall()
			
			for row in rows_status:
				status_value = row[0]
		else:
			status_value = '-1'
		
		
 
		# Getting People starred
		mystarred = soup.findAll("div", { "id" : "issueheader" })
		if(mystarred):
			starred = BeautifulSoup(str(mystarred[0]))
			datastarred = starred.findAll("td", { "nowrap" : "nowrap" })		
			match = re.findall(r'(\d{1,})\s(people|person)\sstarred', str(datastarred), flags=0)
			if(match):
				ppl_star = str(match[0][0])
			else:
				ppl_star = '0'
		else:
			ppl_star = '0'
			
			
		coreVal = str(coreVal)
		priVal = str(priVal)
		dev_idd = str(dev_idd)
		os_value = str(os_value)
		status_value = str(status_value)
		
		# Executing SQL command
		
		cur.execute("INSERT INTO bug(priority,core_module,people_starred,date_reported,id,reported_by,os_id,status_id) VALUES("+priVal+",'"+coreVal+"',"+ppl_star+",'"+reportedDate+"',"+bug_id+","+dev_idd+","+os_value+","+status_value+")")
		
		con.commit()
		
		end = time.time()		
		fileCounter = fileCounter + 1
		print end - start
		print fileCounter
		
		os.remove(pathName+file)
		print("Delete file "+ file)
if con:
	con.close()

