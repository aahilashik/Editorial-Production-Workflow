from django.http import HttpResponse
from django.shortcuts import render
import os, pandas as pd
import pyrebase, time
import bs4
import smtplib
from docx2pdf import convert
from xml.dom import minidom

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
ALLOWED_MS_FORMATS = ["docx", "pdf"]
ALLOWED_IM_FORMATS = ["tiff", "jpg", "jpeg", "png"]
CLOUD_LOCATION  = "manuscript/"

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
    
def index(request):       
    logs = []
    unique_id = "unique_id"
    
    if (request.method == 'POST'):
            
    
        if request.POST.get("button") == "UPLOAD & POPULATE":
            #deleteUpNDownloads(unique_id)
            
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
                if file.name.split(".")[-1] in ALLOWED_MS_FORMATS:
                    logs.append("File  : {} - Successfully Uploaded".format(str(file.name)))
                    with open(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name), 'wb+') as destination:
                        for i, chunk in enumerate(file.chunks()):
                            destination.write(chunk)
                        destination.close()
                        
                    if file.name.split(".")[-1] == "docx":
                        convert(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name), os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".pdf"))
                    
#                    client.process(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript"),  os.path.join(UPLOAD_LOCATION, unique_id, "manuscript"), 10, "processHeaderDocument", False, 1, 0, True, False)
                    
                    coI, fund = 0, 0
                    headingList = minidom.parse(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".tei.xml")).getElementsByTagName('head')
                    for head in headingList:
                        if head.firstChild:
                            if "conflict of interest" in head.firstChild.data.lower():
                                coI = 1
                            if "funding" in head.firstChild.data.lower():
                                fund = 1
                                
                    
                    with open(os.path.join(UPLOAD_LOCATION, unique_id, "manuscript", file.name.split(".")[0] + ".tei.xml"), 'rb') as tei:
                        soup = bs4.BeautifulSoup(tei, 'lxml')
                                        
                        a_title = soup.title.getText()
                        a_type = soup.title.get_attribute_list("type")[0]
                        date = soup.date.getText()
                        authors = ([a.persname.getText(" ") for a in soup.analytic.findAll("author")] if soup.analytic.parent.parent.name=="sourcedesc" else [])
                        abstract = soup.abstract.getText(separator=' ', strip=True)
                        n_tables = len(list(dict.fromkeys(soup.findAll("table"))))
                        n_figures = sum([1 for f in soup.findAll("figure") if ("fig" in f.get_attribute_list("xml:id")[0] and type(list(f.children)[0])==bs4.element.NavigableString)])
                        mail = ""
                        c_interest = coI
                        doi = soup.find('idno', type='DOI').getText()
                        funding = fund
                
                        ppValues = {"Mail_ID": mail, "Article_Title": a_title, "Article_Type": a_type, "Published_Date": date, "Authors": authors, "No_of_Figures": n_figures, "No_of_Tables": n_tables, "Abstract": abstract, "Special_Instructions": "none", "DOI": doi, "Conflict_of_Interest": c_interest, "Funding": fund}
                    
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
            author      = request.POST['authors']
            figures     = request.POST['no_of_figures']
            tables      = request.POST['no_of_tables']
            instruct    = request.POST['spl_instruct']
            cInterest   = request.POST['c_Interest']
            funding     = request.POST['funding']
            
            dbValues = {"mail id": mail, "article title": aTitle, "article type": aType, "running head": date, "authors": author, "no of figures": figures, "no of tables": tables, "abstract": abstract, "special instructions":instruct, "conflict of interest":cInterest, "funding information":funding}
            print("\n\n", dbValues, "\n\n")
            
            if not len(os.listdir(os.path.join(UPLOAD_LOCATION, unique_id, "images"))) == int(figures):
                return render(request, '../templates/page.html', {"logs":"Submission Error : Image count", "alert":"#ff8888"})

                    
            for folder in os.listdir(os.path.join(UPLOAD_LOCATION, unique_id)):
                for file in os.listdir(os.path.join(UPLOAD_LOCATION, unique_id, folder)):
                                        
                    path_on_cloud = os.path.join(CLOUD_LOCATION, unique_id, folder, file)
                    path_on_local = os.path.join(UPLOAD_LOCATION, unique_id, folder, file)
                    # storage.child(path_on_cloud).child(unique_id).child(folder).put(path_on_local)
                    
            # database.child(unique_id).set(dbValues)
            logs.append("Database : Updated Successfully")
            context = {'logs':"\n".join(logs), "alert":"#99ff99"}
            return render(request, '../templates/page.html', context)
            
            
    context = {'logs': "", "alert":"#D6EAF8", "Conflict_of_Interest": 0, "Funding": 0}
    return render(request, '../templates/page.html', context)
    
    
