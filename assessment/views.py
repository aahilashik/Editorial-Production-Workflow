from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
import pyrebase
import os
import pdf2docx
import pandas as pd
import docxpy
import re, json
from googlesearch import search 
from copyleaks import CopyLeaks
import time


cLusername    = "email@copyleaks.com"
cLapiKey      = "00000000000000000000000000000000"

config = {
    "apiKey" : "AIzaSyC7fww5ra5nUCPh-V9h43UHQ9BTqBAqm2I",
    "authDomain" : "data-ingestion-aa201.firebaseapp.com",
    "databaseURL" : "https://data-ingestion-aa201.firebaseio.com",
    "projectId" : "data-ingestion-aa201",
    "storageBucket" : "data-ingestion-aa201.appspot.com",
    "messagingSenderId" : "966163523151",
    "appId" : "1:966163523151:web:02cfd4585f227153c6ac3a",
    "measurementId" : "G-0CFVXYRKRN",
    "serviceAccount": "data-ingestion-aa201-firebase-adminsdk-ys6d7-bdb6adb211.json"
}

firebase    = pyrebase.initialize_app(config)
storage     = firebase.storage()
database    = firebase.database()

copyLeaks = CopyLeaks(cLusername, cLapiKey)

data = {}
log_word_limit = 10

def get_text_from_docx(docx_path) : 
    file = docx_path
    text = docxpy.process(file)
    text = text.split()
    text = " ".join(text)
    return text

def google_search(query): 
    search_result = []
    for j in search(query, tld="co.in", num=2, stop=2, pause=2): 
        search_result.append(j)
    return search_result

def downloadPlag(request, refID):  
    if not request.user.is_authenticated:
        return redirect('/')  
    file_path = os.path.join("cache", str(refID)+"_report.pdf")
    storage.child("ingested data").child(refID).child("others").child(str(refID)+"_report.pdf").download(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        os.unlink(file_path)
        return response
    raise Http404
    
def downloadRnP(request, refID): 
    if not request.user.is_authenticated:
        return redirect('/')   
    file_path = os.path.join("cache", str(refID)+"_RnPlogs.xlsx")
    storage.child("ingested data").child(refID).child("others").child(str(refID)+"_RnPlogs.xlsx").download(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        os.unlink(file_path)    
        return response
    raise Http404

def downloadSpl(request, refID): 
    if not request.user.is_authenticated:
        return redirect('/')   
    file_path = os.path.join("cache", str(refID)+"_Spell_logs.xlsx")
    storage.child("ingested data").child(refID).child("others").child(str(refID)+"_Spell_logs.xlsx").download(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        os.unlink(file_path)
        return response
    raise Http404
    
def downloadLang(request, refID):    
    file_path = os.path.join("./upload/", str(refID), "others", str(refID)+"_Grammar_logs.xlsx")
    storage.child("ingested data").child(refID).child("others").child(str(refID)+"_Grammar_logs.xlsx").download(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        os.unlink(file_path)
        return response
    raise Http404

def spellLogs(request, refID): 
    if not request.user.is_authenticated:
        return redirect('/')
    global data
    
    fileUrl     = storage.child("ingested data").child("{}".format(refID)).child("others").child("{}_Spell_logs.xlsx".format(refID)).get_url(None)
    file1Url    = storage.child("ingested data").child("{}".format(refID)).child("others").child("{}_izeSpell_logs.xlsx".format(refID)).get_url(None)
    file2Url    = storage.child("ingested data").child("{}".format(refID)).child("others").child("{}_yzeSpell_logs.xlsx".format(refID)).get_url(None)
    file3Url    = storage.child("ingested data").child("{}".format(refID)).child("others").child("{}_Comma_logs.xlsx".format(refID)).get_url(None)
    
    print("\n\n", fileUrl, file1Url, file2Url, data.keys(), fileUrl, "\n\n")
    
    df = pd.read_excel(fileUrl)
    df.rename(columns = {'UK English':'UK', "US English":"US"}, inplace = True)
    df = df.fillna("- -")
    json_records = df.reset_index().to_json(orient ='records')
    DATA = []
    DATA = json.loads(json_records)
    
    df1 = pd.read_excel(file1Url)
    df1.rename(columns = {'UK English':'izUK', "US English":"izUS"}, inplace = True)
    
    df2 = pd.read_excel(file2Url)
    df2.rename(columns = {"Unnamed: 0":"Sno", 'UK English':'yzUK', "US English":"yzUS"}, inplace = True)
    
    resultDF = pd.concat([df1, df2], axis=1)
    resultDF = resultDF.fillna("- -")
    json_records = resultDF.reset_index().to_json(orient ='records')
    DATA2 = []
    DATA2 = json.loads(json_records)

    
    df4 = pd.read_excel(file3Url)
    df4.rename(columns = {'Context':'content'}, inplace = True)
    print(df4)
    # df4 = df.fillna("- -")
    json_records = df4.reset_index().to_json(orient ='records')
    DATA3 = []
    DATA3 = json.loads(json_records)

    context = {'dataFrame': DATA, "dataFrame2": DATA2, "dataFrame3": DATA3, "Ref_ID": refID}
    
    print(resultDF)
    return render(request, 'spellLogs.html', context) 
    
def grammLogs(request, refID): 
    if not request.user.is_authenticated:
        return redirect('/')
    global data
    
    fileUrl = storage.child("ingested data").child("{}".format(refID)).child("others").child("{}_Grammar_logs.xlsx".format(refID)).get_url(None)
    
    print("\n\n", data.keys(), fileUrl, "\n\n")
    
    df = pd.read_excel(fileUrl)
    df = df.fillna("- -")
#    df.rename(columns = {'UK English':'UK', "US English":"US"}, inplace = True)
    json_records = df.reset_index().to_json(orient ='records')
    DATA = []
    DATA = json.loads(json_records) 
    context = {'dataFrame': DATA, "Ref_ID": refID}
    
    print(df)
    return render(request, 'grammLogs.html', context) 
    
def logs(request, refID): 
    if not request.user.is_authenticated:
        return redirect('/')
    global data
    
    """
    pattern = r'“(.*?)”'
    text = data[str(refID)]["text"]
    
    df = pd.DataFrame(columns=["Chapter", "Type", "Title", "Count", "Source"])
    x = re.findall(pattern, text)

    chapters = ["Chapter 1"]
    sentences = []
    print()
    for chapter in chapters:
        for sent in x:
            if len(sent.split(" ")) > log_word_limit :
                df2 = {'Chapter': chapter, 'Type': 'Text', 'Title': sent, 'Count' : len(sent.split(" ")), 'Source':"\n".join(google_search(sent))} 
                df = df.append(df2, ignore_index = True)
    df.to_csv(os.path.join("./upload/", str(refID), "others", str(refID)+".csv"), header=["Chapter", "Content Type", "Illustration Title", "Count", "Source"])
    """

    fileUrl = storage.child("ingested data").child("{}".format(refID)).child("others").child("{}_RnPlogs.xlsx".format(refID)).get_url(None)
    
    print("\n\n", data.keys(), fileUrl, "\n\n")
    
    df = pd.read_excel(fileUrl)
    df.rename(columns = {'Content Type':'Type', "Illustration Title":"Title"}, inplace = True)
    df = df.fillna("- -")
    json_records = df.reset_index().to_json(orient ='records')
    DATA = []
    DATA = json.loads(json_records) 
    context = {'dataFrame': DATA, "Ref_ID": refID}
  
    return render(request, 'r&pLogs.html', context) 

def review(request):

    if not request.user.is_authenticated:
        request.session["bar"] = "Please Login In and Try Again"
        return redirect('/0')
        
    try:
        if not request.user.groups.all()[0].name == "Amnet Peoples":
            request.session["bar"] = "Restricted Page"
            return redirect('/1')
    except: 
        request.session["bar"] = "Restricted Page"
        return redirect('/1')
    
    
    global data
    
    if (request.method == 'POST') and data!={}:
        if request.POST.get("button") == "Create":
            refID = request.POST.get("unique_id")
            cloudFiles = [str(file.name) for file in storage.list_files()]
            msCloudLoc = [file for file in cloudFiles if "ingested data/{}/manuscript/".format(refID) in file][0]
            fName = msCloudLoc.split("/")[-1]
            storage.child(msCloudLoc).download("cache/{}".format(fName))
            print("Submitting File to Copyleaks")
            # copyLeaks.submitFile("cache/{}".format(fName), refID)
            time.sleep(1.5)
            report_path = "ingested data/{}/others/{}_report.pdf".format(refID, refID)
            os.unlink("cache/{}".format(fName))
            status      = copyLeaks.getStatus(refID, "temp_{}.pdf".format(refID))
            if status=="Generated":
                storage.child("ingested data").child(refID).child("others").child(str(refID)+"_report.pdf").put(report_path)
            
            word_count  = data[refID]["word count"]
            link        = storage.child("ingested data").child(refID).child("others").child(str(refID)+"_report.pdf").get_url(None)
            a_title     = data[refID]["article title"]
            a_type      = data[refID]["article type"]
            date        = data[refID]["published date"]
            authors     = data[refID]["authors"]
            abstract    = data[refID]["abstract"]
            n_tables    = data[refID]["no of tables"]
            n_figures   = data[refID]["no of figures"]
            doi         = data[refID]["doi"]
            mail        = data[refID]["mail id"]
            c_interest  = data[refID]["conflict of interest"]
            funding     = data[refID]["funding information"]
            message     = data[refID]["message"]
    
            ppValues = {"Status":status, "Message": message, "Word_Count":word_count, "link":link, "Mail_ID": mail, "Article_Title": a_title, "Article_Type": a_type, "Published_Date": date, "Authors": authors, "No_of_Figures": n_figures, "No_of_Tables": n_tables, "Abstract": abstract, "Special_Instructions": "none", "DOI": doi, "Conflict_of_Interest": c_interest, "Funding": funding}
                    
            context = {"Ref_ID": refID}
            context.update(ppValues)
            return render(request, '../templates/review1.html', context)
            
        if request.POST.get("button") == "SUBMIT":
            return render(request, '../templates/review1.html', {"p":"0"})
        
        elif (len(list(request.POST.keys())) > 1):
            
            refID = list(request.POST.keys())[-1]
            click = request.POST[refID]
            
            print("\n\n", refID, " : ", click, "\n\n")
        
            if click == "Delete":
                database.child("ingested data").child(refID).remove()
            elif click == "Open":
                cloudFiles = [file.name for file in storage.list_files()]
                print("\n\n", cloudFiles, "\n\n")
                report_path = "ingested data/{}/others/{}_report.pdf".format(refID, refID)
                if report_path in cloudFiles:
                    status = "Generated"
                    print("\n\n", report_path, status, "\n\n")
                else:    
                    status      = copyLeaks.getStatus(refID, "cache/temp_{}.pdf".format(refID))
                    print("\n\n", report_path, status, "\n\n")
                    if status=="Generated":
                        storage.child("ingested data").child(refID).child("others").child(str(refID)+"_report.pdf").put("cache/temp_{}.pdf".format(refID))
                        os.unlink("cache/temp_{}.pdf".format(refID))
                userID      = data[refID]["username"]
                word_count  = data[refID]["word count"]
                link        =  storage.child("ingested data").child(refID).child("others").child(str(refID)+"_report.pdf").get_url(None)
                a_title     = data[refID]["article title"]
                a_type      = data[refID]["article type"]
                date        = data[refID]["published date"]
                authors     = data[refID]["authors"]
                abstract    = data[refID]["abstract"]
                n_tables    = data[refID]["no of tables"]
                n_figures   = data[refID]["no of figures"]
                doi         = data[refID]["doi"]
                mail        = data[refID]["mail id"]
                c_interest  = data[refID]["conflict of interest"]
                funding     = data[refID]["funding information"]
                message     = data[refID]["message"]

                ppValues = {"userID": userID, "Status":status, "Message": message, "Word_Count":word_count, "link":link, "Mail_ID": mail, "Article_Title": a_title, "Article_Type": a_type, "Published_Date": date, "Authors": authors, "No_of_Figures": n_figures, "No_of_Tables": n_tables, "Abstract": abstract, "Special_Instructions": "none", "DOI": doi, "Conflict_of_Interest": c_interest, "Funding": funding}
                        
                context = {"Ref_ID": refID}
                context.update(ppValues)
                return render(request, '../templates/review1.html', context)
        
    try:
        data = database.child("ingested data").get().val()
        print("Fetching the Data from the Database")
        dataList = [[i+1, ID, data[ID]["authors"][0], data[ID]["word count"]]for i, ID in enumerate(data.keys())]
    except:
        data = {}
        dataList = []
    
    return render(request, '../templates/review.html', {"dataList": dataList*5})