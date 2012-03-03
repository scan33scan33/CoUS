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
        file.close()
        return 
    except IOError, e:
        l = urllib.urlopen(URL)
        f = open(PATH, 'w')
        f.write(l.read())
        f.close()
    except:
        print "Unexcepted Error: ", sys.exc_info()[0]

if __name__ == "__main__":
    main()
