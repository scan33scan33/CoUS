import os
import re
import csv
import urllib
import subprocess
from django.http import HttpResponse
from django.template import Context, loader
from django import forms
from django.shortcuts import render_to_response
from json_utils import JSONSerializer
from mine.models import Item
from xml.etree.ElementTree import parse

# utility function
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

def index(request):
    IP_ADDR = request.META['REMOTE_ADDR']
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
    print subfocuses

    print subfocuses
    c = Context({"yourstate":yourstate, "itsstate" : itsstate, "yourgender" : yourgender, "itsgender" : itsgender, "youredu" : youredu, "itsedu":itsedu, "yourrace": yourrace, "itsrace" : itsrace,'statelist' : statelist, 'racelist' : racelist, 'genderlist' : genderlist, 'edulist':edulist, "bars" : bars, "subfocuslist" : subfocuslist, "subfocuses" : subfocuses, "yourfocus" : yourfocus})
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
    print alldata
    
    c = Context({"relnames":relnames , "names" : names,"genders" : genders, "edus" : edus, "races" : races, "alldatat" : alldatat, "counter" : counter})
    return HttpResponse(t.render(c))

def about(request):
    program_name = 'python'
    PATH = os.path.dirname(os.path.abspath(__file__)) + '/xml_grabber.py'
    argument = [PATH, '108.0.9.87']

    command = [program_name]
    command.extend(argument)

    subprocess.Popen(command)
    return render_to_response('mine/about.html')

def contact(request):
    return render_to_response('mine/contact.html')

