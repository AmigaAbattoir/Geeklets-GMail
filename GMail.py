#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import urllib2
import subprocess
from xml.etree import ElementTree
from compiler.ast import TryExcept
from scipy.weave.c_spec import catchall_converter

# Get password from keychain
def getKeychainPassword(user):
	cmd = "security find-internet-password -l \"accounts.google.com\" -a \"" + user + "\" -w"
	proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in proc.stdout.readlines():
		p = line.rstrip()
	return p

# Simple wrapper function to encode the username & pass
def encodeUserData(user, password):
	return "Basic " + (user + ":" + password).encode("base64").rstrip()

##############################
if len(sys.argv) != 2:
	print "Call the script with the e-mail address of the user to list"

u=sys.argv[1]
p = getKeychainPassword(u)
url='https://mail.google.com/mail/feed/atom'

# create the request object and set some headers
req = urllib2.Request(url)
req.add_header('Accept', 'application/json')
req.add_header("Content-type", "application/x-www-form-urlencoded")
req.add_header('Authorization', encodeUserData(u, p))

try:
	response = urllib2.urlopen(req);
	document = ElementTree.parse( urllib2.urlopen(req) )
except urllib2.HTTPError as error:
	print "*** ERROR: HTTP Error " + str(error.code) + " - " + error.reason + " for user " + u + ". Please make sure your keychain password for \"accounts.google.com\" is correct! ***"

	exit(1)


document = ElementTree.parse( urllib2.urlopen(req) )

feed = document.getroot();
ns = "{http://purl.org/atom/ns#}"

bold = "\033[1m"
normal = "\033[0m"
dim = "\033[2m"

entries = feed.findall(ns+'entry')
numberOfEntries = len(entries)

if numberOfEntries==0:
	print "No unread messages for " + u
else:
	if numberOfEntries==1:
		print "1 unread mail message for " + u
	else:
		print str(numberOfEntries) + " unread mail messages for " + u + "\n"

	for entry in entries:
		title = entry.find(ns+'title').text
		summary = entry.find(ns+'summary').text
		fromName = entry.find(ns+'author').find(ns+'name').text
		fromEmail = entry.find(ns+'author').find(ns+'email').text
		print bold + title + normal + " from: " + fromName + "<" + fromEmail + ">"
		print summary + "\n"

