import os
import re
import csv
import urllib
import subprocess
from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, loader
from django import forms
from django.shortcuts import render_to_response
from json_utils import JSONSerializer
from mine.models import Item
from itertools import imap
from xml.etree.ElementTree import parse

# utility functions
# Compute correlation
def pearson(x, y):
    # Assume len(x) == len(y)
    if len(x) <= 10 or len(y) <= 10: return 0
    # Normalize
    sumarrA = sum(map(lambda z: abs(z), (x)))   
    sumarrB = sum(map(lambda z: abs(z), (y)))   
    if sumarrA == 0 or sumarrB == 0: return 0
    x = map(lambda z: z / sumarrA, x)
    y = map(lambda z: z / sumarrB, y)
    
    n = len(x)
    sum_x = float(sum(x))
    sum_y = float(sum(y))
    sum_x_sq = sum(map(lambda x: pow(x, 2), x))
    sum_y_sq = sum(map(lambda x: pow(x, 2), y))
    psum = sum(imap(lambda x, y: x * y, x, y))
    num = psum - (sum_x * sum_y/n)
    den = pow(max((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n),1e-9), 0.5)
    if den == 0: return 0
    return num / den


# list : (str,value), merge by str... 
def skew_merge(listA,listB):
    listC = []
    keys = list(set([x[0] for x in listA] + [x[0] for x in listB]))
    for key in keys:
        valueA = 0.0
        valueB = 0.0
        for pair in listA:
            if pair[0] == key : valueA = pair[1]
        for pair in listB:
            if pair[0] == key : valueB = pair[1]
        listC.append([key,valueA,valueB])
    return listC

def cmp_by_last(a,b):
    return a[-1] > b[-1] and -1 or 1 

def retrieve_bars(yourstate,yourrace,itsstate,itsrace):
    # Get bars
    itemsA = Item.objects.filter(state = yourstate,attr = yourrace).values_list('topic','value')
    itemsB = Item.objects.filter(state = itsstate,attr = itsrace).values_list('topic','value')
    bars = skew_merge(itemsA,itemsB)
    return bars

def retrieve_subfocuses(yourrace,yourfocus): 
    subfocuses = Item.objects.filter(attr = yourrace, subtopic = yourfocus).values_list('state','value') 
    subfocuses = map(lambda x : list(x),subfocuses)
    return subfocuses

def retrieve_corrtable(yourtopic,yourattr):
    width = 5
#    height = 1

    arrs = Item.objects.filter(topic = yourtopic).values_list('attr','value')
    print arrs
    attr2value = {}
    for i in range(len(arrs)) :
        attr2value[arrs[i][0]] = arrs[i][1]
 
    alls = Item.objects.all().values_list('topic','attr','value')
    topic_arrs_map = {} # used later
    for arr in alls:
        if not topic_arrs_map.has_key(arr[0]) :
            topic_arrs_map[arr[0]] = [[arr[1],arr[2]]]
        else :
            topic_arrs_map[arr[0]].append([arr[1],arr[2]])

    topics_score = []
    for topic_ in topic_arrs_map.keys() :
        arrs = topic_arrs_map[topic_] 
        arrA = []
        arrB = []
        for arr in arrs:
            if attr2value.has_key(arr[0]):
                arrA.append(arr[1])    
                arrB.append(attr2value[arr[0]])
   #     print arrA,arrB
        topics_score.append([topic_,pearson(arrA,arrB)])
    topics_score = sorted(topics_score,cmp_by_last)
    print topics_score[0:5]
    postopics = []
    negtopics = []
    for i in range(width): postopics.append(topics_score[i][0])
    for i in range(width): negtopics.append(topics_score[-i][0])

    return postopics, negtopics


    arrs = Item.objects.filter(attr = yourattr).values_list('topic','value')
    topic2value = {}
    for i in range(len(arrs)) :
        topic2value[arrs[i][0]] = arrs[i][1]
 
    alls = Item.objects.all().values_list('attr','topic','value')
    attr_arrs_map = {} # used later
    for arr in alls:
        if not attr_arrs_map.has_key(arr[0]) :
            attr_arrs_map[arr[0]] = [[arr[1],arr[2]]]
        else :
            attr_arrs_map[arr[0]].append([arr[1],arr[2]])

    attrs_score = []
    for attr_ in attr_arrs_map.keys() :
        arrs = attr_arrs_map[attr_] 
        arrA = []
        arrB = []
        for arr in arrs:
            if topic2value.has_key(arr[0]):
                arrA.append(arr[1])    
                arrB.append(topic2value[arr[0]])
        attrs_score.append([attr_,pearson(arrA,arrB)])
    attrs_score = sorted(attrs_score,cmp_by_last)
    attrs = []
    for i in range(height): attrs.append(attrs_score[i][0])
    for i in range(height): attrs.append(attrs_score[-i][0])

    corrtable = []
#    for attr in attrs:
#        row = []
#        for topic in topics:
#            value = Item.objects.filter(attr = attr,topic = topic).values_list('value')
#            if len(value) > 0:
#                row.append(value[0][0])
#            else :
#                row.append(0)
#        corrtable.append(row)

<<<<<<< HEAD
    return attrs,topics,corrtable
=======
#    print corrtable 

>>>>>>> ee8d8ad59db3663961b46b191ca801f4206bcc5c


def index(request):
    postopics,negtopics = retrieve_corrtable('HIV','White')
    print '\n'.join(postopics)
    print '\n'.join(negtopics)
    
    IP_ADDR = request.META['REMOTE_ADDR']
    xml_grabber(IP_ADDR)
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    t = loader.get_template('mine/index.html')
    statelist = ['-----','NY','NJ']
    racelist = ['-----','Asian','Native American']
    genderlist = ['-----','Male','Female']
    edulist = ['-----','A','B','C']
    
    
    subfocuslist = Item.objects.values('subtopic').distinct() 
    statelist = Item.objects.values('state').distinct() 
    racelist = Item.objects.values('attr').distinct()
    subfocuslist = sorted([x[0] for x in  subfocuslist.values_list('subtopic')[1:]])
    statelist = sorted([x[0] for x in statelist.values_list('state')[1:]])
    racelist = sorted([x[0] for x in racelist.values_list('attr')[1:]])

    yourgender = ""
    itsgender = ""

    youredu = ""
    itsedu = ""

    yourrace = "Hispanic or Latino"# "Black or African American only"
    itsrace = "White"
    
    yourstate = "Connecticut"
    itsstate = "Louisiana"
    yourfocus = "1-1 Persons with health insurance (aged under 65 years)"

    #Check if it is just change #TODO
    try:
        yourstate = request.POST["yourstate"]
    except:
        pass
    try:
        itsstate = request.POST["itsstate"]
    except:
        pass

    try:
        yourgender = request.POST["yourgender"]
    except:
        pass
    try:
        itsgender = request.POST["itsgender"]
    except:
        pass

    try:
        youredu = request.POST["youredu"]
    except:
        pass
    try:
        itsedu = request.POST["itsedu"]
    except:
        pass

    try:
        yourrace = request.POST["yourrace"]
    except:
        pass
    try:
        itsrace = request.POST["itsrace"]
    except:
        pass
    try:
        yourfocus = request.POST["yourfocus"]
    except:
        pass


    bars = retrieve_bars(yourstate,yourrace,itsstate,itsrace)
    subfocuses = retrieve_subfocuses(yourrace,yourfocus)

    c = Context({"yourstate":yourstate, "itsstate" : itsstate, "yourgender" : yourgender, "itsgender" : itsgender, "youredu" : youredu, "itsedu":itsedu, "yourrace": yourrace, "itsrace" : itsrace,'statelist' : statelist, 'racelist' : racelist, 'genderlist' : genderlist, 'edulist':edulist, "bars" : bars, "subfocuslist" : subfocuslist, "subfocuses" : subfocuses, "yourfocus" : yourfocus, "postopics" : postopics, "negtopics" : negtopics})
    return HttpResponse(t.render(c))

def field_filter(request):
    if request.method == 'POST':
        field = request.POST['field']
        val = request.POST['val']
        return HttpResponse('field_filter: Received!')
    return HttpResponse('Incorrect Http Method.')

def ajax_handler(request):
    if request.method == 'POST':
        subfocuslist = Item.objects.values('subtopic').distinct() 
        statelist = Item.objects.values('state').distinct() 
        racelist = Item.objects.values('attr').distinct()
 
        yourstate = request.POST['yourstate']
        yourrace = request.POST['yourrace']
        itsstate = request.POST['itsstate']
        itsrace = request.POST['itsrace']
        yourfocus = request.POST['yourfocus']


        bars = retrieve_bars(yourstate,yourrace,itsstate,itsrace)
        subfocuses = retrieve_subfocuses(yourrace,yourfocus)

        jsonSerializer = JSONSerializer()
        data = jsonSerializer.serialize([bars, subfocuses])
        c = Context({"bars":bars, "subfocuses":subfocuses})
        return HttpResponse(data, mimetype="application/json")
    return HttpResponse('Incorrect Http Method.')

#The function is useless
def display(request):
    t = loader.get_template('mine/display.html')
    
    counter = [0]
    relnames = ["You"]

    names = []
    names = [request.POST["name"]]
    for i in range(1,100):
        try:
            name = request.POST["name" + str(i)]
            counter.append(i)
            names.append(name)
            #relnames.append("Frined" + str(i)]
        except:
            pass #FIXME
    
    states = [request.POST["State"]]
    for i in range(1,100):
        try:
            state = request.POST["State" + str(i)]
            states.append(state)
        except:
            pass #FIXME

    genders = [request.POST["Gender"]]
    for i in range(1,100):
        try:
            gender = request.POST["Gender" + str(i)]
            genders.append(gender)
        except:
            pass #FIXME

    edus = [request.POST["Education Level"]]
    for i in range(1,100):
        try:
            edu = request.POST["Education Level" + str(i)]
            edus.append(edu)
        except:
            pass #FIXME

 
    races = [request.POST["Race"]]
    for i in range(1,100):
        try:
            race = request.POST["Race" + str(i)]
            races.append(race)
        except:
            pass #FIXME
 
    alldata = [relnames,names,states,races,genders,edus] 
    alldatat = map(lambda x: list(x),zip(*alldata))
    
    c = Context({"relnames":relnames , "names" : names,"genders" : genders, "edus" : edus, "races" : races, "alldatat" : alldatat, "counter" : counter})
    return HttpResponse(t.render(c))

def about(request):
    return render_to_response('mine/about.html')

def contact(request):
    return render_to_response('mine/contact.html')

def pre_populate(request):
    if request.method == 'POST':
        IP_ADDR = request.META['REMOTE_ADDR']
        d = xml_parser(IP_ADDR)
        if d is None:
            return HttpResponseNotFound()
        for key, val in d.iteritems():
            print key, " : ", val
        #jsonSerializer = JSONSerializer()
        #data = jsonSerializer.serialize([bars, subfocuses])
        return HttpResponse('T')
    return HttpResponse('Incorrect Http Method.')

def xml_grabber(IP_ADDR):
    program_name = 'python'
    PATH = os.path.dirname(os.path.abspath(__file__)) + '/xml_grabber.py'
    argument = [PATH, IP_ADDR]
    command = [program_name]
    command.extend(argument)
    subprocess.Popen(command)

def xml_parser(IP_ADDR):
    PATH = os.path.dirname(os.path.abspath(__file__)) + '/xml_cache/' + IP_ADDR + '.xml'

    try:
        file = open(PATH, 'r')
    except IOError, e:
        print e
        l = urllib.urlopen(URL)
        f = open(PATH, 'w')
        f.write(l.read())
        f.close()
        file = open(PATH, 'r')
    except:
        print "In View.xml_parser: unexcepted error"

    t = parse(file)
    file.close()

    try:
        r = t.getroot()
        elems = r.getchildren()[0]
        d = {}
        for elem in elems:
            tag = elem.tag
            val = elem.text
            tag = tag.replace('{http://schemas.microsoft.com/ado/2007/08/dataservices}', '')
            d[tag] = val
        return d
    except IndexError, e:
        print e
        return None
