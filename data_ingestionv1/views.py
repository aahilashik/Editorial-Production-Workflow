from django.http import HttpResponse
from django.shortcuts import render
import os, pandas as pd
import pyrebase, time
import bs4
import smtplib
from docx2pdf import convert
from xml.dom import minidom
import pdf2docx
import docxpy
import random

config = {
    "apiKey" : "AIzaSyC7fww5ra5nUCPh-V9h43UHQ9BTqBAqm2I",
    "authDomain" : "data-ingestion-aa201.firebaseapp.com",
    "databaseURL" : "https://data-ingestion-aa201.firebaseio.com",
    "projectId" : "data-ingestion-aa201",
    "storageBucket" : "data-ingestion-aa201.appspot.com",
    "messagingSenderId" : "966163523151",
    "appId" : "1:966163523151:web:02cfd4585f227153c6ac3a",
    "measurementId" : "G-0CFVXYRKRN"
}

#Email Credentials
email_address   = "*****@gmail.com"
email_password  = "******"

UPLOAD_LOCATION = "./upload/"
DOWNLOAD_LOCATION = "./download/"
ALLOWED_MS_FORMATS = ["docx", "pdf", "xml"]
ALLOWED_IM_FORMATS = ["tiff", "jpg", "jpeg", "png"]
CLOUD_LOCATION  = "ingested data"

firebase    = pyrebase.initialize_app(config)
storage     = firebase.storage()
database    = firebase.database()

# Create your views here.

def deleteUpNDownloads(unique_id):
    print("\rDeleting Uploaded Files", end="")
    if os.path.exists(os.path.join(UPLOAD_LOCATION, unique_id)):
        for folder in os.listdir(os.path.join(UPLOAD_LOCATION, unique_id)):
            for file in os.listdir(os.path.join(UPLOAD_LOCATION, unique_id, folder)):
                os.unlink(os.path.join(UPLOAD_LOCATION, unique_id, folder, file))
    print("\r Deleted Uploaded Files")
    
    """print("\rDeleting Downloaded Files", end="")
    for folder in os.listdir(os.path.join(DOWNLOAD_LOCATION, unique_id)):
        for file in os.listdir(os.path.join(UPLOAD_LOCATION, unique_id)):
            os.unlink(os.path.join(DOWNLOAD_LOCATION, unique_id, folder, file))
    print("\r Deleted Downloaded Files")
    """
    

class MAIL:
    
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
        
    def start(self):
        try:
            self.server = smtplib.SMTP("smtp.gmail.com", 587)
            self.server.starttls()
            self.server.login(self.username, self.password)
            print("Login : Sucess")
        except:
            print("Login : Failed - Kindly Check the API Settings")
            
    def stop(self):
        self.server.quit()
        print("Quit : Success")
        
    def send(self, to_mailID, subject, message):
        body = "Subject: {}\n\n{}".format(subject,message)
        self.server.sendmail(self.username, to_mailID, body)
        print("Send : Success")


def word_counter(docx_path) : 

    text = docxpy.process(docx_path).replace(":", " ")
    
    words = [word for word in text.split() if not word in [":", "."]]

    text = " ".join(docxpy.process(docx_path).split())
    
    return len(words), text

def get_text_from_docx(docx_path) : 
    file = docx_path
    text = " ".join(docxpy.process(file).split())
    return text
    
unique_id = 0
def index(request):       
    global unique_id
    logs = []
    
    if (request.method == 'POST'):
            
    
        if request.POST.get("button") == "UPLOAD & POPULATE":
            #deleteUpNDownloads(unique_id)
            unique_id = str(random.randint(10000,99999))#"unique_id"
    
            ppValues = {}
            try:
                if not os.path.exists(os.path.join(UPLOAD_LOCATION, unique_id)): 
                    os.mkdir(os.path.join(UPLOAD_LOCATION, unique_id))
                if not os.path.exists(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript")): 
                    os.mkdir(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript"))
                if not os.path.exists(os.path.join(UPLOAD_LOCATION, unique_id, "images")): 
                    os.mkdir(os.path.join(UPLOAD_LOCATION, unique_id, "images"))
                if not os.path.exists(os.path.join(UPLOAD_LOCATION, unique_id, "others")): 
                    os.mkdir(os.path.join(UPLOAD_LOCATION, unique_id, "others"))
            except: pass
            logs.append("Auto Populate Done")
            for file in request.FILES.getlist("files"):
                
                print("\n\n", file.name, os.listdir(os.path.join(UPLOAD_LOCATION, "unique_id", "manuscript")), "\n\n" )
                
                if file.name.split(".")[-1] in ALLOWED_MS_FORMATS :
                    word_count, text = 0, ""
                
                    logs.append("File  : {} - Successfully Uploaded".format(str(file.name)))
                    with open(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name), 'wb+') as destination:
                        for i, chunk in enumerate(file.chunks()):
                            destination.write(chunk)
                        destination.close()
                        
                    if file.name.split(".")[-1] == "docx":
                        
                        convert(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name), os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".pdf"))
                        word_count, text = word_counter(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name))
                        
                    else:
                    
                        pdf2docx.parse(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name), os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".docx"))
                        word_count, text = word_counter(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".docx"))
                        os.unlink(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".docx"))
                    
                    
#                    client.process(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript"),  os.path.join(UPLOAD_LOCATION, unique_id, "manuscript"), 10, "processHeaderDocument", False, 1, 0, True, False)
                    
                    coI, fund = 0, 0
                    headingList = minidom.parse(os.path.join(UPLOAD_LOCATION, "unique_id", "manuscript", file.name.split(".")[0] + ".tei.xml")).getElementsByTagName('head')
                    for head in headingList:
                        if head.firstChild:
                            if "conflict of interest" in head.firstChild.data.lower():
                                coI = 1
                            if "funding" in head.firstChild.data.lower():
                                fund = 1
                                
                    
                    with open(os.path.join(UPLOAD_LOCATION, "unique_id", "manuscript", file.name.split(".")[0] + ".tei.xml"), 'rb') as tei:
                        soup = bs4.BeautifulSoup(tei, 'lxml')
                                        
                        try:
                            a_title = soup.title.getText()
                        except: a_title = ""
                        try:
                            a_type = soup.title.get_attribute_list("type")[0]
                        except: a_type = ""
                        try:
                            date = soup.date.getText()
                        except: date = ""
                        try:
                            authors = ([a.persname.getText(" ") for a in soup.analytic.findAll("author")] if soup.analytic.parent.parent.name=="sourcedesc" else [])
                        except: authors = []
                        try:
                            abstract = soup.abstract.getText(separator=' ', strip=True)
                        except: abstract = ""
                        try:
                            n_tables = len(list(dict.fromkeys(soup.findAll("table"))))
                        except: n_tables = ""
                        try:
                            n_figures = sum([1 for f in soup.findAll("figure") if ("fig" in f.get_attribute_list("xml:id")[0] and type(list(f.children)[0])==bs4.element.NavigableString)])
                        except: n_figures = ""
                        try:
                            doi = soup.find('idno', type='DOI').getText()
                        except: doi = ""
                        mail = ""
                        c_interest = coI
                        funding = fund
                        
                        print("\n\n", text, "\n\n")
                        ppValues = {"Content_Text": text, "Ref_ID": unique_id, "Mail_ID": mail, "Article_Title": a_title, "Article_Type": a_type, "Published_Date": date, "Authors": authors, "No_of_Figures": n_figures, "No_of_Tables": n_tables, "Abstract": abstract, "Special_Instructions": "none", "DOI": doi, "Conflict_of_Interest": c_interest, "Funding": fund, "Word_Count": word_count}
                    
                    if file.name.split(".")[-1] == "docx":
                        os.unlink(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".pdf"))
                    
                else:
                    logs.append("File  : {} - Upload Error : Not Supported".format(str(file.name)))
                    
            for file in request.FILES.getlist("images"):
                if file.name.split(".")[-1] in ALLOWED_IM_FORMATS:
                    logs.append("Image : {} - Successfully Uploaded".format(str(file.name)))
                    with open(os.path.join(UPLOAD_LOCATION, unique_id, "images", file.name), 'wb+') as destination:
                        for i, chunk in enumerate(file.chunks()):
                            destination.write(chunk)
                else:
                    logs.append("Image : {} - Upload Error : Not Supported".format(str(file.name)))

            for file in request.FILES.getlist("others"):
                logs.append("Other : {} - Successfully Uploaded".format(str(file.name)))
                with open(os.path.join(UPLOAD_LOCATION, unique_id, "others", file.name), 'wb+') as destination:
                    for i, chunk in enumerate(file.chunks()):
                        destination.write(chunk)
            
            context = {'logs':"\n".join(logs)}
            context.update(ppValues)
            return render(request, '../templates/page.html', context)
            
            
        if request.POST.get("button") == "SUBMIT":
        
            mail        = request.POST['mail_id']
            doi         = request.POST['doi']
            aTitle      = request.POST['article_title']
            aType       = request.POST['article_type']
            abstract    = request.POST['abstract']
            date        = request.POST['published_date']
            author      = request.POST.getlist("authors")
            figures     = request.POST['no_of_figures']
            tables      = request.POST['no_of_tables']
            instruct    = request.POST['spl_instruct']
            cInterest   = request.POST['c_Interest']
            funding     = request.POST['funding']
            refID       = request.POST['unique_id']
            wCount      = request.POST['word_count']
            message     = request.POST['message']
            text        = request.POST['content_text']
            
            dbValues = {"text": text, "mail id": mail, "message": message, "doi":doi, "word count":wCount,"article title": aTitle, "article type": aType, "published date": date, "authors": author, "no of figures": figures, "no of tables": tables, "abstract": abstract, "special instructions":instruct, "conflict of interest":cInterest, "funding information":funding}
            print("\n\n", dbValues, "\n\n")
            
            if not len(os.listdir(os.path.join(UPLOAD_LOCATION, refID, "images"))) == int(figures):
                ppValues = {"Content_Text": text, "Ref_ID": refID, "Mail_ID": mail, "Article_Title": aTitle, "Article_Type": aType, "Published_Date": date, "Authors": author, "No_of_Figures": "", "No_of_Tables": tables, "Abstract": abstract, "Special_Instructions": instruct, "DOI": doi, "Conflict_of_Interest": cInterest, "Funding": funding, "Word_Count": wCount}
                context = {'logs':"Submission Error : Image count", "alert":"#ff8888"}
                context.update(ppValues)
                return render(request, '../templates/page.html', context)
                # return render(request, '../templates/page.html', {"logs":"Submission Error : Image count", "alert":"#ff8888"})
                
            for folder in os.listdir(os.path.join(UPLOAD_LOCATION, refID)):
                for file in os.listdir(os.path.join(UPLOAD_LOCATION, refID, folder)):
                                        
                    path_on_cloud = CLOUD_LOCATION
                    path_on_local = os.path.join(UPLOAD_LOCATION, refID, folder, file)
                    storage.child(path_on_cloud).child(refID).child(folder).child(file).put(path_on_local)
                    #os.unlink(path_on_local)
                    
            database.child(CLOUD_LOCATION).child(refID).set(dbValues)
            logs.append("Database : Updated Successfully")
            context = {'logs':"\n".join(logs), "alert":"#99ff99"}
            return render(request, '../templates/page.html', context)
            
            
    context = {'logs': "", "alert":"#D6EAF8", "Conflict_of_Interest": 0, "Funding": 0}
    return render(request, '../templates/page.html', context)
    
    
