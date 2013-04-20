#!/usr/bin/python

import urllib
import urllib2
import random
import re
import sys
import time
import math

def parse_xml(song_id):
	#print song_id
	xml_loc = 'http://www.xiami.com/song/playlist/id/' + song_id + '/object_name/default/object_id/0'
	#print xml_loc

	headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) Chrome/24.0.1312.57'}
	request = urllib2.Request(xml_loc, headers = headers)
	response = urllib2.urlopen(request)
	text = response.read()
	#print text

	loc_reg=r"<location>(.*)</location>"
	match = re.search(loc_reg, text)
	if match:
		location = match.group(1)
		#print location
	else:
		print 'location not match'

	song_title_reg=r"<title><\!\[CDATA\[(.*)\]\]></title>"
	match = re.search(song_title_reg, text)
	if match:
		song_title = match.group(1)
		#print song_title
	else:
		print 'song_title not match'

	artist_reg=r"<artist><\!\[CDATA\[(.*)\]\]></artist>"
	match = re.search(artist_reg, text)
	if match:
		artist = match.group(1)
		#print artist
	else:
		print 'artist not match'

	return (location, song_title, artist)

def parse_location(location):
	
	row = int(location[0])

	encypt_location = location[1:]
	#print('encypt_location: %s') % encypt_location
	encypt_loc_len = len(encypt_location)
	#print('len of encypt_location: %d') % encypt_loc_len
	column = encypt_loc_len/row 
	remainder = encypt_loc_len% row

	#print('row: %d')%row
	#print('column: %d') % column
	#print('remainder: %d') % remainder
	src_list = []
	unencypt_loc = ''
	iter = 0
	for i in range(0, remainder):
		sub_list = encypt_location[iter:iter + column + 1]
		iter = iter + column + 1
		src_list.append(sub_list)
	
	for i in range(0, row - remainder):
		sub_list = encypt_location[iter:iter+column]
		iter = iter + column
		src_list.append(sub_list)
	
	#for i in range(0, row):
	#	print src_list[i]

	for i in range(0, column + 1):
		for j in range(0, row):
			if i < len(src_list[j]):
				unencypt_loc += src_list[j][i]
	#print unencypt_loc
	#print(urllib.unquote(unencypt_loc))
	target = urllib.unquote(unencypt_loc).replace('^','0')
	#print('unencypt_location: %s') % target


	return target

def download_music(location, song_name):
	path = '/Users/fengchj/temp/music/' + song_name +  '.mp3'
	urllib.urlretrieve(location ,path)
	print 'download ' + song_name + ' done!'

def batch_download_music(song_id_list):
	print song_id_list
	#print len(song_id_list)

	for song_id in song_id_list:
		#print song_id

		#if errors ocurs during the download processing, re-try 3 times.
		RETRY_TIME_LIMIT  = 3
		isFail = True
		trytime = 0
		while isFail and  trytime < RETRY_TIME_LIMIT:
			try:
				(location, song_title, artist) = parse_xml(song_id)
				target = parse_location(location)
				download_music(target, artist + ' - ' + song_title)
				isFail = False
			except Exception, e:
				print ('song_id: %s') % song_id,
				print e
				time.sleep(math.pow(2, trytime))
				isFail = True
				trytime = trytime + 1
		if trytime == RETRY_TIME_LIMIT:
			print '!!!!!!!!!!!!!!!!! ' + song_id + ' (' + artist + '-' + song_title + ') download failed !!!!!!!!!!!!!!!!!!!!!'

	print ('%d songs download!') % len(song_id_list)

def get_song_id_list(user_id):
	user_fav_url = 'http://www.xiami.com/space/lib-song/u/' + user_id + '/page/'
	page_no = 1
	song_id_list = []
	while True:
		url = user_fav_url + str(page_no)
		#print url
		headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) Chrome/24.0.1312.57'}
		request = urllib2.Request(url, headers = headers)
		response = urllib2.urlopen(request)
		text = response.read()
		#print text

		song_reg=r"\"/song/(\d{1,20})\""
		result = re.findall(song_reg, text, re.S)
		#print result
		if len(result) == 0 :
			break
		song_id_list += result
		page_no = page_no + 1
	return song_id_list

def main():
	user_id = raw_input('input your Xiami\'s userid: ')
	#user_id = '3270716'

	song_id_list = get_song_id_list(user_id)

	batch_download_music(song_id_list)
	 
if __name__ == '__main__' :
	main()
