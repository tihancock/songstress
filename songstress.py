#! /usr/bin/python

import os, fnmatch, sys, urllib, simplejson, eventful, smtplib, unicodedata, json
from mutagen.easyid3 import EasyID3
from argparse import ArgumentParser
from email.mime.text import MIMEText
from datetime import datetime


parser = ArgumentParser()
parser.add_argument('dir', metavar='<directory>',
                    help='The directory to scan for artist names')
parser.add_argument('--email', dest='email', metavar='<email address>',
                    help='An email address to send the results to')
parser.add_argument('--known-events-file', dest='known_file_path', metavar='<file>',
                    help='A file to store details of already discovered events in')

args = parser.parse_args()

known_events = {}
if args.known_file_path is not None and os.path.exists(args.known_file_path):
  with open(args.known_file_path) as known_file:
     known_events = json.load(known_file)

# Remove any events that have already passed
known_events = { k : v for k, v in known_events.iteritems() if datetime(strptime(v, '%y-%m-%d %H:%M:%S') > datetime.now()) }

matches = []
for root, dirnames, filenames in os.walk(args.dir):
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
results = ""

for a in artists:
    events = api.call('/events/search', q='title:"'+a+'"', l='London')
    try:
        if int(events['total_items']) > 0:
            e = events['events']['event'][0]

            if e['id'] in known_events:
                  continue

            results+=a+':\r\n'
            results+='%s at %s, starttime: %s\r\n%s\r\n' % (e['title'], e['venue_name'], e['start_time'],e['url'])
            results+='\r\n'

            known_events[e['id']] = e['start_time']
    except:
        pass

print results.encode('ascii', 'ignore')

if args.email is not None and len(results) > 0:
    sender = 'myconcertupdates@gmail.com'
    recipient = args.email

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.ehlo()
    
    session.login(sender,'R3s5h6pk2')
    
    headers = ["from: " + sender,
               "subject: Concert Update",
               "to: " + recipient,
               "mime-version: 1.0",
               "content-type: text/plain"]
    headers = "\r\n".join(headers)

    session.sendmail(sender, recipient, headers + "\r\n\r\n" + results.encode('ascii', 'ignore'))

if args.known_file_path is not None:
    known_s = json.dumps(known_events)
    with open(args.known_file_path,'w') as known_file:
        known_file.write(known_s)
