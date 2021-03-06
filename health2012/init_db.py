import os
import csv
import sys
try:
    from mine.models import Item
    from mine.models import URLtopic
    from mine.models import Logo
except:
    pass

if __name__ == "__main__":
    os.system('rm CoUS.sqlite3')
    os.system('echo "no" | ./manage.py syncdb')
    os.system('echo "import init_db" | ./manage.py shell')
    sys.exit(0)


os.system('wget http://www.aiksee.com/cous/data/collaborators.csv')
csvReader = csv.reader(open('collaborators.csv', 'rb'), delimiter=',', quotechar='"')
for row in csvReader:
    print row
    item = Logo()
    item.name = row[0]
    item.url = row[1]
    item.attr = row[2]
    item.logopath = row[3]
    item.save() 
os.system('rm collaborators.csv')




os.system('wget http://www.aiksee.com/cous/data/url_topic.csv')
csvReader = csv.reader(open('url_topic.csv', 'rb'), delimiter=',')
for row in csvReader:
    try:
        item = URLtopic()
        #item.topic = row[0]
        item.url = row[0]
        item.topic = row[1]
        if len(row[2]) == 0: 
            item.shorttopic = row[1]
        else:
            item.shorttopic = row[2].strip()
        item.save()
        print row
    except:
        print "Error"
os.system('rm url_topic.csv')

# get datasets
# get lines and insert into database 
os.system('wget http://www.aiksee.com/cous/data/data.csv')
csvReader = csv.reader(open('data.csv', 'rb'), delimiter=',', quotechar='"')
for row in csvReader:
    try:
        item = Item()
        item.topic = row[0]
        item.qtopic = row[0]
        item.subtopic = row[1]
        item.state = row[2]
        item.attr = row[3]
        item.value = float(row[4])
        item.save()
        print row
    except:
        print "Error"
os.system('rm data.csv')



os.system('wget http://www.aiksee.com/cous/data/result.dat')
csvReader = csv.reader(open('result.dat', 'rb'), delimiter=',', quotechar='"')
for row in csvReader:
    try:
        item = Item()
        item.qtopic = row[0]
        if row[0][0].isupper():
            item.topic = row[0]
#        if row[0][0].isupper() and len(row[0]) < 20 and float(row[2]) < 3:
        if "vaccin" in row[0] and len(row[0]) < 25 and float(row[2]) < 5:
            item.state = "Wildcard"
        item.attr = row[1]
        item.value = float(row[2])
        item.save() 
        print row
    except:
        print "Error"
os.system('rm result.dat')




