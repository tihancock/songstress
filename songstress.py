import os, fnmatch, sys, urllib, simplejson, eventful
from mutagen.easyid3 import EasyID3

matches = []
for root, dirnames, filenames in os.walk(sys.argv[1]):
  for filename in fnmatch.filter(filenames, '*'):
      matches.append(os.path.join(root, filename))

artists = set()

for f in matches:
    try:
        id3 = EasyID3(f)
        artists.add(str(id3['artist'][0]))
    except:
        pass

api = eventful.API('CdDcXHqV4qpNMq2F')

for a in artists:
    events = api.call('/events/search', q='music', l='London', keywords=a, date='Future')
    try:
        if len(events['events']) > 0:
            print a
        for event in events['events']['event']:
            print "%s at %s" % (event['title'], event['venue_name'])
    except:
        pass
