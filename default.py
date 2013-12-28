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

addon = xbmcaddon.Addon('plugin.video.c3')
addondir = xbmc.translatePath(addon.getAddonInfo('profile'))
loc = addon.getLocalizedString
addon_handle = int(sys.argv[1])

def log(msg):
	with open(addondir + 'logfile.txt', 'a') as file:
		file.write("[" + time.strftime('%X') + "] " + msg + "\n")

parameters = urlparse.parse_qsl(sys.argv[2][1:])
parameters = dict(parameters)
log(str(parameters))

# xml stuff

response = urllib2.urlopen('http://events.ccc.de/congress/2013/Fahrplan/schedule.xml')
xml = response.read()
xmldoc = minidom.parseString(xml)
itemlist = xmldoc.getElementsByTagName('day')
for s in itemlist:
	if s.getAttribute('date') == time.strftime('%Y-%m-%d'):
		for i in s.childNodes:
			if i.nodeType == minidom.Node.ELEMENT_NODE:
				log(i.getAttribute('name'))


#stable
    
halls = { '1' : loc(30001), '2' : loc(30002), 'g' : loc(30003), '6' : loc(30004) }
trans = { 'native' : loc(30005), 'translated' : loc(30006) }

urls = { '1' : { 'native' :
					[['HD', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_native_hd'],
					['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_native_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_native_lq']],
				'translated' :
					[['HD', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_translated_hd'],
					['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_translated_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal1_translated_lq']]
			},
		'2' : { 'native' :
					[['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_native_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_native_lq']],
				'translated' :
					[['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_translated_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal2_translated_lq']]
			},
		'g' : { 'native' :
					[['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_native_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_native_lq']],
				'translated' :
					[['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_translated_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saalg_translated_lq']]
			},
		'6' : { 'native' :
					[['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_native_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_native_lq']],
				'translated' :
					[['HQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_translated_hq'],
					['LQ', 'rtmp://rtmp-hd.streaming.media.ccc.de:1935/stream/saal6_translated_lq']]
			}
	}
	
if 'hall' not in parameters:
	for key, value in halls.iteritems():
		parameters = {'hall' : key}
		url = sys.argv[0] + '?' + urllib.urlencode(parameters)
		li = xbmcgui.ListItem(value, iconImage='defaultfolder.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
elif 'trans' not in parameters:
	for key, value in trans.iteritems():
		parameters = {'hall' : parameters['hall'], 'trans' : key}
		url = sys.argv[0] + '?' + urllib.urlencode(parameters)
		li = xbmcgui.ListItem(value, iconImage='defaultfolder.png')
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
else:
	for i in urls[parameters['hall']][parameters['trans']]:
		li = xbmcgui.ListItem(i[0], iconImage='defaultvideo.png')
		li.setInfo('video', {'title' : halls[parameters['hall']] + ' - ' + trans[parameters['trans']] + ' (' + i[0] + ')'})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=i[1], listitem=li)
xbmcplugin.endOfDirectory(addon_handle)
