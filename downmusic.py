#!/usr/bin/python
#coding: utf-8

import urllib
import urllib2
import re
import sys
import os
import time
import math
from mutagen.easyid3 import EasyID3


def parse_xml(song_id):
	#print song_id
	xml_loc = 'http://www.xiami.com/song/playlist/id/' + song_id + '/object_name/default/object_id/0'
	#print xml_loc

	headers = {
		'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) Chrome/24.0.1312.57'
	}
	request = urllib2.Request(xml_loc, headers = headers)
	response = urllib2.urlopen(request)
	text = response.read()
	#print text

	loc_reg=r"<location>(.*)</location>"
	match = re.search(loc_reg, text)
	if match:
		location = match.group(1).strip()
		#print location
	else:
		print 'location not match'

	song_title_reg=r"<title><\!\[CDATA\[(.*)\]\]></title>"
	match = re.search(song_title_reg, text)
	if match:
		song_title = match.group(1).strip()
		#print song_title
	else:
		print 'song_title not match'

	artist_reg=r"<artist><\!\[CDATA\[(.*)\]\]></artist>"
	match = re.search(artist_reg, text)
	if match:
		artist = match.group(1).strip()
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

def download_music(location, song_name, base_dir):
	if not os.path.isdir(base_dir):
		os.mkdir(base_dir)

	path = base_dir + '/' + song_name +  '.mp3'
	urllib.urlretrieve(location ,path)

	write_id3(path, song_name)

	if os.path.getsize(path) < 2048 :
		return False
	else:
		print 'download ' + song_name + ' done!'
		return True

def write_id3(path, song_name):
	#write id3 info to song.
	try:
		audio = EasyID3(path)
	except Exception, e:
		#while source track doesn't have ID3 structure. malloc new EasyID3().
		audio = EasyID3()
	song_info = song_name.split(' - ')
	artist = song_info[0]
	title = song_info[1]
	audio["artist"] = unicode(artist, 'utf-8')
	audio["title"] = unicode(title, 'utf-8')
	audio.save(path)
	#print audio

def batch_download_music(song_id_list, base_dir):
	print song_id_list
	#print len(song_id_list)

	count = 0
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
				rt = download_music(target, artist + ' - ' + song_title, base_dir)
				if rt == False :
					raise Exception
				count = count + 1
				isFail = False
			except Exception, e:
				print ('song_id: %s') % song_id,
				print e
				#raise e
				time.sleep(math.pow(2, trytime))
				isFail = True
				trytime = trytime + 1
		if trytime == RETRY_TIME_LIMIT:
			print '!!!!!!!!!!!!!!!!! ' + song_id + ' (' + artist + '-' + song_title + ') download failed !!!!!!!!!!!!!!!!!!!!!'

	print ('%d songs download successful! %d songs download failed!') % (count, len(song_id_list) - count)

def get_song_id_list(user_id):
	user_fav_url = 'http://www.xiami.com/space/lib-song/u/' + user_id + '/page/'
	page_no = 1
	song_id_list = []
	while True:
		url = user_fav_url + str(page_no)
		print url
		headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) Chrome/24.0.1312.57'}
		request = urllib2.Request(url, headers = headers)
		response = urllib2.urlopen(request)
		text = response.read()
		#print text

		song_reg=r"\"lib_song_(\d{1,20})\""
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

	base_dir = raw_input('input your music lib directory (current dir by default): ')
	if not base_dir:
		base_dir = 'music'

	song_id_list = get_song_id_list(user_id)

	batch_download_music(song_id_list, base_dir)
	 
if __name__ == '__main__' :
	main()
