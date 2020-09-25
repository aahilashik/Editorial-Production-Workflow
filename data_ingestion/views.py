from django.http import HttpResponse
from django.shortcuts import render
import os
import pyrebase

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

UPLOAD_LOCATION = "./upload/"
ALLOWED_FORMATS = ["csv", "docx", "xml"]
CLOUD_LOCATION  = "files/"

firebase    = pyrebase.initialize_app(config)
storage     = firebase.storage()
database    = firebase.database()

# Create your views here.

def index(request):       
    logs = []
    unique_id = "unique_id"
    
    if (request.method == 'POST'):
        if request.POST.get("button") == "SUBMIT":
            
            mail        = request.POST['mail_id']
            aTitle       = request.POST['article_title']
            aType        = request.POST['article_type']
            head        = request.POST['running_head']
            author      = request.POST['authors']
            figures     = request.POST['no_of_figures']
            tables      = request.POST['no_of_tables']
            instruct    = request.POST['spl_instruct']
            
            dbValues = {"mail id": mail, "article title": aTitle, "article type": aType, "running head": head, "author s": author, "no of figures": figures, "no of tables": tables, "special instructions":instruct}
            
            for file in request.FILES.getlist("files"):
                if file.name.split(".")[-1] in ALLOWED_FORMATS:
                    logs.append("File : {} - Successfully Uploaded".format(str(file.name)))
                    with open(os.path.join(UPLOAD_LOCATION, file.name), 'wb+') as destination:
                        for i, chunk in enumerate(file.chunks()):
                            destination.write(chunk)
                                        
                    path_on_cloud = os.path.join(CLOUD_LOCATION, unique_id, file.name)
                    path_on_local = os.path.join(UPLOAD_LOCATION, file.name)
                    storage.child(path_on_cloud).put(path_on_local)
                else:
                    logs.append("File : {} - Upload Error : Not Supported".format(str(file.name)))
            
            database.child(unique_id).set(dbValues)
            logs.append("Database : Updated Successfully")
            context = {'logs':"\n".join(logs)}
            return render(request, '../templates/home.html', context)

                    
       





    context = {'logs': ""}
    return render(request, '../templates/home.html', context)
    
def page(request):
    return HttpResponse("You are in page 1")
    
