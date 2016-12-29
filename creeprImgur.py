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

	except AttributeError as e: #catches if the attribute is not found
		print(e)
		return None	

	return bsObj
	
def getImageType(url):
	urlSplit = url.rsplit('.', 1)
	urlImageType = urlSplit[1]
	return '.' + urlImageType

def switchMP4toGIF(url):
	urlSplit = url.rsplit('.', 1)
	urlImage = urlSplit[0]

	return urlImage + '.gif'
	
def printImage(url, count, outputDir):
	newCount = count + 1
	goodUrl = url

	imageType = getImageType(url)
	if(imageType == '.mp4'):
		imageType = '.gif'
		goodUrl = switchMP4toGIF(url)

	try:
		os.makedirs(outputDir)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

	f = open(outputDir + str(newCount) + imageType,'wb')
	print('printing {0}'.format(goodUrl))
	f.write(urlopen(goodUrl).read())
	f.close()
	return newCount
	
def printImages(pageObj, count, outputDir):
	newCount = count
	if pageObj == None:
		print("Title could not be found")
	else:
		imgTagList = pageObj.findAll("img", {"itemprop" : "contentURL" })
		for imgTag in imgTagList:
			imgUrl = str("http:" + imgTag["src"])
			newCount = printImage(imgUrl, newCount, outputDir)

		gifTagList = pageObj.findAll("meta", {"itemprop" : "contentURL" })
		for gifTag in gifTagList:
			gifUrl = str(gifTag["content"])
			newCount = printImage(gifUrl, newCount, outputDir)
		
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
	baseUrl = 'http://imgur.com'
	if currentPageObj == None:
		print("Title could not be found")
	else:
		linkUrlLists = currentPageObj.findAll("a",  {"class" : "image-list-link" })
		for linkUrlList in linkUrlLists:
			data = str(linkUrlList["href"])		
			print('Delving into {0}'.format(createSafeUrl(baseUrl + data)))
			childPageObj = getHTMLObject(createSafeUrl(baseUrl + data))
			newCount = printImages(childPageObj, newCount, outputDir)				
	return newCount

def getNextPage(homePageUrl, count):
	return homePageUrl + '/page/' + str(count)
				
def readSite(homePageUrl, pageLimit, outputDir):
	pageCounter = 0
	imageCounter = 0
	currentUrl = homePageUrl
	while (pageCounter < pageLimit and currentUrl != 'Out of pages'):
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
		
	if(url.endswith("/")):
		safeUrl = safeUrl[:-1]
	return safeUrl
	
def prepareOutputDir(outputDir):
	safeOutputDir = outputDir
	outputDirEnding = "//"
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
	tumUrl = input("Enter the Imgur url to creep on: ")
	outputDir = input("Enter the folder name to save to: ")
	pageCount = int(input("Enter many pages do you want to creep through: "))
	
	
readSite(prepareUrl(tumUrl), pageCount, prepareOutputDir(outputDir))












