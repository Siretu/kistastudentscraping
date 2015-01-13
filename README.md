# kistastudentscraping
Continually scrapes kistastudentbostader.se for student apartments and mails you when new apartments come up.


To use, make sure you create a file called email_settings.py with the following rows:
username = 'myemail@gmail.com'
password = 'mypassword123'
server = 'smtp.gmail.com'
port = 587

Change the username, password, server and port as you want.

Seen apartments will be saved in the apartments text file and wont be reported if they're seen the next time.

If run without parameters it will look for new apartments every five minutes. If you supply the -s flag, it will only look once and then exit (useful if you prefer using a cron service or similar).