import sys
import os
import urllib
from xml.etree.ElementTree import parse
 
def main():
    try:
        IP = sys.argv[1]
    except IndexError:
        sys.exit('Pass in only one argument')
    except e:
        sys.exit(e)

    PREFIX_URL = "https://azure.geodataservice.net/GeoDataService.svc/GetUSDemographics?includecrimedata=true&ipaddress="
    URL = PREFIX_URL + IP
    PATH = os.path.dirname(os.path.abspath(__file__)) + '/xml_cache/' + IP + '.xml'

    try:
        file = open(PATH, 'r')
    except IOError, e:
        l = urllib.urlopen(URL)
        f = open(PATH, 'w')
        f.write(l.read())
        f.close()
        file = open(PATH, 'r')
    except e:
        print e

    t = parse(file)
    file.close()

    r = t.getroot()
    elems = r.getchildren()[0]
    d = {}
    for elem in elems:
        tag = elem.tag
        val = elem.text
        tag = tag.replace('{http://schemas.microsoft.com/ado/2007/08/dataservices}', '')
        d[tag] = val
    for key, val in d.iteritems():
        print key, ":", val

if __name__ == "__main__":
    main()
