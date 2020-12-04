from django.http import HttpResponse
from django.shortcuts import render
import os, pandas as pd
import pyrebase, time
import bs4
import smtplib
from docx2pdf import convert
from xml.dom import minidom
import pdf2docx
import docxpy, enchant
import random, re
from itertools import chain, repeat, islice
import language_check 
import re
import numpy as np

langTool = language_check.LanguageTool('en-US') 

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

#Email Credentials
email_address   = "@@@@@@@@@@@@@@gmail.com"
email_password  = "################"

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
    
    """
    print("\rDeleting Downloaded Files", end="")
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
            return True
        except:
            print("Login : Failed - Kindly Check the API Settings")
            return False
            
    def stop(self):
        self.server.quit()
        print("Quit : Success")
        
    def send(self, to_mailID, subject, message):
        body = "Subject: {}\n\n{}".format(subject,message)
        self.server.sendmail("Confirmation mail for your submission", to_mailID, body)
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
    
def google_search(query): 
    search_result = []
    try: 
        from googlesearch import search 
        for j in search(query, tld="co.in", num=2, stop=2, pause=2): 
            search_result.append(j)
    except ImportError:  
        print("No module named 'google' found") 
    return search_result
    
def createRnPlogs(text, refID):
    print("Generating Rights and Permission Logs")
    pattern = r'“(.*?)”'
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

    df.to_excel(os.path.join("./upload/", str(refID), "others", str(refID)+"_RnPlogs.xlsx"), header=["Chapter", "Content Type", "Illustration Title", "Count", "Source"])

def pad_infinite(iterable, padding=None):
   return chain(iterable, repeat(padding))

def pad(iterable, size, padding=None):
   return islice(pad_infinite(iterable, padding), size)

def createSpellLogs(text, refID) :
    print("Generating Spell Check Logs")
    punc = '''!()-[]{};:=-'“"\”, <>./?@#$%^&*_~'''
    for ele in text:  
        if ele in punc:  
            text = text.replace(ele, " ")
    words = text.split(" ")
    dicts_to_use = {"en-US":[] , "en-GB":[]}
    for lang in dicts_to_use.keys() : 
        dict = enchant.Dict(lang) 
        misspelled = [] 
        for word in words: 
            if word != "":
                if dict.check(word) == False: 
                    misspelled.append(word) 
        dicts_to_use[lang] = misspelled

    unique_wds = set(dicts_to_use["en-US"]) ^ set(dicts_to_use["en-GB"])
    wrong_US_words = list(set(dicts_to_use["en-US"]) & unique_wds)
    wrong_UK_words = list(set(dicts_to_use["en-GB"]) & unique_wds)
    uk_wds_length = len(wrong_UK_words)
    us_wds_length = len(wrong_US_words)
    diff = uk_wds_length - us_wds_length

    if diff > 0 : 
        wrong_US_words = list(pad(wrong_US_words, diff+us_wds_length, ''))
    elif diff > 0 : 
        wrong_UK_words = list(pad(wrong_UK_words, diff+uk_wds_length, ''))
    
    
    
    df = pd.DataFrame(columns = ["US English", "UK English"])
    df['US English'] = wrong_US_words
    df['UK English'] = wrong_UK_words
    cp = df.copy()
    df.to_excel(os.path.join("./upload/", str(refID), "others", str(refID)+"_Spell_logs.xlsx"))
    
    return cp


def createIzYzLogs(df, refID):
    print("Generating IzYz Logs")
    yze_us_lst, ize_us_lst, yze_uk_lst, ize_uk_lst = [], [], [], []
    import numpy as np
    header = ["US English", "UK English"]
    yze_df = pd.DataFrame(columns=header)
    ize_df = pd.DataFrame(columns=header)

    for wd in np.array(df['US English']):
        if re.findall(r"(?:yze|yse)$", wd)!=[]:
            yze_us_lst.append(wd)
        elif re.findall(r"(?:ise|ize)$", wd)!=[]:
            ize_us_lst.append(wd)

    for wd in np.array(df['UK English']):
        if re.findall(r"(?:yze|yse)$", wd)!=[]:
            yze_uk_lst.append(wd)
        elif re.findall(r"(?:ise|ize)$", wd)!=[]:
            ize_uk_lst.append(wd)
    

    if yze_us_lst == []:
        yze_us_lst.append('')
    if yze_uk_lst == []:
        yze_uk_lst.append('')
    diff = len(yze_uk_lst) - len(yze_us_lst)
    
    print("\n\n", diff, yze_uk_lst, yze_us_lst, "\n\n")
    
    if diff > 0 : 
        # wrong_US_words = list(pad(yze_us_lst, yze_uk_lst, ''))
        yze_df["US English"] = list(pad(yze_us_lst, yze_uk_lst, ''))
        yze_df["UK English"] = yze_uk_lst
    elif diff < 0 : 
        # wrong_UK_words = list(pad(yze_us_lst, yze_us_lst, ''))
        yze_df["US English"] = yze_us_lst
        yze_df["UK English"] = list(pad(yze_uk_lst, yze_us_lst, ''))
    else : 
        yze_df["US English"] = np.array(yze_us_lst)
        yze_df["UK English"] = np.array(yze_uk_lst)


    if ize_us_lst == []:
        ize_us_lst.append('')
    if ize_uk_lst == []:
        ize_uk_lst.append('')
    diff = len(ize_uk_lst) - len(ize_us_lst)

    print("\n\n", diff, ize_uk_lst, ize_us_lst, "\n\n")
    
    if diff > 0 : 
        ize_df["US English"] = list(pad(ize_us_lst, ize_uk_lst, ''))
        ize_df["UK English"] = ize_uk_lst
    elif diff < 0 : 
        ize_df["US English"] = ize_us_lst
        ize_df["UK English"] = list(pad(ize_uk_lst, ize_us_lst, ''))
    else : 
        ize_df["US English"] = np.array(ize_us_lst)
        ize_df["UK English"] = np.array(ize_uk_lst)
    
    resultDF = pd.concat([ize_df, yze_df], axis=1, join='inner')
    resultDF.to_excel(os.path.join("./upload/", str(refID), "others", str(refID)+"_Yzeize_logs.xlsx"))
    print("\n\n", ize_df, resultDF, yze_df, "\n\n")
    ize_df.to_excel(os.path.join("./upload/", str(refID), "others", str(refID)+"_izeSpell_logs.xlsx"))
    yze_df.to_excel(os.path.join("./upload/", str(refID), "others", str(refID)+"_yzeSpell_logs.xlsx"))

def createCommaLogs(text, refID):

    print("Generating Comma Logs")
    pattern = "and"
    r = re.search(pattern, text, re.IGNORECASE)
    output = []
    if r:
        while text:
            before, match, text = text.partition(pattern)
            if match:
                if not output:
                    before = before.split()[-2:]
                else:    
                    before = ' '.join([pattern, before]).split()[-2:]
                after = text.split()[:2]
                output.append((before, after))
    data=[]
    
    for i in range(len(output)) : 
        data.append(" ".join(output[i][0]+[pattern]+output[i][1]))
    lines=[]
    for line in data : 
        pattern = "\w+, \w+ and"
        z = re.search(r"\w+, \w+ and", line, re.IGNORECASE)
        if z : 
            lines.append(line)
        else : 
            continue
    final_df = pd.DataFrame(data=lines, columns=['Context'])
    print(final_df)
    final_df.to_excel(os.path.join("./upload/", str(refID), "others", str(refID)+"_Comma_logs.xlsx"))


def createGrammarLogs(text, refID) :
    print("Generating Grammar Check Logs")
    matches = langTool.check(text)
    df = pd.DataFrame(columns=["Message", "Suggestions", "Context", "Word"])

    match_lst = []
    for match in matches :
        match_lst.append([match.msg, match.replacements, match.context, match.toy - match.fromy, match.tox-match.fromx])

    msg, rep, lin, con, wrd = [], [], [], [], []
    for lst in match_lst:
        msg.append(lst[0])
        rep.append(lst[1])
        con.append(lst[2])
#        lin.append(lst[3])
        wrd.append(lst[4])

    df['Message']       = msg
    df['Suggestions']   = rep
    df['Context']       = con
#    df['Line']          = lin
    df['Word']          = wrd
    df = df[df['Message']!='Possible spelling mistake found']
    
    df.to_excel(os.path.join("./upload/", str(refID), "others", str(refID)+"_Grammar_logs.xlsx"))


unique_id = 0
mailService = MAIL(email_address, email_password)
def index(request):       
    global unique_id
    logs = []
    
    if (request.method == 'POST'):
            
    
        if request.POST.get("button") == "UPLOAD & POPULATE":
            #deleteUpNDownloads(unique_id)
            
            unique_id = str(random.randint(10000,99999))#"unique_id"
            if database.child("ingested data").get().val():
                while unique_id in database.child("ingested data").get().val().keys():
                    unique_id = str(random.randint(10000,99999))#"unique_id"
            
            print("\n\n", "Reference ID : ", unique_id, "\n\n")
            
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
                    
                    createRnPlogs(text, unique_id)
                    gDF = createSpellLogs(text, unique_id)
                    createIzYzLogs(gDF, unique_id)
                    createGrammarLogs(text, unique_id)
                    createCommaLogs(text, unique_id)
                        
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
            # text        = request.POST['content_text']
            
            dbValues = {"mail id": mail, "message": message, "doi":doi, "word count":wCount,"article title": aTitle, "article type": aType, "published date": date, "authors": author, "no of figures": figures, "no of tables": tables, "abstract": abstract, "special instructions":instruct, "conflict of interest":cInterest, "funding information":funding}
            print("\n\n", dbValues, "\n\n")
            
            if not len(os.listdir(os.path.join(UPLOAD_LOCATION, refID, "images"))) == int(figures):
                ppValues = {"Ref_ID": refID, "Mail_ID": mail, "Article_Title": aTitle, "Article_Type": aType, "Published_Date": date, "Authors": author, "No_of_Figures": "", "No_of_Tables": tables, "Abstract": abstract, "Special_Instructions": instruct, "DOI": doi, "Conflict_of_Interest": cInterest, "Funding": funding, "Word_Count": wCount}
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
            if mailService.start():
                logs.append("Confirmation mail has been sent to " + str(mail))
                mailService.send(mail, "Confirmation mail for your Submission", "Amnet Systems\nReference ID\t:\t{} \nYour request has been submitted successfully".format(refID))
            logs.append("Database : Updated Successfully")
            context = {'logs':"\n".join(logs), "alert":"#99ff99"}
            
            
            return render(request, '../templates/page.html', context)
            
            
    context = {'logs': "", "alert":"#D6EAF8", "Conflict_of_Interest": 0, "Funding": 0}
    return render(request, '../templates/page.html', context)
    
    
