#! /usr/bin/python

import os, fnmatch, sys, urllib, simplejson, eventful, smtplib, unicodedata
from mutagen.easyid3 import EasyID3
from argparse import ArgumentParser
from email.mime.text import MIMEText


parser = ArgumentParser()
parser.add_argument('dir', metavar='<directory>',
                    help='The directory to scan for artist names')
parser.add_argument('--email', dest='email', metavar='<email address>',
                    help='An email address to send the results to')

args = parser.parse_args()

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
            results+=a+':\r\n'
            results+='%s at %s, starttime: %s\r\n%s\r\n' % (e['title'], e['venue_name'], e['start_time'],e['url'])
            results+='\r\n'  
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
