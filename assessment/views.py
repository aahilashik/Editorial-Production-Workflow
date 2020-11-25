from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
import pyrebase
import os
import pdf2docx
import pandas as pd
import docxpy
import re, json

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

data = {}


def get_text_from_docx(docx_path) : 
    file = docx_path
    text = docxpy.process(file)
    text = text.split()
    text = " ".join(text)
    return text

def google_search(query): 
    search_result = []
    try: 
        from googlesearch import search 
        for j in search(query, tld="co.in", num=2, stop=2, pause=2): 
            search_result.append(j)
    except ImportError:  
        print("No module named 'google' found") 
    return search_result

def download(request, refID):    
    file_path = os.path.join("./upload/", str(refID), "others", str(refID)+".csv")
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def logs(request, refID): 
    global data
    print("\n\n", data.keys(), "\n\n")
    
    # return redirect("https://google.com/")
    
    pattern = r'“(.*?)”'
    
    # file = os.listdir(os.path.join("./upload/", refID, "manuscript"))[0]
    # pdf2docx.parse(os.path.join("./upload/", refID, "manuscript", file), os.path.join("./upload/", refID, "manuscript", file.split(".")[0] + ".docx"))
    
    # print("\n\n", os.listdir(os.path.join("./upload/", refID, "manuscript")), "\n\n")
    
    text = data[str(refID)]["text"] # get_text_from_docx(os.path.join("./upload/", refID, "manuscript", file.split(".")[0] + ".docx"))
    #os.unlink(os.path.join("./upload/", refID, "manuscript", file.split(".")[0] + ".docx"))

    
    df = pd.DataFrame(columns=["Chapter", "Type", "Title", "Count", "Source"])
    x = re.findall(pattern, text)

    chapters = ["Chapter 1"]
    sentences = []
    print()
    for chapter in chapters:
        for sent in x:
            if len(sent.split(" ")) > 10 :
                df2 = {'Chapter': chapter, 'Type': 'Text', 'Title': sent, 'Count' : len(sent.split(" ")), 'Source':"\n".join(google_search(sent))} 
                df = df.append(df2, ignore_index = True)

    df.to_csv(os.path.join("./upload/", str(refID), "others", str(refID)+".csv"), header=["Chapter", "Content Type", "Illustration Title", "Count", "Source"])
    json_records = df.reset_index().to_json(orient ='records')
    DATA = []
    DATA = json.loads(json_records) 
    context = {'dataFrame': DATA, "Ref_ID": refID}
  
    return render(request, 'r&pLogs.html', context) 

def review(request):
    global data
    
    if (request.method == 'POST'):
        if request.POST.get("button") == "Create":
            funding     = request.POST['unique_id']
            print("\n\n", funding, "\n\n")
            pass
            
        if request.POST.get("button") == "SUBMIT":
            return render(request, '../templates/review1.html', {"p":"0"})
        
        elif (len(list(request.POST.keys())) > 1):
            
            refID = list(request.POST.keys())[-1]
            click = request.POST[refID]
            
            print("\n\n", refID, " : ", click, "\n\n")
        
            if click == "Delete":
                database.child(refID).remove()
            elif click == "Open":
                
                print("\n\n", [file.name for file in storage.child(str(refID)).list_files()], "\n\n")
                
                word_count  = data[refID]["word count"]
                link        = "http://www.google.com/"
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

                ppValues = {"Message": message, "Word_Count":word_count, "link":link, "Mail_ID": mail, "Article_Title": a_title, "Article_Type": a_type, "Published_Date": date, "Authors": authors, "No_of_Figures": n_figures, "No_of_Tables": n_tables, "Abstract": abstract, "Special_Instructions": "none", "DOI": doi, "Conflict_of_Interest": c_interest, "Funding": funding}
                        
                context = {"Ref_ID": refID}
                context.update(ppValues)
                return render(request, '../templates/review1.html', context)
        
    
    data = database.child("ingested data").get().val()
    dataList = [[i+1, ID, data[ID]["authors"][0], data[ID]["word count"]]for i, ID in enumerate(data.keys())]
    
    return render(request, '../templates/review.html', {"dataList": dataList*20})