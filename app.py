import os
import sys
import requests
import requests.packages.urllib3
import json

requests.packages.urllib3.disable_warnings()

#albumUrl = "https://www.facebook.com/1118241991550593/photos/?tab=album&album_id=1127894767251982"
albumUrl = str(sys.argv[1])

albumId = albumUrl.split("album_id=",1)
try:
	album = albumId[1]
except Exception as e:
	print "Album ID not found"
	sys.exit(1)

print "Download Album %s" % (album)
facebook_token = "EAAYmMthewQsBAD2KcTar6h7DEfXPZATLFZBvqdu5N6XI2JkkyPx7W3pCgyXReIQ3xcD4hVT3YHUtmWweGjYq4pGi0ZCA3O3J7JmhJ8Ir81oMj4weYoJssWobVwkueB4KBZAceJsIEmGaSEGPflSJ5VvSCZBzBBIYZD"

def setAlbumUrl(albumId):
	setUrlAlbum = "https://graph.facebook.com/v2.8/%s/photos?access_token=%s&limit=100" % (albumId, facebook_token)

	getPaging = requests.get(setUrlAlbum)
	loadURL = json.loads(getPaging.content)
	albumURL = []
	nextPage = loadURL['paging']
	albumURL.append(setUrlAlbum)

	if "next" in nextPage:
		albumURL.append(loadURL['paging']['next'])
	
	while "next" in nextPage:
		getPaging = requests.get(setUrlAlbum)
		loadURL = json.loads(getPaging.content)
		nextPage = loadURL['paging']
		if "next" in nextPage:
			albumURL.append(loadURL['paging']['next'])
			setUrlAlbum = loadURL['paging']['next']

	return albumURL


def getPhotosId(setAlbumUrl):
	PhotosId = []
	for albumURL in setAlbumUrl:
		try:
			getPhotos = requests.get(albumURL)
			setIdPhotosJson = json.loads(getPhotos.content)	
			
			for id in setIdPhotosJson['data']:
				idPhotos = id['id']
				PhotosId.append(idPhotos)
		except requests.exceptions.RequestException as e:  # This is the correct syntax
		    print e
		    sys.exit(1)
		    
	return PhotosId

def getPhotosURL(getPhotosId):
	photosURL = []	
	for photosId in getPhotosId:
		photoId = photosId
		setUrlPhoto = "https://graph.facebook.com/v2.8/%s/picture?access_token=%s" % (photoId, facebook_token)
		photosURL.append(setUrlPhoto)
	return photosURL

def downloadAlbum(albumId):
	albumURL = setAlbumUrl(albumId)

	photoId = getPhotosId(albumURL)
	photoURL = getPhotosURL(photoId)
	print "Download %i photos" %(len(photoId))
	number = 0

	if not os.path.exists(albumId):
		os.makedirs(albumId)

	for image in photoURL:
		try:

			number += 1
			chekImageJPG = "%s/%s.jpg" %(albumId,number)
			chekImagePNG = "%s/%s.png" %(albumId,number)
			if os.path.exists(chekImageJPG) or os.path.exists(chekImagePNG):
				continue

			response = requests.get(image, stream=True)
			contentType = response.headers['Content-Type']

			if contentType.startswith('image/png'):
				imageType = "png"
			elif contentType.startswith('image/jpeg'):
				imageType = "jpg"

			nameImage = "%s/%s.%s" %(albumId,number,imageType)

			print "Please Wait %s while downloading...."%(nameImage)
			
			with open(nameImage, 'wb') as handle:
			        if not response.ok:
			            print response

			        for block in response.iter_content(1024):
			            if not block:
			                break

			            handle.write(block)
		except requests.exceptions.RequestException as e:  # This is the correct syntax
			print e
			os.remove(nameImage)
			sys.exit(1)

	print "Finish Download %i photos" %(len(photoId))
	return "finish"


# albumurl = setAlbumUrl(album)
# photoid = getPhotosId(albumurl)
if __name__ == "__main__":
	downloadAlbum(album)


