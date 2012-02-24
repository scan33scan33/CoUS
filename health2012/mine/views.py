# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django import forms
from django.shortcuts import render_to_response
import re
import csv

def index(request):
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    t = loader.get_template('mine/index.html')
    statelist = ['-----','NY','NJ']
    racelist = ['-----','Asian','Native American']
    genderlist = ['-----','Male','Female']
    edulist = ['-----','A','B','C']
#    attrmap = {'State': statelist,'Race': racelist,'Gender':genderlist,'Education Level':edulist}
    
    arrs = []
#    spamReader = csv.reader(open('/home/minghen/django/health2012/media/CountingOnUSData.csv', 'rb'), delimiter=',', quotechar='"')
    spamReader = csv.reader(open('/home/minghen/django/health2012/media/data.csv', 'rb'), delimiter=',', quotechar='"')
    for row in spamReader:
        arrs.append(row)
    #arrs = map(lambda x : re.sub('"','',x).strip().split(','),open('/home/minghen/django/health2012/media/CountingOnUSData.csv').readlines())
    dbmap = {"topic" : 0, "sub" : 1, "state" : 2, "category" : 3}
    nbar = 5
    arrst = zip(*arrs)
    statelist = sorted(list(set((arrst[dbmap["state"]]))))
    racelist = sorted(list(set((arrst[dbmap["category"]])).difference(set(["Male","Female","At least some college","High school graduate","Less than high school"]))))[8:]
    subfocuslist = sorted(list(set((arrst[dbmap["sub"]]))))

#    if request.method == 'POST':

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

    print "before bars"
    bars = []
    youmap = {}
    for arr in arrs: 
        if arr[dbmap["state"]] == yourstate and arr[dbmap["category"]] == yourrace:
            if not youmap.has_key(arr[dbmap["topic"]]):
                youmap[arr[dbmap["topic"]]] = len(bars)
                bars.append([arr[dbmap["topic"]] ,str(arr[-1])])
    print "bars:", bars
    k = 0
    for arr in arrs:
        k += 1
        if arr[dbmap["state"]] == itsstate and arr[dbmap["category"]] == itsrace:
            if youmap.has_key(arr[dbmap["topic"]]):
                if len(bars[youmap[arr[dbmap["topic"]]]]) == 2:
                    bars[youmap[arr[dbmap["topic"]]]].append(str(arr[-1]))
            else:
                if not youmap.has_key(arr[dbmap["topic"]]):
                    youmap[arr[dbmap["topic"]]] = len(bars)
                    bars.append([arr[dbmap["topic"]] , "0", str(arr[-1])])
    print "bars2:", bars
    for bar in bars:
        print len(bar)
        if len(bar) == 2:
            bar.append("0")
    #bars = sort(bars,cmpfunc)
    if len(bars) > 7: bars = bars[:7]
    
    #def cmpfunc(a,b):
     #   aa = 1
     #   bb = 1
     #   if a[1] == "0" or a[2] == "0": aa =0
     #   if b[1] == "0" or b[2] == "0": bb =0
     #   return a < b
    #sort(bars,cmpfunc)
#        for arr in arrs: 
#            if arr[dbmap["state"]] == yourstate and arr[dbmap["category"]] == yourrace:
#               yourscore = str(arr[-1])
#               youmap[arr[dbmap["topic"]]] = len(bars)
#               bars.append([arr[dbmap["topic"]] ,str(arr[-1])])
    print "before"
    subfocuses = []
    for arr in arrs: 
        if arr[dbmap["sub"]] == yourfocus and arr[dbmap["category"]] == yourrace:
            subfocuses.append([arr[dbmap["state"]],str(arr[-1])])
    print "subfocuses : ",subfocuses 


    #Map Data by Current State %TODO

    print "bars:", bars
    c = Context({"yourstate":yourstate, "itsstate" : itsstate, "yourgender" : yourgender, "itsgender" : itsgender, "youredu" : youredu, "itsedu":itsedu, "yourrace": yourrace, "itsrace" : itsrace,'statelist' : statelist, 'racelist' : racelist, 'genderlist' : genderlist, 'edulist':edulist, "bars" : bars, "subfocuslist" : subfocuslist, "subfocuses" : subfocuses, "yourfocus" : yourfocus})
    return HttpResponse(t.render(c))








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
