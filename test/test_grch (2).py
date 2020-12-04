# import grammar_check
# tool = grammar_check.LanguageTool('en-GB')
# text = 'This are bad.'
# matches = tool.check(text)
# matches

# pylanguagetool textfile.txt

# import language_check
# tool = language_check.LanguageTool('en-GB')
# text = u'A sentence with a error in the Hitchhiker’s Guide tot he Galaxy'
# matches = tool.check(text)
# len(matches)

'''
import enchant 

words = ["archeology", "colour", "humor", "neighbour", "accessorise"] 
print("Words given for check : ", words)
print("\n")
dicts_to_use = ['en_US', "en-GB"]
for lang in dicts_to_use : 
    print(lang)
    dict = enchant.Dict(lang) 
    
    # list of words 

    misspelled =[] 
    for word in words: 
        if dict.check(word) == False: 
            misspelled.append(word) 
    print("The misspelled words are : " + str(misspelled)) 
    
    for word in misspelled: 
        print("Suggestion for " + word + " : " + str(dict.suggest(word))) 
    print("\n")
'''
# import smtplib

# sender = 'anish.s.ghiya@gmail.com'
# receivers = ['a.ghiya@iitg.ac.in']

# message = """From: From Person <anish.s.ghiya@gmail.com>
# To: To Person <a.ghiya@iitg.ac.in>
# Subject: SMTP e-mail test

# This is a test e-mail message.
# """

# try:
#    smtpObj = smtplib.SMTP('localhost')
#    smtpObj.sendmail(sender, receivers, message)         
#    print("Successfully sent email")
# except smtplib.SMTPException:
#    print("Error: unable to send email")

# import language_tool_python
# tool = language_tool_python.LanguageTool('en-US')
 
# text = """LanguageTool offers spell and grammar checking. Just paste your text here and click the 'Check Text' button. Click the colored phrases for details on potential errors. or use this text too see an few of of the problems that LanguageTool can detecd. What do you thinks of grammar checkers? Please not that they are not perfect. Style issues get a blue marker: It's 5 P.M. in the afternoon. The weather was nice on Thursday, 27 June 2017"""
 
 
# # get the matches
# matches = tool.check(text)
 
# matches


import re
import pandas as pd
import docxpy
import enchant 
import os
from itertools import chain, repeat, islice

def pad_infinite(iterable, padding=None):
   return chain(iterable, repeat(padding))

def pad(iterable, size, padding=None):
   return islice(pad_infinite(iterable, padding), size)

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

def spelling_error_finder(docx_path) :
    text = get_text_from_docx(docx_path)

    punc = '''!()-[]{};:=-'“"\”, <>./?@#$%^&*_~'''
    for ele in text:  
        if ele in punc:  
            text = text.replace(ele, " ")
    words = text.split(" ")
    # print(words)
    dicts_to_use = {"en-US":[] , "en-GB":[]}
    for lang in dicts_to_use.keys() : 
        dict = enchant.Dict(lang) 
        # list of words 
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
        wrong_US_words = list(pad(wrong_US_words, uk_wds_length, ''))
    elif diff < 0 : 
        wrong_UK_words = list(pad(wrong_UK_words, us_wds_length, ''))

    df = pd.DataFrame(columns = ["US English", "UK English"])
    df['UK English'] = wrong_US_words
    df['US English'] = wrong_UK_words
    df.style.set_properties(subset=['US English'], **{'width': '1000px'})
    return df

def rights_and_perm_log(docx_path) : 

    pattern = r'“(.*?)”'
    # text = 'Hello Amnet "i am a comment that will not be detected." Also there is more to this sentence "I am a comment that will be detected because my length is greater than 10". \nThis line is to test multiple inputs of comments "Data science is an inter-disciplinary field that uses scientific methods, processes, algorithms and systems to extract knowledge and insights from many structural and unstructured data" "An outcomes-based approach to the design, implementation, assessment, and evaluation of education programs using an organizing framework of competencies"'
    text = get_text_from_docx(docx_path)

    # print("Provided sample text : ", text[:1000])
    df = pd.DataFrame(columns=["Chapter", "Content Type", "Illustration Title", "Count", "Source"])
    x = re.findall(pattern, text)

    chapters = ["Chapter 1"]
    sentences = []
    print()
    for chapter in chapters : 
        for sent in x: 
            if len(sent.split(" ")) > 10 :
                # sentences.append(sent)
                df2 = {'Chapter': chapter, 'Content Type': 'Text', 'Illustration Title': sent, 'Count' : len(sent.split(" ")), 'Source':"\n".join(google_search(sent))} 
                df = df.append(df2, ignore_index = True)
    return(df)

def save_log_csv(df,directory) : 
    mainpath = os.path.join(os.getcwd() + directory)
    df.to_csv(mainpath,index=False)
    
docx_path = os.path.join("C:/Users/ANISH/Desktop/Dev/Internship/Manuscripts", "Wittmann-Price_CH01.docx")
# docx_path = os.path.join("C:/Users/ANISH/Desktop/Dev/Internship/Manuscripts", "Test.docx")

text = get_text_from_docx(docx_path)
df = spelling_error_finder(docx_path)

print(df)

# df3 = pd.DataFrame(new, index=["LGBMRegressor()", "XGBRegressor()", "CatboostRegressor()"], columns = header ) 

def ize_yze_tables(df):
    yze_us_lst=[]
    ize_us_lst=[]
    yze_uk_lst=[]
    ize_uk_lst=[]
    import numpy as np
    header = ["US Eng", "UK Eng"]
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
    elif yze_uk_lst == []:
        yze_uk_lst.append('')
    diff = len(yze_uk_lst) - len(yze_us_lst)

    if diff > 0 : 
        # wrong_US_words = list(pad(yze_us_lst, yze_uk_lst, ''))
        yze_df["US Eng"] = list(pad(yze_us_lst, yze_uk_lst, ''))
        yze_df["UK Eng"] = yze_uk_lst
    elif diff < 0 : 
        # wrong_UK_words = list(pad(yze_us_lst, yze_us_lst, ''))
        yze_df["US Eng"] = yze_us_lst
        yze_df["UK Eng"] = list(pad(yze_uk_lst, yze_us_lst, ''))
    else : 
        yze_df["US Eng"] = np.array(yze_us_lst)
        yze_df["UK Eng"] = np.array(yze_uk_lst)

    diff = len(ize_uk_lst) - len(ize_us_lst)

    if diff > 0 : 
        # wrong_US_words = list(pad(yze_us_lst, yze_uk_lst, ''))
        ize_df["US Eng"] = list(pad(ize_us_lst, ize_uk_lst, ''))
        ize_df["UK Eng"] = ize_uk_lst
    elif diff < 0 : 
        # wrong_UK_words = list(pad(yze_us_lst, yze_us_lst, ''))
        ize_df["US Eng"] = ize_us_lst
        ize_df["UK Eng"] = list(pad(ize_uk_lst, ize_us_lst, ''))
    else : 
        ize_df["US Eng"] = np.array(ize_us_lst)
        ize_df["UK Eng"] = np.array(ize_uk_lst)

    return yze_df, ize_df

y, i = ize_yze_tables(df)
print(y)
print(i)
# print((len(re.findall(r"(?:ate|ize|ify|able)$", "terrorize")))>0)
# print((len(re.findall(r"(?:ate|ize|ify|able)$", "Trial")))>0)
# pattern = r'“( [^"]* ”)'

# print(rights_and_perm_log(docx_path))

'''
import language_check 
tool = language_check.LanguageTool('en-US') 
def grammer_check(docx_path) :
    text = get_text_from_docx(docx_path)
    matches = tool.check(text)
    # df = pd.DataFrame()
    # columns=["Message", "Suggestions", "Line", "Context", "Word"]
    match_lst = []
    for match in matches :
        match_lst.append([match.msg, match.replacements, match.context, match.toy - match.fromy, match.tox-match.fromx])

    msg = []
    rep = []
    line = []
    con = []
    wd = []

    print(match_lst[0][0])
    df = df.append(pd.DataFrame(match_lst[0][:5], columns=['col1','col2']),ignore_index=True)
    # df = df.append(pd.Series(match_lst[0][:5], index=["Message", "Suggestions", "Line", "Context", "Word"]), ignore_index=True)
    # for lst in match_lst:
    #     msg.append(lst[0])
    #     rep.append(lst[1])
    #     con.append(lst[2])
    #     line.append(lst[3])
    #     wd.append(lst[4])

    # df['Message'] = msg
    # df['Suggestions'] = rep
    # df['Context'] = con
    # df['Line'] = line
    # df['Word'] = wd

    df = df.drop_duplicates(subset=['Suggestions'], keep="first")
    return(df)

df = grammer_check(docx_path)
print(df.head(50))
'''

'''
import os, sys
# Print current working directory
print ("Current working dir : %s", os.getcwd())
mainpath = os.path.join(os.getcwd() + "\Csvfiles" + "\stest.csv")
print(mainpath)
df.to_csv(mainpath,index=False)
'''

# if len(x[0].split(" ")) > 7 : 
#     print(x)
# print(x)