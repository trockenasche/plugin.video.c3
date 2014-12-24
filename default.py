import sys
import xbmc
import xbmcaddon
import urllib
import urllib2
import urlparse
import xbmcplugin
import xbmcgui
import xbmcvfs
import time
from xml.dom import minidom
from datetime import datetime, timedelta

addon = xbmcaddon.Addon('plugin.video.c3')
xmlurl = 'http://events.ccc.de/congress/2014/Fahrplan/schedule.xml'
addondir = xbmc.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(addondir):
	xbmcvfs.mkdirs(addondir)
loc = addon.getLocalizedString

if sys.argv[1] == 'resetetag':
	addon.setSetting('cache-etag', '')
	if xbmcvfs.exists(addondir + 'schedule.xml'):
		xbmcvfs.delete(addondir + 'schedule.xml')
	d = xbmcgui.Dialog()
	d.ok('c3 Videos Add-on', loc(30104))
	exit()

addon_handle = int(sys.argv[1])

resolution = addon.getSetting('resolution') #LQ - 0; HQ - 1; HD - 2
translated = addon.getSetting('translated') #original - 0; translated - 1
'''
def log(msg):
	with open(addondir + 'logfile.txt', 'a') as file:
		file.write("[" + time.strftime('%X') + "] " + msg + "\n")
'''

if not addon.getSetting('cache-etag') or not xbmcvfs.exists(addondir + 'schedule.xml'):
	response = urllib2.urlopen(xmlurl)
	addon.setSetting('cache-etag', response.headers.get('ETag'))
	xml = response.read()
	with open(addondir + 'schedule.xml', 'w') as file:
		file.write(xml)
else:
	req = urllib2.Request(xmlurl)
	req.add_header('If-None-Match', addon.getSetting('cache-etag'))
	try:
		response = urllib2.urlopen(req)
		addon.setSetting('cache-etag', response.headers.get('ETag'))
		xml = response.read()
		with open(addondir + 'schedule.xml', 'w') as file:
			file.write(xml)
	except urllib2.HTTPError:
		with open(addondir + 'schedule.xml', 'r') as file:
			xml = file.read()

parameters = urlparse.parse_qsl(sys.argv[2][1:])
parameters = dict(parameters)

if not xbmcvfs.exists(addondir + 'schedule.xml'):
	response = urllib2.urlopen('http://events.ccc.de/congress/2014/Fahrplan/schedule.xml')
	xml = response.read()
	with open(addondir + 'schedule.xml', 'w') as file:
		file.write(xml)
else:
	with open(addondir + 'schedule.xml', 'r') as file:
		xml = file.read()

# xml stuff

def parse_datetime_string(timestr):
	timestr = timestr.rsplit('+', 1)
	timeo = time.strptime(timestr[0], '%Y-%m-%dT%H:%M:%S')
	timeo = datetime.fromtimestamp(time.mktime(timeo))
	timezone = timestr[1].split(':', 1)
	timezone = timedelta(hours=int(timezone[0]), minutes=int(timezone[1]))
	return timeo - timezone

def find_current(xmlstr, roomstr):
	xmldoc = minidom.parseString(xmlstr)
	itemlist = xmldoc.getElementsByTagName('day')
	for s in itemlist:
		start = parse_datetime_string(s.getAttribute('start'))
		end = parse_datetime_string(s.getAttribute('end'))
		if start <= datetime.utcnow() < end:
			return find_current_room(s.firstChild, roomstr)
	return False

def find_current_room(node, roomstr):
	if (node.nodeType == minidom.Node.ELEMENT_NODE) and (node.nodeName == 'room') and (node.getAttribute('name') == roomstr):
		return find_current_talk(node)
	elif node.nextSibling is not None:
		return find_current_room(node.nextSibling, roomstr)
	else:
		return False

def find_current_talk(node):
	for event in node.childNodes:
		if (event.nodeType == minidom.Node.ELEMENT_NODE) and (event.nodeName == 'event'):
			date = event.getElementsByTagName('date').item(0)
			date = date.firstChild.data
			date = parse_datetime_string(date)
			duration = event.getElementsByTagName('duration').item(0)
			duration = duration.firstChild.data
			duration = duration.split(':', 1)
			duration = timedelta(hours=int(duration[0]), minutes=int(duration[1]))
			if date <= datetime.utcnow() < date + duration:
				return event
	return False

def get_tag_info(node, tag):
	final = False
	nodes = node.getElementsByTagName(tag)
	nodes = nodes.item(0).childNodes
	for i in nodes:
		if i.nodeType == minidom.Node.ELEMENT_NODE:
			final = []
			final.append(i.firstChild.data)
		elif not final:
			final = i.data
	if not final:
		return 'N/A'
	else:
		return final

#dicts and so on
    
halls = { '1' : loc(30001), '2' : loc(30002), 'G' : loc(30003), '6' : loc(30004) }
trans = { '0' : loc(30005), '1' : loc(30006) }

urls = { '1' : { '0' :
					{ '2' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_native_hd',
					'1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_native_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_native_lq'},
				'1' :
					{ '2' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_translated_hd',
					'1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_translated_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_translated_lq' }
			},
		'2' : { '0' :
					{ '1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_native_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_native_lq' },
				'1' :
					{ '1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_translated_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_translated_lq' }
			},
		'G' : { '0' :
					{ '1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_native_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_native_lq' },
				'1' :
					{ '1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_translated_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_translated_lq' }
			},
		'6' : { '0' :
					{ '1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_native_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_native_lq' },
				'1' :
					{ '1' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_translated_hq',
					'0' : 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_translated_lq' }
			}
	}
	

# display streams

for key, value in halls.iteritems():
	talk = find_current(xml, 'Saal ' + key)
	if key != '1' and resolution == '2':
		resolution = '1'
	if talk is not False:
		#log('Aktueller Talk in Saal ' + key + ': ' +  get_tag_info(talk, 'title') + '\tURL: ' + urls[key][translated][resolution])
		li = xbmcgui.ListItem(value + ' - ' + get_tag_info(talk, 'title'), get_tag_info(talk, 'subtitle'), iconImage='defaultvideo.png')
		#li.setProperty('TotalTime', '3600')
		#log(str(get_tag_info(talk, 'persons')))

		info = {'genre'			:		get_tag_info(talk, 'track'),
				'year'			:		'2014',
				'director'		:		' / '.join(get_tag_info(talk, 'persons')),
				'writer'		:		' / '.join(get_tag_info(talk, 'persons')),
				'plot'			:		get_tag_info(talk, 'description'),
				'plotoutline'	:		get_tag_info(talk, 'abstract'),
				'title'			:		value + ' - ' + get_tag_info(talk, 'title'),
				'mpaa'			:		'FSK 0',
				'duration'		:		get_tag_info(talk, 'duration') + ':00',
				'studio'		:		'CCC',
				'tagline'		:		get_tag_info(talk, 'subtitle'),
				'aired'			:		parse_datetime_string(get_tag_info(talk, 'date')).strftime('%Y-%m-%d'),
				'credits'		:		' / '.join(get_tag_info(talk, 'persons')),
				'artist'		:		get_tag_info(talk, 'persons')
			}

		if get_tag_info(talk, 'optout') == 'true':
			info['tagline'] += ' - ' + loc(30008)

		if get_tag_info(talk, 'language') == 'de':
			info['tagline'] += ' - Deutsch'
		else:
			info['tagline'] += ' - English'
		
		li.setInfo('video', info)
		li.setThumbnailImage('defaultvideo.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=urls[key][translated][resolution], listitem=li)
	else:
		#log('Aktueller Talk in Saal ' + key + ': ' +  'none' + '\tURL: ' + urls[key][translated][resolution])
		li = xbmcgui.ListItem(value + ' - ' + loc(30007), iconImage='defaultvideo.png')
		li.setInfo('video', {'title' : value + ' - ' + loc(30007)})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=urls[key][translated][resolution], listitem=li)
xbmcplugin.endOfDirectory(addon_handle)
