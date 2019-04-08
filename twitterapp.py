from birdy.twitter import UserClient
from PIL import Image
import requests
from io import BytesIO
import time
import pickle
import pygame
import qrcode
import unicodedata
import json
import sys

if(len(sys.argv) == 2):
	streamMode = sys.argv[1]
	loadData = True
elif(len(sys.argv) == 3):
	streamMode = sys.argv[1]
	userScreenName = sys.argv[2]
	loadData = True
elif(len(sys.argv) == 4):
	streamMode = sys.argv[1]
	userScreenName = sys.argv[2]
	loadData = False
else:
	streamMode = "Likes" #Timeline or Likes or Home_Timeline
	userScreenName = "@USER HERE"
	loadData = True


amountOfTweetsToDownload = 20

pickleFileName = streamMode + userScreenName + ".pkl"

switchImageStart = 600
switchImage = switchImageStart

display_width = 700
display_height = 800

profPicSize = 50

artDisplay_width = 700
artDisplay_height = 700

pygame.font.init()
myfont = pygame.font.SysFont('Arial', 40)
loadfont = pygame.font.SysFont('Arial', 10)
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption(userScreenName + "'s " + streamMode)

clock = pygame.time.Clock()
crashed = False




CONSUMER_KEY 	= 
CONSUMER_SECRET = 
TOKEN_KEY 		= 
TOKEN_SECRET 	= 

client = UserClient(CONSUMER_KEY, CONSUMER_SECRET, TOKEN_KEY, TOKEN_SECRET)

try:
	pickle_in = open(pickleFileName,"rb")
	ID, response = pickle.load(pickle_in)
except:
	ID = -1
	response = -1

if(loadData == False):
	ID = -1
	response = -1

def generateQRCode(url):
	qr = qrcode.QRCode(
		version = 1,
		error_correction = qrcode.constants.ERROR_CORRECT_H,
		box_size = 10,
		border = 4,
	)
	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image()
	img.thumbnail((500, 500), Image.ANTIALIAS)
	img.save("qrCode.png")

	qrcodePygame = pygame.image.load("qrCode.png")

	return qrcodePygame

def getResponse(ID, oldResponse):
	global streamMode
	imageList = []
	

	if(streamMode == "Likes"):
		resource = client.api.favorites.list
	elif(streamMode == "Timeline"):
		resource = client.api.statuses.user_timeline
	elif(streamMode == "Home_Timeline"):
		resource = client.api.statuses.home_timeline
	
	try:
		if(ID == -1):
			response = resource.get(screen_name=userScreenName, count=amountOfTweetsToDownload, tweet_mode="extended")
		else:
			response = resource.get(screen_name=userScreenName, count=amountOfTweetsToDownload, max_id=ID, tweet_mode="extended")
			if(len(response.data) >= 2):
				response.data = response.data[1:]
			else:
				response = resource.get(screen_name=userScreenName, count=amountOfTweetsToDownload)
	except:
		response = oldResponse

	lastID = response.data[-1]["id"]

	return lastID, response

#Returns a list of (ImageUrl, ProfPicUrl, ScreenName, TweetUrl)
def getImageList(response):
	imageList = []
	i = 0
	for tweet in response.data:
		url = -1
		try:
			if streamMode == "Likes" or streamMode == "Home_Timeline":
				screenName = tweet["user"]["screen_name"]
				profPic = tweet["user"]["profile_image_url"]
				url = tweet["entities"]["media"][0]["url"]
	
				if "extended_entities" in tweet.keys():
					if(tweet["extended_entities"]["media"][0]["type"] == "video"):
						continue
					if("ShowImage" not in tweet.keys()):
						for image in tweet["extended_entities"]["media"]:
							imageList.append((image["media_url_https"], profPic, screenName, url))
						tweet["ShowImage"] = showImage
				elif "entities" in tweet.keys() and "media" in tweet["entities"].keys():
					imageList.append((tweet["entities"]["media"][0]["media_url_https"], profPic, screenName, url))
				else:
					continue
	
	
			elif streamMode == "Timeline":
				screenName = tweet["retweeted_status"]["user"]["screen_name"]
				profPic = tweet["retweeted_status"]["user"]["profile_image_url"]
				url = tweet["retweeted_status"]["entities"]["media"][0]["url"]
	
				if "extended_entities" in tweet.keys():
					if(tweet["extended_entities"]["media"][0]["type"] == "video"):
						continue
					if("ShowImage" not in tweet.keys()):
						for image in tweet["extended_entities"]["media"]:
							imageList.append((image["media_url_https"], profPic, screenName, url))
						tweet["ShowImage"] = showImage
				elif "entities" in tweet["retweeted_status"].keys() and "media" in tweet["retweeted_status"]["entities"].keys():
					imageList.append((tweet["retweeted_status"]["entities"]["media"][0]["media_url_https"], profPic, screenName, url))
				else:
					print(tweet.keys())
					continue
		except:
			continue
	return imageList

def getRenderElements(image, profPic, screenName, url):
	global profPicSize
	try:
		buff = requests.get(image)
		img = Image.open(BytesIO(buff.content))
		img.format = "PNG"
		img.thumbnail((artDisplay_width, artDisplay_height), Image.ANTIALIAS)
		img.save('loadPic.png')
		
		pyImage = pygame.image.load("loadPic.png")
	except:
		return -1,- 1, -1, -1, -1

	try:
		buff = requests.get(profPic)
		profPicImg = Image.open(BytesIO(buff.content))
		profPicImg.format = "PNG"
		profPicImg.thumbnail((profPicSize, profPicSize), Image.ANTIALIAS)

		mode = profPicImg.mode
		size = profPicImg.size
		data = profPicImg.tobytes()
		profPicGame = pygame.image.fromstring(data, size, mode)
	except:
		profPicGame = -1

	try:
		screenNameGame = myfont.render("@" + str(screenName), True, (255, 255, 255))
	except:
		screenNameGame = -1

	qrcodePygame = generateQRCode(url)
	return pyImage, ((artDisplay_width-img.width)/2, (artDisplay_height-img.height)/2), profPicGame, screenNameGame, qrcodePygame


print(ID)
gotoNext = False
goBack = False
paused = False
showQR = False
displayed = False
pauseMess = loadfont.render("Paused.", True, (255, 255, 255))
loadingMess = loadfont.render("Loading...", True, (255, 255, 255))
while not crashed:
	
	ID, response = getResponse(ID, response)

	imageList = getImageList(response)
	print(imageList[0])
	if(imageList == []):
		continue

	listLength = len(imageList)
	curElement = 0

	

	while curElement < listLength:
		if(not displayed):
			print(imageList[curElement])
			image, profPic, screenName, url = imageList[curElement]
			image, pos, profPic, screenName, url = getRenderElements(image, profPic, screenName, url)
			if image != -1:
				gameDisplay.fill((0,0,0))
				gameDisplay.blit(image, pos)
				displayed = True
			else:
				displayed = False
			if(profPic != -1):
				gameDisplay.blit(profPic, (10, artDisplay_height+10))
			if(screenName != -1):
				gameDisplay.blit(screenName, (10+profPicSize, artDisplay_height+10))
			displayed = True
		
		clock.tick(5)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					paused = not paused
				if event.key == pygame.K_RIGHT:
					gotoNext = True
				if event.key == pygame.K_LEFT:
					goBack = True
				if event.key == pygame.K_q:
					showQR = not showQR
					paused = showQR


		if showQR:
			gameDisplay.fill(pygame.Color("black"), (0, 0, artDisplay_width, artDisplay_height))
			gameDisplay.blit(url, ((artDisplay_width-370)/2,(artDisplay_height-370)/2))
		elif image != -1:
			gameDisplay.fill(pygame.Color("black"), (0, 0, artDisplay_width, artDisplay_height))
			gameDisplay.blit(image, pos)

		if paused:
			gameDisplay.blit(pauseMess, (10, display_height-20))
		else:
			gameDisplay.fill(pygame.Color("black"), (10, display_height-20, 30, display_height))


		if(showQR == False and displayed == True):
			switchImage = max([0, switchImage - 1])

		if(curElement > 0 and goBack and displayed):
			curElement -= 1
			switchImage = switchImageStart
			displayed = False
			gotoNext = False
			goBack = False
			showQR = False
			gameDisplay.blit(loadingMess, (display_width-40, display_height-20))
		else:
			goBack = False

		if(((switchImage <= 0 and not paused) or gotoNext) and displayed):
			curElement += 1
			switchImage = switchImageStart
			displayed = False
			gotoNext = False
			showQR = False
			gameDisplay.blit(loadingMess, (display_width-40, display_height-20))
		else:
			gotoNext = False
		pygame.display.update()

	displayed = False
	gotoNext = False
	showQR = False
	switchImage = switchImageStart
	
	pygame.display.update()

	pickle_out = open(pickleFileName, "wb")
	pickle.dump((ID, response), pickle_out)



pygame.quit()