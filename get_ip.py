import urllib
import re
import connect

f = urllib.urlopen("http://www.canyouseeme.org/")
html_doc = f.read()
f.close()
m = re.search('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',html_doc)
print m.group(0)
db = connect.getConnect()
r = db.cursor()

r.execute('''INSERT INTO ip (adr) VALUES (%s)''', m.group(0))
db.commit()
