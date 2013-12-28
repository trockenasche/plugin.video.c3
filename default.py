import os
import sys
import xbmc
import xbmcaddon
import urllib
import urllib2
import urlparse
import xbmcplugin
import xbmcgui
import time
from xml.dom import minidom
from datetime import datetime, timedelta

addon = xbmcaddon.Addon('plugin.video.c3')
addondir = xbmc.translatePath(addon.getAddonInfo('profile'))
if not os.path.exists(addondir):
	os.makedirs(addondir)
loc = addon.getLocalizedString
addon_handle = int(sys.argv[1])

resolution = addon.getSetting('resolution') #LQ - 0; HQ - 1; HD - 2
translated = addon.getSetting('translated') #original - 0; translated - 1

def log(msg):
	with open(addondir + 'logfile.txt', 'a') as file:
		file.write("[" + time.strftime('%X') + "] " + msg + "\n")

parameters = urlparse.parse_qsl(sys.argv[2][1:])
parameters = dict(parameters)

if 'hall' not in parameters:
	response = urllib2.urlopen('http://events.ccc.de/congress/2013/Fahrplan/schedule.xml')
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
		if s.getAttribute('date') == time.strftime('%Y-%m-%d'):
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

#stable
    
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
	
#if 'hall' not in parameters:
for key, value in halls.iteritems():
	talk = find_current(xml, 'Saal ' + key)
	if key != '1' and resolution == '2':
		resolution = '1'
	if talk is not False:
		log('Aktueller Talk in Saal ' + key + ': ' +  talk.getElementsByTagName('title').item(0).firstChild.data + '\tURL: ' + urls[key][translated][resolution])
		li = xbmcgui.ListItem(value + ' - ' + talk.getElementsByTagName('title').item(0).firstChild.data, iconImage='defaultvideo.png')
		li.setInfo('video', {'title' : value + ' - ' + talk.getElementsByTagName('title').item(0).firstChild.data})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=urls[key][translated][resolution], listitem=li)
	else:
		log('Aktueller Talk in Saal ' + key + ': ' +  'none' + '\tURL: ' + urls[key][translated][resolution])
		li = xbmcgui.ListItem(value + ' - ' + loc(30007), iconImage='defaultvideo.png')
		li.setInfo('video', {'title' : value + ' - ' + loc(30007)})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=urls[key][translated][resolution], listitem=li)


	'''for key, value in halls.iteritems():
		parameters = {'hall' : key}
		url = sys.argv[0] + '?' + urllib.urlencode(parameters)
		li = xbmcgui.ListItem(value, iconImage='defaultfolder.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)'''
'''elif 'trans' not in parameters:
	for key, value in trans.iteritems():
		parameters = {'hall' : parameters['hall'], 'trans' : key}
		url = sys.argv[0] + '?' + urllib.urlencode(parameters)
		li = xbmcgui.ListItem(value, iconImage='defaultfolder.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
else:
	for i in urls[parameters['hall']][parameters['trans']]:
		li = xbmcgui.ListItem(i[0], iconImage='defaultvideo.png')
		li.setInfo('video', {'title' : halls[parameters['hall']] + ' - ' + trans[parameters['trans']] + ' (' + i[0] + ')'})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=i[1], listitem=li)'''
xbmcplugin.endOfDirectory(addon_handle)
