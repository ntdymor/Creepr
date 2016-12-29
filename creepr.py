from urllib.request import urlopen
from urllib.request import Request
from urllib.request import HTTPError
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import json
import os
import errno

import sys

def createSafeUrl(unsafeUrl):
	urlSplit = unsafeUrl.rsplit('/', 1)
	urlMain = urlSplit[0]
	urlPath = urlSplit[1]		
	safeUrlPath = quote(urlPath)	
	safeFullUrl = urlMain + '/' + safeUrlPath
	return safeFullUrl

def getHTMLObject(url):	
	bsObj = None	
	try:		
		req = Request(url)
		response = urlopen(req)

	except HTTPError as e: 	#catches if the server or page return an error
		print(e)
		print(url + ' is bad')
		return None

	try:
		bsObj = BeautifulSoup(response.read(), "html.parser")
		#newNameList = bsObj.findAll("span", class_="green")

	except AttributeError as e: #catches if the attribute is not found
		print(e)
		return None	

	return bsObj
	
def getImageType(url):
	urlSplit = url.rsplit('.', 1)
	urlImageType = urlSplit[1]
	return '.' + urlImageType
	
def printImage(url, count, outputDir):
	newCount = count + 1
	try:
		os.makedirs(outputDir)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

	f = open(outputDir + str(newCount) + getImageType(url),'wb')
	f.write(urlopen(url).read())
	f.close()
	return newCount
	
def printImages(pageObj, count, outputDir):
	newCount = count
	if pageObj == None:
		print("Title could not be found")
	else:
		imageLists = pageObj.findAll("script", type="application/ld+json")
		for imageList in imageLists:
			data = str(imageList.getText())
			formattedImageList = json.loads(data)
			if 'image' not in formattedImageList:
				print("No image to print on this link")
			else:
				if isinstance(formattedImageList["image"], dict):
					for image in formattedImageList["image"]['@list']:
						newCount = printImage(image, newCount, outputDir)
				else:
					newCount = printImage(formattedImageList["image"], newCount, outputDir)
	return newCount

def followLinks(archivePageObj):
	count = 0
	if archivePageObj == None:
		print("No archive loaded")
	else:
		links = archivePageObj.findAll("a", target="_blank")
		for link in links:
			print("Opening link: " + link["href"])
			bsObj = getHTMLObject(link["href"])			
			count = printImages(bsObj, count)
	
def readPage(currentPageObj, url, count, outputDir):
	newCount = count
	if currentPageObj == None:
		print("Title could not be found")
	else:
		linkUrlLists = currentPageObj.findAll("script", type="application/ld+json")
		for linkUrlList in linkUrlLists:
			data = str(linkUrlList.getText())
			linkUrls = json.loads(data)			
			if isinstance(linkUrls['itemListElement'], list):
				for linkUrl in linkUrls['itemListElement']:
					print('Delving into {0}'.format(createSafeUrl(linkUrl['url'])))
					childPageObj = getHTMLObject(createSafeUrl(linkUrl['url']))
					newCount = printImages(childPageObj, newCount, outputDir)					
			else:				
				print('Page {0} not in expected format'.format(url))
	return newCount

def getNextPage(homePageUrl, count):
	return homePageUrl + 'page/' + str(count)
				
def readSite(homePageUrl, pageLimit, outputDir):
	pageCounter = 1
	imageCounter = 0
	currentUrl = homePageUrl
	while (pageCounter <= pageLimit and currentUrl != 'Out of pages'):
		currentPageObj = getHTMLObject(currentUrl)
		imageCounter = readPage(currentPageObj, currentUrl, imageCounter, outputDir)
		pageCounter += 1
		currentUrl = getNextPage(homePageUrl, pageCounter)
		
		
		
def prepareUrl(url):
	safeUrl = url
	urlBeggining = "http://"
	urlEnd = "/"
	if(urlBeggining not in url):
		safeUrl = urlBeggining + safeUrl
		
	if(not url.endswith("/")):
		safeUrl = safeUrl + urlEnd
	return safeUrl
	
def prepareOutputDir(outputDir):
	safeOutputDir = outputDir
	outputDirEnding = "/"
	if(not outputDir.endswith(outputDirEnding)):
		safeOutputDir = safeOutputDir + outputDirEnding
	
	return safeOutputDir


tumUrl = ""
pageCount = 0
outputDir = ""

if (len(sys.argv) == 4):
	tumUrl = sys.argv[1] 
	outputDir = sys.argv[2] 
	pageCount = int(sys.argv[3])
	
	
elif (len(sys.argv) == 3):
	tumUrl = sys.argv[1] 
	outputDir = sys.argv[2]
	pageCount = int(input("Enter many pages do you want to creep through: "))
	
elif (len(sys.argv) == 2):
	tumUrl = sys.argv[1] 
	outputDir = input("Enter the folder name to save to: ")
	pageCount = int(input("Enter many pages do you want to creep through: "))
	
	
else:
	tumUrl = input("Enter the Tumblr url to creep on: ")
	outputDir = input("Enter the folder name to save to: ")
	pageCount = int(input("Enter many pages do you want to creep through: "))
	
	
readSite(prepareUrl(tumUrl), pageCount, prepareOutputDir(outputDir))












