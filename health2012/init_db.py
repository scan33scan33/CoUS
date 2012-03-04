import os
import csv
import sys
try:
    from mine.models import Item
except:
    pass

if __name__ == "__main__":
    os.system('rm CoUS.sqlite3')
    os.system('echo "no" | ./manage.py syncdb')
    os.system('echo "import init_db" | ./manage.py shell')
    sys.exit(0)


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
        #item.topic = row[0]
        item.qtopic = row[0]
        item.attr = row[1]
        item.value = float(row[2])
        item.save() 
        print row
    except:
        print "Error"
os.system('rm result.dat')

