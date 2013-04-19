#!/usr/bin/python

import urllib
import urllib2
import random
import re

def cbk(a, b, c):
	per = 100.0 * a * b / c
	if per > 100:
		per = 100
	print '%.2f%%' % per

def parse_xml(song_id):
	#print song_id
	xml_loc = 'http://www.xiami.com/song/playlist/id/' + song_id + '/object_name/default/object_id/0'
	#print xml_loc

	headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1'}

	request = urllib2.Request(xml_loc, headers = headers)
	response = urllib2.urlopen(request)
	text = response.read()
	#print text

	loc_reg=r"<location>(.*)</location>"
	match = re.search(loc_reg, text)
	if match:
		location = match.group(1)
		print location
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
	print('unencypt_location: %s') % target


	return target

def download_music(location, song_name):
	path = '/Users/fengchj/temp/music/' + song_name +  '.mp3'
	urllib.urlretrieve(location ,path)
	print 'download ' + song_name + ' done!'

def main():
	#song_id = raw_input()
	user_id = '3270716'
	user_fav_url = 'http://www.xiami.com/space/lib-song/u/' + user_id + '/page/'
	page_no = 1
	song_id_list = []
	while True:
		url = user_fav_url + str(page_no)
		print url
		headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1'}
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

		
	print song_id_list
	print len(song_id_list)

	for song_id in song_id_list:
		#song_id = '72234'
		#print song_id
		(location, song_title, artist) = parse_xml(song_id)

		target = parse_location(location)
		download_music(target, artist + ' - ' + song_title)
	print ('%d songs download!') % len(song_id_list) 
if __name__ == '__main__' :
	main()
