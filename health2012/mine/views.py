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
from mine.models import URLtopic
from itertools import imap
from xml.etree.ElementTree import parse


genderlist = ['Male','Female']
racelist = ["American Indian","Asian or Pacific Islander","Black","Hispanic (of any race)","Non-Hispanic White"]
edulist = ["Less than High School","High School Graduate/Some College/Associate's Degree","Bachelor's Degree or More"]

genderprior = {genderlist[0] : 1.01, genderlist[1] : 0.97}
eduprior = {edulist[0] : 1.05, edulist[1] : 1, edulist[2] : 0.95}

# utility functions
# Compute correlation
def pearson(x, y):
    # Assume len(x) == len(y)
    if len(x) <= 8 or len(y) <= 8: return 0
   
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

def cmp_by_last2(a,b):
    return a[-2] > b[-2] and -1 or 1 


def retrieve_bars(yourstate,yourrace,yourgender,youredu,itsstate,itsrace,itsgender,itsedu):
    # Get bars
    # raceprior , eduprior
    itemsA = Item.objects.filter(state = yourstate,attr = yourrace).values_list('topic','value')
    itemsA = map(lambda x: [x[0],x[1]*genderprior[yourgender]*eduprior[youredu]],itemsA)
    itemsB = Item.objects.filter(state = itsstate,attr = itsrace).values_list('topic','value')
    itemsB = map(lambda x: [x[0],x[1]*genderprior[itsgender]*eduprior[itsedu]],itemsB)
    bars = skew_merge(itemsA,itemsB)
    bars = sorted(bars,cmp_by_last2)
    return bars

def retrieve_subfocuses(yourrace,yourfocus): 
    subfocuses = Item.objects.filter(attr = yourrace, subtopic = yourfocus).values_list('state','value') 
    subfocuses = map(lambda x : list(x),subfocuses)
    return subfocuses

def retrieve_corrtable(yourtopic,yourattr):
    m = {}
    m["Access to Quality Health Services"] = "access"
    m["Disability and Secondary Conditions"] = "disability"
    m["Heart Disease and Stroke"] = "heart"
    m["HIV"] = "hiv"
    m["Injury and Violence Prevention"] = "violen"
    m["Maternal Infant and Child Health"] = "infant"
    m["Mental Health and Mental Disorders"] = "mental"
    m["Physical Activity and Fitness"] = "physical"
    m["Respiratory Diseases"] = "respir"
    m["Substance Abuse"] = "abuse"
    m["Cancer"] =  "cancer"
    m["Diabetes"] = "diabetes"
    query = m[yourtopic]

    width = 3
#    height = 1
    arrs = Item.objects.all().values_list('qtopic','attr','value')
   

    attr2value = {}
    for i in range(len(arrs)) :
        if query  in arrs[i][0].lower(): 
            attr2value[arrs[i][1]] = arrs[i][2]
 
    alls = Item.objects.all().values_list('qtopic','attr','value')
    topic_arrs_map = {} # used later
    for arr in alls:
        if len(arr[0]) == 0: continue
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
        if query in topic_.lower() and query != topic_.lower():
            topics_score.append([topic_,99])
        else:
            topics_score.append([topic_,pearson(arrA,arrB)])
    topics_score = sorted(topics_score,cmp_by_last)
    print topics_score[0:10]
    print topics_score[-10:]
    postopics = []
    negtopics = []

    j = 0
    for i in range(10): 
        if j == width: break 
        topic = topics_score[i+1][0]
        try:
            utopic = list(URLtopic.objects.filter(topic = topic).values_list('url','shorttopic')[0])
            j += 1
        except:
            continue
        postopics.append(utopic)
    j = 0
    for i in range(10): 
        if j == width: break 
        topic = topics_score[-i-1][0]
        try:
            utopic = list(URLtopic.objects.filter(topic = topic).values_list('url','shorttopic')[0])
            j += 1
        except:
            continue
        negtopics.append(utopic)
    print "return",postopics,negtopics
    return postopics, negtopics


def index(request):
    IP_ADDR = request.META['REMOTE_ADDR']
    xml_grabber(IP_ADDR)
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    t = loader.get_template('mine/index.html')
    
    topiclist = Item.objects.values('topic').distinct() 
    subfocuslist = Item.objects.values('subtopic').distinct() 
    statelist = Item.objects.values('state').distinct() 
#    racelist = Item.objects.values('attr').distinct()
    topiclist = sorted([x[0] for x in  subfocuslist.values_list('topic')[1:]])
    subfocuslist = sorted([x[0] for x in  subfocuslist.values_list('subtopic')[1:]])
    statelist = sorted([x[0] for x in statelist.values_list('state')[1:]])
#    racelist = sorted([x[0] for x in racelist.values_list('attr')[1:]])

    yourgender = "Male"
    itsgender = "Female"

    youredu = edulist[-1]
    itsedu = edulist[-1]

    yourrace = "Hispanic (of any race)"# "Black or African American only"
    itsrace = "Non-Hispanic White"
    
    yourstate = "Connecticut"
    itsstate = "Louisiana"
    yourfocus = "1-1 Persons with health insurance"
    yourtopic = "HIV"

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


    bars = retrieve_bars(yourstate,yourrace,yourgender,youredu,itsstate,itsrace,itsgender,itsedu)
    subfocuses = retrieve_subfocuses(yourrace,yourfocus)
    postopics,negtopics = retrieve_corrtable(yourtopic,'')
    print "bars :" , bars

    c = Context({"yourstate":yourstate, "itsstate" : itsstate, "yourgender" : yourgender, "itsgender" : itsgender, "youredu" : youredu, "itsedu":itsedu, "yourrace": yourrace, "itsrace" : itsrace,'statelist' : statelist, 'racelist' : racelist, 'genderlist' : genderlist, 'edulist':edulist, "bars" : bars, "subfocuslist" : subfocuslist, "subfocuses" : subfocuses, "yourfocus" : yourfocus, "postopics" : postopics, "negtopics" : negtopics, "yourtopic" : yourtopic, "topiclist" : topiclist})
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

        print request.POST

        yourgender = request.POST['yourgender']
        youredu = request.POST['youredu']
        itsgender = request.POST['itsgender']
        itsedu = request.POST['itsedu']
        yourstate = request.POST['yourstate']
        yourrace = request.POST['yourrace']
        itsstate = request.POST['itsstate']
        itsrace = request.POST['itsrace']
        yourfocus = request.POST['yourfocus']
        yourtopic = request.POST['yourtopic']


        bars = retrieve_bars(yourstate,yourrace,yourgender,youredu,itsstate,itsrace,itsgender,itsedu)
        subfocuses = retrieve_subfocuses(yourrace,yourfocus)
        print "posp"
        postopics,negtopics = retrieve_corrtable(yourtopic,'')

        print "pos", postopics

        jsonSerializer = JSONSerializer()
        data = jsonSerializer.serialize([bars, subfocuses, postopics, negtopics])
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

def collaborators(request):
    return render_to_response('mine/collaborators.html')

def pre_populate(request):
    if request.method == 'POST':
        IP_ADDR = request.META['REMOTE_ADDR']
        d = xml_parser(IP_ADDR)
        if d is None:
            return HttpResponseNotFound()
        else:
            for key, val in d.iteritems():
                print key, " : ", val
        state = d["State"] 
        yourrace = "Non-Hispanic White"
        itsrace = "Asian or Pacific Islander"
        yourstate = state
        itsstate = state
        youredu = "Bachelor's Degree or More"
        itsedu = "Bachelor's Degree or More"
        yourgender = "Male"
        itsgender = "Female"
        yourfocus = "1-1 Persons with health insurance"

        bars = retrieve_bars(yourstate,yourrace,yourgender,youredu,itsstate,itsrace,itsgender,itsedu)
        subfocuses = retrieve_subfocuses(yourrace,yourfocus)
        yourtopic = bars[0][0]
        postopics,negtopics = retrieve_corrtable(yourtopic,'')

        youform_data = [yourstate,yourrace,yourgender,youredu,yourfocus,itsstate,itsrace,itsgender,itsedu,yourtopic]

        jsonSerializer = JSONSerializer()
        data = jsonSerializer.serialize([bars, subfocuses, postopics, negtopics,youform_data])
        return HttpResponse(data, mimetype="application/json")
        #return HttpResponse('T')
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
