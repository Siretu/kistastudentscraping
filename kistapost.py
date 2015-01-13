from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from time import sleep
import datetime
import urllib
import urllib2
import json
import smtplib
import sys
import traceback
import email_settings

SAVED_APARTMENTS = "apartments.txt"

def create_app_file():
  f = open(SAVED_APARTMENTS, 'w')
  f.write("[]")
  f.close()

def self_mail(id):
  mail(email_settings.username,"Kista: New apartment available","There's a new apartment available in kista. It has the ID %s" % id)

def mail(email, subject, message):
  gmail_username = email_settings.username
  recipients = email

  msg = MIMEText(message)
  msg['Subject'] = subject
  msg['From'] = gmail_username
  msg['To'] = recipients
  msg = msg.as_string()

  session = smtplib.SMTP(email_settings.server, email_settings.port, timeout=10)
  session.ehlo()
  session.starttls()
  session.login(gmail_username, email_settings.password)
  session.sendmail(gmail_username, recipients, msg)
  session.quit()

def retrieve_source():
  url = "http://minasidor.kistastudentbostader.se/portal/WebForm/wfTorg.aspx?Mode=both&TorgID=1&SecurityToken=xPYLdrtKXwSnmDu2a75v6A%3d%3d"

  headers = {"Host" : "minasidor.kistastudentbostader.se",
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language" : "sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding" : "gzip, deflate",
            "Referer" : "http://minasidor.kistastudentbostader.se/portal/WebForm/wfTorg.aspx?Mode=both&TorgID=1&SecurityToken=xPYLdrtKXwSnmDu2a75v6A%3d%3d",
            "Cookie" : "__utma=216670476.1343914320.1390693422.1390693422.1402332739.2; __utmz=216670476.1390693422.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=216670476; ASP.NET_SessionId=hapv1qfjbq5kmwquxf5qox30",
            "Connection" : "keep-alive",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Content-Length" : "928"}

  data = "__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwUKMTk1MzY5Mjc5OA8WCB4GVG9yZ0lEBQExHgRNb2RlBQRib3RoHghTZWxLb3R5cGQeCVNlbE9tcmFkZWQWAgIBD2QWCAIBDw8WAh4EVGV4dAUfU3R1ZGVudGzDpGdlbmhldGVyIHDDpSBwb3J0YWxlbmRkAgMPDxYCHgdWaXNpYmxlaGRkAgUPDxYCHwQFK1RvcmcgZsO2ciBmw7ZybWVkbGluZyBhdiBzdHVkZW50bMOkZ2VuaGV0ZXJkZAIHD2QWBAIBD2QWAgIBDxAPFgYeDURhdGFUZXh0RmllbGQFBE5hbW4eDkRhdGFWYWx1ZUZpZWxkBQhPbXJhZGVJRB4LXyFEYXRhQm91bmRnZBAVBAgtIEFsbGEgLRBTdHVkZW50Ym9zdMOkZGVyCFNrYWxob2x0Dktpc3RhIEdhbGxlcmlhFQQBJQMxLTEDMS0yAzEtMxQrAwRnZ2dnZGQCAw9kFgICAQ8QDxYGHwYFCUtvVHlwTmFtbh8HBQdLb1R5cElEHwhnZBAVBQgtIEFsbGEgLQlMw6RnZW5oZXQGR2FyYWdlD1BhcmtlcmluZ3NwbGF0cwVMb2thbBUFASUBMQEyATMBNBQrAwVnZ2dnZ2RkZFQbSkURkLZXeAj2YDKubAqWs%2Bwf&__EVENTVALIDATION=%2FwEWDAL0m9%2BKCwLfreHhCQLg1LxBAvvD3usKAt6q%2BfYMAqWLndYKAtGKndYKAtCKndYKAtOKndYKAtKKndYKAuLukb0PAvO%2Bq6kFRVlfOw%2FHe3FFL5bATF8V0xZxpTg%3D&skapaintranmids=&ddlOmraden=%25&ddlKoTyper=1&btnVisaUrval=Visa+Urval"
  req = urllib2.Request(url, data, headers)
  response = urllib2.urlopen(req)
  the_page = response.read()
  return the_page

def parse_apartments(source):
  soup = BeautifulSoup(source)
  inp = soup.find_all(attrs={"type": "checkbox"})
  return [x['name'] for x in inp]


def get_saved_apartments():
  try:
    f = open(SAVED_APARTMENTS)
  except IOError:
    create_app_file()
    f = open(SAVED_APARTMENTS)
  text = f.read()
  aps = json.loads(text)
  return aps

def write_new_apartments(apps):
  f = open(SAVED_APARTMENTS, 'w')
  f.write(json.dumps(apps))
  f.close()

def find_apartments():
  print str(datetime.datetime.now()) + ": Searching"
  source = retrieve_source()
  apps = parse_apartments(source)
  old_apps = get_saved_apartments()

  found_new = False
  for app in apps:
    if app not in old_apps:
      found_new = True
      print "Found new apartment: %s" % app
      self_mail(app)
      old_apps.append(app)

  if found_new:
    write_new_apartments(old_apps)

if __name__ == "__main__":
  got_error = False
  got_second_error = False
  if len(sys.argv) > 1 and sys.argv[1] == "-s":
    find_apartments()
  else:
    while 1:
      try:
        find_apartments()
        print str(datetime.datetime.now()) + ": Sleeping"
        sleep(300)
      except (KeyboardInterrupt, SystemExit):
        raise
      except Exception, error:
        print traceback.format_exc()
        if not got_error:
          mail(email_settings.username,"Kista: Error occured",traceback.format_exc())
          got_error = True
        elif not got_second_error:
          mail(email_settings.username,"Kista: Fatal (Second) Error occured",traceback.format_exc())
          got_second_error = True



