#!/bin/bash
from PIL import Image
#import pytesseract
#pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
import cv2,glob,time
import re,logging,os,sys,subprocess,shutil
import numpy as np
import pandas
import operator,collections
from dateutil.parser import parse
import calendar,datetime,time

import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize,sent_tokenize
import string as string_func
from nltk.stem import WordNetLemmatizer 
lemmatizer = WordNetLemmatizer() 

import spacy
from spacy.matcher import Matcher
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
import warnings
warnings.simplefilter("ignore")

EMAIL_REGEX = r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}"
invalidChars = set(string_func.punctuation)
symbols_log = ["e@","e","@","¢","_","—","°","|",'?']
#Remove All symbols expect "."
stop_symbols = []
for i in list(invalidChars):
    if(i == "."):
        pass
    else:
        stop_symbols.append(i)

def headline_text_extract():
    objective = ['CARRIER OBJECTIVES','career Objective','Career Summary','OBJECTIVE','OBIECTIVE']
    academics = ['Academic Project Details','Education Qualification','Education','Educational Background','Academics','ACADEMIC DETAILS','ACADEMIC BACKGROUND','ACADEMIC QUALIFICATIONS','EDUCATIONAL QUALIFICATION','EDUCATIONAL QUALIFICATIONS','ACADEMIC SUMMARY','Academic Profile','Academic Credentials','EDUCATIONAL DETAILS','Additional Qualification','ACADEMIC QUALIFICATION','Academic Records','Academic Credentials','Educational Records','Education records']
    experience = ['company experience','Industrial Experience','Experience','Training and Experience','Internship Experience','Work Experience','Domain Experience','EXPERIENTIAL  LEARNING','Organizational Experience','Professional Experience','research Experience']    
    publications = ['publications','patents','publication','patent']             
    internships = ['Trainings Internship','INTERNSHIP EXPERIENCE II','INTERNSHIP EXPERIENCE I','Summer Internship Program','Summer Internship','Internship Program','Internships',"Internship"]
    skills = ['TECHNICAL SKILL SET','skills','Computer Professiency','COMPUTER SKILLS','COMPUTING SKILLS','Software Knowledge','Software skills','Key SKills and Strengths','Technical Skills','SELF SKILLS','Hardware Skills','SKILLS','IT Proficiency','Expertise','Expertise skills','Technical SKillset','software proficiency','IT SKILLS','skills and abilities','SKILLS/CORE COMPETENCIES','Core Competancies','COMPETENCIES & SKILLS','Technical Strength','Software Proficiency','Technical exposure']
    personal_info = ['MY STRENGTH','ADDITIONAL INFORMATION','Personal Details','PERSONAL PROFILE','Personal Information','Strength','My Strengths','HOBBIES','personal traits','Other Interest and Hobbies']
    achievements = ['academic achievements year','ACADEMIC ACHIEVEMENTS','achievement','Achievements','Post of Responsibilities','Achievements and Extra Curricular','academic achievements','Achievements and Participation','Scholastic Achievements','Extracurricular Achievements','EXTRA CURRICULAR ACHIEVEMENTS','awards','awards and achievements','participation','participations','Recognitions','Technical Award and Achievements','Technical Achievements','Technical Presentation','Technical qualification','areas of expertise']
    interests = ['INTERESTS','AREA OF INTEREST','Interests and hobbies','Fields of Interest','Interested Fields','interest']
    #languages = ['LANGUAGES KNOWN','known Languages','Language Efficiency','Language Proficiency','Languages']
    projects = ['GRADUATE LEVEL PROJECT','Final Year Project','Final Year Projects','Academic Projects Undertaken','Academic Project Details','Project Undertaken','Academic Project','Academic Activities','Mini Projects','PROJECTS AND INTERNSHIPS','project','PROJECTS','INTERNSHIPS','Project Details','Key Projects','Project Profile','Project Done','Technical project','Technical Projects and Internships','RESEARCH PROJECTS','ongoing projects','BE Project','Academic Projects','Course projects','other projects','graduate level projects','project details']
    declaration = ["declaration","declarations"]
    details = ['ADDITIONAL INFORMATION','Personal Details','PERSONAL PROFILE','Personal Information','Strength','My Strengths','HOBBIES','personal traits','Other Interest & Hobbies']
    courseWork = ['COURSES','Course Work','coursework','courses did','course taken','relevant coursework','key courses taken','Course And Training']
    publications = ['publications and rewards','publications','publication','research publication']
    extracurriculars = ['Extra Curricular Activities and Achievements','EXTRACURRICULARS','EXTRA-CURRICULARS','EXTRA-CURRICULUM ACTIVITIES','EXTRA CURRICULAR ACHIEVEMENTS','Extra Curricular Activities','ExtraCurricular Activities','Extra-Curricular Activities','CO-/EXTRA – CURRICULAR  ACTIVITIES','INTERPERSONAL SKILL','Extra curriculars','Personal Skills','Co curricular Activities','Co-curricular Activities and interests','CO-CORRICULAR ACTIVITIES','co corricular activities']
    responsibility = ['POSITION OF RESPONSIBILITY','LEADERSHIP EXPERIENCE','Positions OF Responsibility','leadership experiences','responsibilities']
    certification = ['CERTIFICATIONS','earned certificates','certificates and awards','awards and rewards']

    objective = [s.replace("&","and").lower() for s in objective]
    academics = [s.replace("&","and").lower() for s in academics]
    experience = [s.replace("&","and").lower() for s in experience]
    publications = [s.replace("&","and").lower() for s in publications]
    skills = [s.replace("&","and").lower() for s in skills]
    personal_info = [s.replace("&","and").lower() for s in personal_info]
    achievements = [s.replace("&","and").lower() for s in achievements]
    interests = [s.replace("&","and").lower() for s in interests]
    #languages = [s.replace("&","and").lower() for s in languages]
    projects = [s.replace("&","and").lower() for s in projects]
    declaration = [s.replace("&","and").lower() for s in declaration]
    internships = [s.replace("&","and").lower() for s in internships]
    details = [s.replace("&","and").lower() for s in details]
    courseWork = [s.replace("&","and").lower() for s in courseWork]
    publications = [s.replace("&","and").lower() for s in publications]
    extracurriculars = [s.replace("&","and").lower() for s in extracurriculars]
    responsibility = [s.replace("&","and").lower() for s in responsibility]
    certification = [s.replace("&","and").lower() for s in certification]

    main_ext = objective+academics+experience+publications+internships+skills+personal_info+achievements+interests+projects+declaration+details+courseWork+publications+extracurriculars+responsibility+certification

    aca_dict = {}
    aca_dict['objective'] = objective
    aca_dict['academics'] = academics
    aca_dict['experience'] = experience
    aca_dict['publications'] = publications
    aca_dict['skills'] = skills
    aca_dict['personal_info'] = personal_info
    aca_dict['achievements'] = achievements
    aca_dict['interests'] = interests
    aca_dict['projects'] = projects
    aca_dict['declaration'] = declaration
    aca_dict['internships'] = internships
    aca_dict['details'] = details
    aca_dict['courseWork'] = courseWork
    aca_dict['publications'] = publications
    aca_dict['extracurriculars'] = extracurriculars
    aca_dict['responsibility'] = responsibility
    aca_dict['certification'] = certification

    return main_ext,aca_dict
main_ext,aca_dict = headline_text_extract()
def get_flat_list():
    init1 = {
    'mini_project' : ['indiplomacourse','indiplomacourseproject','becourse','becourses','befinalcourse','befinalyearcourse','inbefinalyear','indiplomafinalyear','finalyearproject','finalproject','meproject','mefinalproject','finalproject(be)','beproject','diplomaproject','miniproject',"miniprojects","projects","projecttitles"],
    'proj_headline' : ["project","projecttitle","titleofproject","titleoftheproject","project-1","project-2","project-3","project-4","project-5","project-6","project-7","project-8","project-9","project-10","project-11","project-12","project-13","project-14","project-15","project-16","project-17","project-18","project-19","project-20",'nameoftheproject','projectname',"nameofproject","nameofprojects","projectsname","nameofprojects","projectinstatistics","statisticsproject"],
    'proj_duration' : ['projectduration',"duration","timeduration","timerange","durationoftheproject"],
    'proj_descript' : ['projectdescription',"descriptionoftheproject","abstract","summary","detailsoftheproject","projectdetails","projectdetails"],

    'pos' : ['scientist','engineer','scholor','intern','executive','senior','statistician','scientist','datascientist','architect','manager','maker','analyst','expert','leader','manager'],
    'company_name' : ['nameoftheorganization','nameofthecompany','nameofthestartup','nameofcompany','nameoforganization','nameofstartup','companyname','organizationname','company','organization','startup'],
    'designation' : ['positioninthecompany','roleinthecompany','designationinthecompany','roleincompany','designationincompany','positionincompany','nameoftheposition','nameofthedesignation','nameoftherole','nameofposition','nameofdesignation','nameofrole','positionname','designationname','rolename','designation','role','position','employment'],
    'duration' : ['duration/tenure','time/duration','duration','tenure','timeduration'],
    'hackathons' : ['hackathons','hackathon','codathon','competition','challenge','participated','participant','participation','coordinator','coordinated']
    }
    
    return init1

def get_skills_list():
    skills_list = {
    'ms_office' : ['Ms-Office','MsOffice','Msoffice','Ms-office','Ms Office','ms office','Word', 'Excel', 'Powerpoint', 'Outlook', 'Access', 'OneNote'],
    'operating_systems' : ['windows','mac','linux','ubuntu','UNIX','symbian','Android','FreeBSD','OpenBSD','JavaOS','Xandros Linux','Red Hat Linux','Zorin','Elementary OS','Macintosh','Slackware','Gentoo','Debian','Chromium','iOS','openSUSE','DOS','AmigaOS'],
    'google_drive' : ['Docs', 'Sheets', 'Forms', 'Slides'],
    'writing' : ['WordPress', 'SEO', 'Yoast', 'journalism', 'technical writing', 'ghostwriting'],
    'spreadsheets' : ['Excel', 'Google Sheets', 'OpenOffice','comparative analyses', 'pivot tables', 'macros', 'link to database', 'vertical lookups'],
    'social_media' : ['Facebook', 'Twitter', 'LinkedIn','Instagram', 'posts', 'giveaways', 'customer interaction'],
    'productivity' : ['Trello', 'Slack', 'Asana', 'Todoist', 'Zapier', 'Basecamp'],
    'graphical' : ['Photoshop', 'Illustrator', 'InDesign', 'Acrobat', 'Free Hand', 'Corel Draw'],
    'web_tech' : ['HTML, CSS, Javascript, WordPress, Content Management Systems','cms','JQUERY','CoffeeScript','VBScript','Silverlight'],
    'enterprise_systems' : ['Payment Processing', 'Automated Billing Systems','Customer Relationship Managemen','CRM','Oracle Netsuite','Salesforce', 'Business Continuity Planning', 'Enterprise Resource Planning','ERP','sap','oracle'],
    'math_skills' : ['Basic math', 'arithmetic', 'statistics', 'algebra', 'trigonometry', 'geometry', 'calculus'],
    'computer_skills' : ['MS Office', 'Google Drive', 'spreadsheets', 'PowerPoint', 'databases', 'enterprise systems'],
    'programming_skills' : ['Visual Basic','mysql','kotlin','rust','Scheme','Erlang','Scala','Elixir','Haskell','PostgreSQL','C#','SQL', 'Java', 'C++','cpp','swift','JavaScript', 'XML','TypeScript', 'Perl', 'Python', 'PHP', 'Objective-C', 'AJAX', 'ASP.NET', 'Ruby'],
    'frameworks':['Tableau','django','flask','jupyter notebook','spyder','netbeans','eclips','aws','colab'],
    'concentrate' : ['R','C','go'],
    'soft_skills' : ['Communication','Work Under Pressure','Decision Making','Time Management','Self motivation','Conflict Resolution','Leadership','Adaptability','Teamwork','Creativity','analytical','adaptable','quick learner','loyal','discreet','flexible','resposible','operate under pressure','multi tasking']
    }

    # it has all skill tokens from every category...
    flat_skills_list = []
    for sublist in list(skills_list.values()):
        for item in sublist:
            flat_skills_list.append(item.strip().lower().replace("-",""))

    return flat_skills_list

def get_edu_background():
    edu_back = {
    'edu_phd' : ['Doctorate', 'PhD', 'Ph.D'],
    'edu_mtech' : ['MTech', 'M.E.', 'M.Tech','m-tech','postgraduate'],
    'edu_btech' : ['tech','Bachelor','Bachelor of Engineering','bs','graduate','undergraduate','graduate student','b.e.','B.E','be.','b-tech','btech', 'bachelors', 'bachelorsofengineering','be','graduation'],
    'edu_hsc' : ['Diploma','h.s.c','puc','preuniversitycourse','12"','12th','XII','HSC','highersecondary'],
    'edu_ssc' : ['.S.C','S.C','$.S.C','S.S.C.','s.s.c','10"','10th', 'X', 'Matric', 'SSC','secondary'],
    'edu_dip' : ['CDAC', 'PGDBM','diploma','polytechnic'],
    'edu_branches' : ['Mechanical','mech','Instrumentation','Civil','cse','computer','ece','eee','mme']
    }

    return edu_back

def skills_extraction(data_string):
    fl_skills_list = get_skills_list()
    all_skills = []
    for i in data_string:
        for j in i.lower().split():
            if(j not in invalidChars):
                w_token = j.replace(",","").strip().replace("-","")
                if(w_token in fl_skills_list and w_token.capitalize() not in all_skills):
                    all_skills.append(w_token.capitalize())
    return all_skills

## Utility Functions
def remove_suffix_symbols(str1):
    for sym in str1.strip():
        if(sym in symbols_log and str1.startswith(sym)):
            str1 = str1.replace(sym,"",1)
        else:
            return str1.strip()

def listToString(s):  
    str1 = ""  
    for ele in s:  
        str1 += " "+ele   
    return str1  
def Remove_duplicates(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num)
    return final_list
def update(headline,recent):
    if(headline in main_ext):
        value,key = occur_headline(headline)
        print(value,key)
        if(recent != key):
            dict1[key] = value
def is_date(string, fuzzy=False):
    try: 
        d1 = parse(string, fuzzy=fuzzy)
        #print(d1.year,d1.month)
        return True,d1

    except ValueError:
        return False,False
def find_next_index(area_name,dict1):
    #print(dict1)
    index = list(dict1.keys()).index(area_name)
    #print(area_name+" index: "+str(index))
    start = dict1[area_name]
    #print(area_name+" index: ",str(start))
    try:
        next_val = list(dict1.values())[index+1]
        #print("next element value: ",next_val)
    except:
        next_val = False
    return index,start,next_val
#find_next_index("achievements",dict1)
def data_process(overall_text):
    rl,proj_copy = [],[]
    #def make_replacements():
    #print(overall_text)
    #print('''###########################''')
    #print(overall_text.splitlines())
    #print("(************************)")
    for s in overall_text.splitlines():
        if(len(s)!= 0 and s!= None):
            #print(s)
            #s = s.replace('&',"and")
            proj_copy.append(s.strip()) 
            s = remove_suffix_symbols(s)
            rl.append(s)
    #print(")***************************(")in_file.replace("."+in_file.split('.')[-1],".txt"), "r")

    return rl,proj_copy
def zero_selects(zero_list):
    new_l = []
    for lk in zero_list:
        if(lk.strip()):
            #print(lk.split("\n"))
            if(len(lk.split("\n"))>1):
                new_l.append(lk.split("\n")[1])
            else:
                new_l.append(lk.split("\n")[0])
    return new_l

def for_case_1(str1):
   # print("string: ",str1)
    match_count = 0
    cases = [company_name,designation]
    case_names = ['Company Name',"Designation"]
    for case_name,case in zip(case_names,cases):
        for i in case:
            prep = remove_suffix_symbols(str1).lower().replace(" ","").strip()
            #print(prep,i)
            if(prep.startswith(i)):
                match_count +=1
                match_word = i
                break
        if(match_count != 0):
            break
    str2 = str1
    if(match_count!=0):
        for i in str1.strip().split():
            #print(i)
            #print(remove_suffix_symbols(i).lower())
            if(remove_suffix_symbols(i).lower() in match_word):
                str2 = str2.replace(i,"",1)
        return case_name,str2.strip()
    else:
        return "Nothing","Nothing"
#for_case_1("Role in the company Clove Technologies")
#zero_selects(proj_splitted_list)

#Remove Numbers
def remove(list): 
    pattern = '[0-9]'
    list = [re.sub(pattern, '', i) for i in list] 
    return list

# Remove All Symbols
def remove_symb(string):
    string = string.replace("&"," and ")
    for i in invalidChars:
        if(i in string):
            string = string.replace(i," ")
    return string

# Remove All Symbols Except numbers
def remove_symb_except_numbers(string):
    string = string.replace("&"," and ")
    for i in invalidChars:
        if(i != '.'):
            if(i in string):
                string = string.replace(i," ")
        else:
            pass
    return string

# import win32com.client as win32
# from win32com.client import constants
#word = win32.Dispatch("Word.Application")
#word.visible = 0

def save_as_docx(path):
    # Opening MS Word
    print("path: ",path)
    word = win32.gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(path)
    doc.Activate()

    # Rename path with .docx
    new_file_abs = os.path.abspath(path)
    new_file_abs = re.sub(r'\.\w+$', '.docx', new_file_abs)

    # Save and Close
    word.ActiveDocument.SaveAs(
        new_file_abs, FileFormat=constants.wdFormatXMLDocument
    )
    doc.Close(False)

# import doc2text
# def doc_to_text(path):
#     doc = doc2text.Document()
#     doc = doc2text.Document(lang="eng")
#     doc.read(path)
#     doc.process()
#     doc.extract_text()
#     text = doc.get_text()
#     return text
def doc_to_pdf(file_location,folder):
    #print("file location: ",file_location)
    os.system("sudo lowriter --convert-to pdf --outdir {}/ {}".format(folder, file_location))
def docx_to_text(filename):
    #print("filename: ",os.getcwd()+"/"+filename)
    file_ext = filename.split(".")[-1]
    #print("file Extensions: ",file_ext)
    if(file_ext == 'doc'):
        data = doc_to_text(os.getcwd()+"/"+filename)
        #save_as_docx(os.getcwd()+"/"+filename)
        # in_file = os.path.abspath(filename)
        # wb = word.Documents.Open(in_file)
        #filename = filename.split('.')[0]+".docx"
        # out_file = os.path.abspath(filename)
        # wb.SaveAs2(out_file, FileFormat=16) # file format for docx
        # wb.Close()
        #print(data)
        return data
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        print(para.text)
        fullText.append(para.text)
    data = listToString(fullText)
    #print(data)
    return data

def get_jd_data(temp_folder_name,jd_dir,filename,is_jd):
    # print(">>Temp_folder_name:{}\n>>jd_dir:{}\n>>filename:{}".format(temp_folder_name,jd_dir,filename))
    filename = filename.split("/")[-1]
    ext_name = str(filename).split(".")[-1]
    file_name = str(filename).replace("."+ext_name,"")

    file_name = re.sub(r'[^\w]', ' ', file_name).replace(" ","_")
    filename = file_name+"."+ext_name
    # print("filename(jd data): ",filename)
    '''
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    data = listToString(fullText)
    '''
    in_file = jd_dir+"/"+filename
    ext = filename.split('.')[-1]
    if(is_jd):
        directory = "media/"+temp_folder_name
    else:
        directory = "media/"+temp_folder_name+"/resumes/"
    in_file = directory+"/"+filename
    f_out = in_file.replace("."+in_file.split('.')[-1],".txt")
    if(ext == 'pdf'):
        # print("file_in: {},file_out: {}".format(in_file,f_out))
        os.system("sudo pdftotext {} {}".format(in_file,f_out))
    elif(ext in ['doc','docx']):
        # print("Entered in elif>>>>>>>>>")
        # print("jd_dir: {}\nin_file:{}".format(jd_dir,in_file))
        os.system("sudo libreoffice --headless --convert-to 'txt:Text (encoded):UTF8' --outdir {} {}".format(directory,in_file))
    else:
        print("File Extension is Not Supported...")
    f = open(f_out, "r")
    data = f.read()
    #print(data)

    n_skills = skills_extraction(data.split())
    n_deg = edu_highest_degree(data.split())
    jd_data = []
    data = data.replace("&", ' and ').replace("/",' and ')
    for i in data.split():
        if(not nlp.vocab[i].is_stop):
            if(not i[-1:].isalpha()):
                i = i=i[:-1]
            jd_data.append(i.strip())
    
    remove_tags = ['SPACE','VERB','ADP','ADV','ADJ']
    remove_words = ['job','ability','passion','success','requirements','knowledge','skill','description']
    final_list = []
    jd_data = [lemmatizer.lemmatize(i.lower()) for i in jd_data]

    jd_data1 = Remove_duplicates(jd_data)
    jd_data2 = listToString(jd_data1)
    doc = nlp(jd_data2)
    for ent in doc:
        if(ent.pos_ not in remove_tags and str(ent).lower() not in remove_words):
            final_list.append(str(ent.text))
    return data,final_list,n_skills,n_deg

def key_processing(data_file):
    main=[]
    dict1 = {}
    recent,key = True,False
    for en,i in enumerate(data_file):
        i = remove_symb(i)
        if(i.endswith(":")):
            i = i[:-1]
        l1 = i.split()
        #print(i)
        #print(l1)
        l1 = remove(l1)#remove all numbers from the list
        l2 = []
        #if()
        for j in l1:
            if(j.strip() and len(j)>=2):
                if((nlp.vocab[j.strip()].is_stop or j.strip() in invalidChars) and j.strip().lower() != "be"):
                    pass
                else:
                    #print(j.strip())
                    l2.append(j.strip())
        if(len(l2)>0):
            main.append(l2)
            #print(l2)
            headline = listToString(l2).strip().lower()
            #print(headline)
            if(headline in main_ext):
                value,key = occur_headline(en,headline)
                #print(headline)
                #print(value,key)
                if(recent != key):
                    dict1[key] = value
                if(recent != key):
                    recent = key
                    dict1[key] = value
    return main,dict1
#key_processing(rl)

# Except Numbers
def key_processing_numbers(data_file):
    main=[]
    dict1 = {}
    recent,key = True,False
    for en,i in enumerate(data_file):
        #print(i)
        i = remove_symb_except_numbers(i)
        if(i.endswith(":")):
            i = i[:-1]
        l1 = i.split()
        #print(i)
        #print(l1)
        #l1 = remove(l1)#remove all numbers from the list
        l2 = []
        #if()
        for j in l1:
            if(j.strip() and len(j)>=2):
                if((j.strip() in invalidChars) and j.strip().lower() != "be"):
                    pass
                else:
                    #print(j.strip())
                    l2.append(j.strip())
        if(len(l2)>0):
            main.append(l2)
            #print(l2)
            headline = listToString(l2).strip().lower()
            #print(headline)
            if(headline in main_ext):
                value,key = occur_headline(en,headline)
                #print(headline)
                #print(value,key)
                if(recent != key):
                    dict1[key] = value
                if(recent != key):
                    recent = key
                    dict1[key] = value
    return main,dict1
#key_processing_numbers(rl)
'''
def key_processing_bk(data_file):
    print(data_file)
    dict1 = {}
    recent,key = True,False
    tokens_list = []
    for en,sent in enumerate(data_file):
        #print(">>>",sent)
        while(True):
            if(sent == None or len(sent) == 0):
                break
            elif((not sent[-1].isalpha()) and (not sent[-1].isnumeric())):
                sent = sent[:-1]
                #print(sent)
            elif((not sent[0].isalpha()) and (not sent[0].isnumeric())):
                sent = sent[1:]
                #print(sent)
            else:
                #print("<<",sent)
                break
        if(sent == None or len(sent) == 0):
            continue
        #if("-" in sent):
        #    sent.replace('-'," ")
        if('&' not in sent):
            sent = sent.replace(":"," ").strip().replace("/"," ")
            word_tokens = word_tokenize(sent) 
            while(True):
                try:
                    if(word_tokens[0] in invalidChars):
                        word_tokens.pop(0)
                    elif(word_tokens[0] in nums):
                        word_tokens.pop(0)
                    elif(word_tokens[0] in symbols_log):
                        word_tokens.pop(0)
                    else:
                        break
                except:
                    break
            #print(word_tokens)
            tokens_list.append(word_tokens)
            if(len(word_tokens)<=3):
                headline = listToString(word_tokens).strip().lower()
                #print(headline)
                #print(main_ext)
                #print(headline.strip() in main_ext)
                #if(headline.strip() in main_ext):
                #    print(en,headline)
                if(headline in main_ext):
                    value,key = occur_headline(en,headline)
                    #print(word_tokens)
                    print(value,key)
                    if(recent != key):
                        dict1[key] = value
            else:
                headline = listToString(word_tokens).lower().strip()
                if(headline in main_ext):
                    value,key = occur_headline(en,headline)
                    #print(word_tokens)
                    print(value,key)
                    if(recent != key):
                        dict1[key] = value
                elif(len(word_tokens)<5):
                    headline = word_tokens[0].lower().strip()
                    if(headline in main_ext):
                        value,key = occur_headline(en,headline)
                        #print(word_tokens)
                        print(value,key)
                        if(recent != key):
                            dict1[key] = value
                    #print(word_tokens)
        else:
            l2 = sent.split('&')
            headline = l2[0].strip().lower()
            if(headline in main_ext):
                value,key = occur_headline(en,headline)
                print(value,key)
                if(recent != key):
                    dict1[key] = value
        if(key):
            recent = key
    return tokens_list,dict1
#key_processing_bk(rl)
'''
def key_processing_bk(data_file):
    #print(data_file)
    dict1 = {}
    recent,key = True,False
    tokens_list = []
    print("\t\tLine Number\t\t\tHeadline")
    print("\t\t---------\t\t--------")
    for en,sent in enumerate(data_file):
        #print(">>>",sent)
        #sent = listToString(sent)
        #print("@>>",sent)
        while(True):
            if(sent == None or len(sent) == 0):
                #print("sent: ",sent)
                break
            elif(not sent[-1].isalpha()):
                sent = sent[:-1]
                #print("sent: ",sent)
            elif(not sent[0].isalpha()):
                sent = sent[1:]
                #print("sent: ",sent)
            else:
                #print("<<",sent)
                break
        if(sent == None or len(sent) == 0):
            continue
        #if("-" in sent):
        #    sent.replace('-'," ")
        if('&' not in sent):
            sent = sent.replace(":"," ").strip().replace("/"," ")
            word_tokens = word_tokenize(sent) 
            while(True):
                try:
                    if(word_tokens[0] in invalidChars):
                        word_tokens.pop(0)
                    elif(word_tokens[0] in nums):
                        word_tokens.pop(0)
                    elif(word_tokens[0] in symbols_log):
                        word_tokens.pop(0)
                    else:
                        break
                except:
                    break
            #print(word_tokens)
            tokens_list.append(word_tokens)
            if(len(word_tokens)<=3):
                headline = listToString(word_tokens).strip().lower()
                if(headline in main_ext):
                    value,key = occur_headline(en,headline)
                    #print(word_tokens)
                    print("\t\t",value,"\t\t",key)
                    if(recent != key):
                        dict1[key] = value
            else:
                headline = listToString(word_tokens).lower().strip()
                if(headline in main_ext):
                    value,key = occur_headline(en,headline)
                    #print(word_tokens)
                    print("\t\t",value,"\t\t",key)
                    if(recent != key):
                        dict1[key] = value
                elif(len(word_tokens)<5):
                    headline = word_tokens[0].lower().strip()
                    if(headline in main_ext):
                        value,key = occur_headline(en,headline)
                        #print(word_tokens)
                        print("\t\t",value,"\t\t",key)
                        if(recent != key):
                            dict1[key] = value
                    #print(word_tokens)
        else:
            l2 = sent.split('&')
            headline = l2[0].strip().lower()
            if(headline in main_ext):
                value,key = occur_headline(en,headline)
                print("\t\t",value,"\t\t",key)
                if(recent != key):
                    dict1[key] = value
        if(key):
            recent = key
    #print(dict1)
    return tokens_list,dict1
#key_processing_bk(rl)

def keyword_extract(project_list):
    f1 = []
    for num,i in enumerate(project_list):
        #print(i.split())
        l1 = i.split()
        for n,sent in enumerate(l1):
            #print(j)
            while(True):
                if(len(sent) == 0):
                    break
                elif((not sent[-1].isalpha()) and (not sent[-1].isnumeric())):
                    sent = sent[:-1]
                    #print(sent)
                elif((not sent[0].isalpha()) and (not sent[0].isnumeric())):
                    sent = sent[1:]
                    #print(sent)
                else:
                    break
            if(sent.strip()):
                f1.append(sent)
    #print(f1)
    remove_tags = ['SPACE','VERB','ADP','ADV','ADJ']
    remove_words = ['job','ability','passion','success','requirements','knowledge','skill','description']
    data_res = []
    jd_data = [lemmatizer.lemmatize(i.lower()) for i in f1]

    jd_data1 = Remove_duplicates(jd_data)
    jd_data2 = listToString(jd_data1)
    doc = nlp(jd_data2)
    for ent in doc:
        if(ent.pos_ not in remove_tags and str(ent).lower() not in remove_words):
            data_res.append(ent)
    return data_res

def find_proj_list(project_tokens):
    #print("project Tokens: >>\n",project_tokens)
    init = 0
    symbol,colon,num_iteration = False,False,False
    init1 = get_flat_list()

    for ind,i in enumerate(project_tokens):
        if(len(i)>1):
            #print(i)
            i = i.lower()
            i = i.replace("guide:","").replace("instructor:","").strip()
            if(i.strip()):
                str1 = remove_suffix_symbols(i).strip().lower().replace(" ","") 
                str1 = str1.replace(".","")
                ok = True
                for el in init1['mini_project']:
                    #print(el,str1)
                    if(el in str1):
                        ok = False
                        break
                if(ok):
                    #print(str1,mini_project)
                    if((i.strip()) and (str1 not in init1['mini_project'])):
                        if(i.strip().split()[0] in symbols_log):
                            symbol = True
                    if(i.endswith(":")):
                        if(":" in i[:-1]):
                            colon = True
                    if(":" in i):
                        colon = True
                    break
        if(not symbol):
            symb = [')','>','.','=>']
        
            i = project_tokens[ind]
            for s in symb:
                if(i.strip().startswith("1"+s)):
                    num_iteration = True
                    num_value = 1
                    num_symb = s
                    break
                elif(i.strip().startswith("0"+s)):
                    num_iteration = True
                    num_value = 0
                    num_symb = s
                    break

    print("Symbol:{}, Colon:{}, NumIteration:{}".format(symbol,colon,num_iteration))    
    proj_count = 0
    
    #print(project_tokens)
    #for i in project_tokens:
    val = 0
    init_length = len(project_tokens)
    main_count = 0
    
    while(True):
        if(init_length == main_count):
            break
        main_count+=1
        try:
            i = project_tokens[val]
        except:
            break
        #i = i.lower()
        i = i.replace("Guide:","").replace("Instructor:","").strip()
        #print(i)
        #assert(False)
        if(i.strip()):
            if(symbol and colon):
                #print(i.strip().split()[0].replace(".",""))
                if(i.endswith(":")):
                    i = i[:-1]#remove last character ":" value (because it ends with ":")
                syc = remove_suffix_symbols(i).strip().split(":")
                check_mini = syc[0].strip().lower().replace(".","").strip().replace(" ","")
                #print(check_mini,mini_project)
                if(check_mini in init1['mini_project']):
                    #print(project_tokens[val])
                    del project_tokens[val]
                    continue
                #print("checkmini: ",check_mini)
                if(i.strip().split()[0].replace(".","") in symbols_log and ":" in i.strip()):
                    if(syc[0].strip().isupper() and check_mini not in init1['mini_project']):
                        proj_count+=1
                        print("{}) {}".format(proj_count,syc[1].strip()))
                        val+=1
                    elif(syc[0].strip().lower().replace(" ","") in init1['proj_headline'] and check_mini not in init1['mini_project']):
                        proj_count+=1
                        print("{}) {}".format(proj_count,syc[1].strip()))
                        val+=1
                        #continue
                        #pname = i.replace("e","",1).strip()
                        #pname = i.replace("@","",1).strip()
                        #f1 = pname.strip().lower().replace(" ","").split(":")[0]
                        #if(f1 in proj_headline):
                else:
                    st = remove_suffix_symbols(i)
                    #print(st)
                    if(check_mini not in init1['mini_project']):
                        if((st.strip().split()[0].isupper()) or (st.strip().split()[0] in symbols_log)):
                            proj_count+=1
                            print("{}) {}".format(proj_count,remove_suffix_symbols(i)))
                            val+=1
            elif(symbol):
                #if(":" in i):
                if((i.strip().split()[0].isupper()) or (i.strip().split()[0] in symbols_log)):
                    #print(i)
                    proj_count+=1
                    print("{}) {}".format(proj_count,remove_suffix_symbols(i)))
                    val+=1
            elif(colon):
                #print(i)
                #assert(False)
                init = 1
                if(i.strip().endswith(":")):
                    i = i.strip()[:-1]
                if(":" in i.strip()):
                    l1 = i.replace(".","").strip().split(":")
                    #print(l1)
                    
                    if(l1[0].strip().isupper() or l1[0].strip().capitalize()):
                        if(l1[0] in init1['proj_headline']):
                            proj_count+=1
                            task_headline = l1[1].strip()
                            print("{}) {}".format(proj_count,task_headline))
                    if(l1[0].strip() and len(l1[0].strip())>1):
                        name = l1[0].strip().lower().replace(" ","") 
                        #print(name)
                        #assert(False)
                        if(name in init1['proj_headline']):
                            proj_count+=1
                            task_headline = l1[1].strip()
                            print("{}) {}".format(proj_count,task_headline))
                        #elif(name in proj_duration):
                        #    task_headline = l1[1].strip()
                        #    print("Project Duration: ",task_headline)
                        else:
                            #colon = False
                            pass
            elif(num_iteration):
                st_comp = str(num_value)+num_symb
                if(i.strip().startswith(st_comp)):
                    proj_count+=1
                    print("{}) {}".format(proj_count,i.strip()[len(st_comp):]))
                    num_value+=1
                    val+=1
            else:
                ## Check for num_iteration condition
                symb = [')','>','.','=>']
                
                sy1 = False
                for s in symb:
                    if(i.strip().startswith("1"+s) or i.strip().startswith("0"+s)):
                        sy1 = True
                        break
                if(sy1):
                    pass
                #===============================
                elif(i.strip().isupper()):
                    proj_count+=1
                    print("{}) {}".format(proj_count,i.strip()))
                    val+=1
                elif(" - " in i.strip()):
                    i = i.strip().split("-")[0]
                    if((len(i.strip().split()[0])>2) and (len(i.strip().split())>=3)):
                        proj_count+=1
                        print("{}) {}".format(proj_count,i.strip()))
                        val+=1
                elif((len(i.strip().split()[0])>1) and (len(i.strip().split())>=3)):
                    proj_count+=1
                    print("{}) {}".format(proj_count,i.strip()))
                    val+=1
                #print(i.strip().split())
                #assert(False)
        val+=1
    #print(proj_count)
    #if(proj_count == 0):
    #    #assert(False)
    #    loop+=1
    #    print("Loop: ",loop)
    #    if(loop==3):
    #        return 0
    #    new_list = zero_selects(proj_splitted_list)
    #    find_proj_list(new_list)
    #else:
    #    return proj_count 
    return proj_count
#loop = 0
#find_proj_list(project_tokens)

def find_exp_list(project_tokens):
    #print(project_tokens)
    init = 0
    symbol,colon,num_iteration = False,False,False
    
    for ind,i in enumerate(project_tokens):
        #print(i)
        if(i.strip()):
            str1 = remove_suffix_symbols(i).strip().lower().replace(" ","") 
            str1 = str1.replace(".","")
            ok = True
            for el in init1['mini_project']:
                #print(el,str1)
                if(el in str1):
                    ok = False
                    break
            if(ok):
                #print(str1,mini_project)
                if((i.strip()) and (str1 not in init1['mini_project'])):
                    if(i.strip().split()[0] in symbols_log):
                        symbol = True
                if(project_tokens[ind].endswith(":")):
                    if(":" in project_tokens[ind][:-1]):
                        colon = True
                elif(":" in project_tokens[ind]):
                    colon = True
                break
    symb = [')','>','.','=>']
    if(not symbol):
        vl = 0
        while(True):
            if(project_tokens[vl].strip()):
                break
            vl+=1
        i = project_tokens[vl]
        for s in symb:
            if(i.strip().startswith("1"+s)):
                num_iteration = True
                num_value = 1
                num_symb = s
                break
            elif(i.strip().startswith("0"+s)):
                num_iteration = True
                num_value = 0
                num_symb = s
                break

    print("Symbol:{}, Colon:{}, NumIteration:{}".format(symbol,colon,num_iteration))    
    proj_count = 0
    
    #print(project_tokens)
    #for i in project_tokens:
    val = 0
    init_length = len(project_tokens)
    main_count = 0
    update = False
    while(True):
        if(init_length == main_count):
            break
        main_count+=1
        try:
            i = project_tokens[val]
        except:
            break
        #print(i)
        if(i.strip()):
            #print(i)
            if(symbol and colon):
                #print(i.strip().split()[0].replace(".",""))
                if(i.endswith(":")):
                    i = i[:-1]#remove last character ":" value (because it ends with ":")
                syc = remove_suffix_symbols(i).strip().split(":")
                check_mini = syc[0].strip().lower().replace(".","").strip().replace(" ","")
                #print(check_mini,mini_project)
                if(check_mini in init1['mini_project']):
                    print(project_tokens[val])
                    del project_tokens[val]
                    continue
                #print("checkmini: ",check_mini)
                if(i.strip().split()[0].replace(".","") in symbols_log and ":" in i.strip()):
                    if(syc[0].strip().isupper() and check_mini not in init1['mini_project']):
                        proj_count+=1
                        print("{}) {}".format(proj_count,syc[1].strip()))
                    elif(syc[0].strip().lower().replace(" ","") in init1['proj_headline'] and check_mini not in init1['mini_project']):
                        proj_count+=1
                        print("{}) {}".format(proj_count,syc[1].strip()))
                        val+=1
                else:
                    st = remove_suffix_symbols(i)
                    #print(st)
                    if(check_mini not in init1['mini_project']):
                        if((st.strip().split()[0].isupper()) or (st.strip().split()[0] in symbols_log)):
                            proj_count+=1
                            print("{}) {}".format(proj_count,remove_suffix_symbols(i)))
                            val+=1
            elif(symbol):
                ## For cases Like ("Name of the Company Clove Technologies")
                tag,pp = for_case_1(remove_suffix_symbols(i))
                if(tag == "Nothing"):
                    if((i.strip().split()[0].isupper()) or (i.strip().split()[0] in symbols_log)):
                        proj_count+=1
                        data_string = remove_suffix_symbols(i)
                        print("{}) {}".format(proj_count,data_string))
                        val+=1
            elif(colon):
                init = 1
                if(i.strip().endswith(":")):
                    i = i.strip()[:-1]
                if(":" in i.strip()):
                    l1 = i.replace(".","").strip().split(":")
                    f1 = l1[0].lower().replace(" ","").strip()
                    if(remove_suffix_symbols(f1) in company_name):
                        proj_count+=1
                        print("Company Name: ",l1[1])
                    elif(remove_suffix_symbols(f1) in designation):
                        proj_count+=1
                        print("Position Name: ",l1[1])
        
            elif(num_iteration):
                st_comp = str(num_value)+num_symb
                if(i.strip().startswith(st_comp)):
                    proj_count+=1
                    print("{}) {}".format(proj_count,i.strip()[len(st_comp):]))
                    num_value+=1
                    val+=1
            else:
                capital = False
                if(i.strip().isupper()):
                    #cap
                    proj_count+=1
                    print("{}) {}".format(proj_count,i.strip()))
                    val+=1
                elif(" - " in i.strip()):
                    i = i.strip().split("-")[0]
                    #print(i)
                    if((len(i.strip().split()[0])>2) and (len(i.strip().split())>=3 and len(i.strip().split())<14) and (":" not in i.strip())):
                        proj_count+=1
                        print("{}) {}".format(proj_count,i.strip()))
                        val+=1
                elif((len(i.strip().split()[0])>2) and (len(i.strip().split())>=3 and len(i.strip().split())<14) and (":" not in i.strip())):
                    proj_count+=1
                    print("{}) {}".format(proj_count,i.strip()))
                    val+=1
        val+=1
    if(proj_count == 0):
        new_list = zero_selects(copy_data[start+1:next_index])
        find_exp_list(new_list)

#find_exp_list(copy_data[start+1:next_index])

def getPhone(inputString):
    number = None
    try:
        pattern = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
        match = pattern.findall(inputString)
        match = [re.sub(r'[,.]', '', el) for el in match if len(re.sub(r'[()\-.,\s+]', '', el))>6]
        match = [re.sub(r'\D$', '', el).strip() for el in match]
        match = [el for el in match if len(re.sub(r'\D','',el)) <= 15]
        try:
            for el in list(match):
                if len(el.split('-')) > 3: continue # Year format YYYY-MM-DD
                for x in el.split("-"):
                    try:
                        if x.strip()[-4:].isdigit():
                            if int(x.strip()[-4:]) in range(1900, 2100):
                                match.remove(el)
                    except:
                        pass
        except:
            pass
        number = match
    except:
        pass

    if(len(number)!=0):
        return str(number[0])
    else:
        return 'No'
def candidate_name_extractor(input_string, nlp):

    doc = nlp(input_string)

    # Extract entities
    doc_entities = doc.ents
    #print(doc_entities)
    #assert(False)
    # Subset to person type entities
    doc_persons = filter(lambda x: x.label_ == 'PERSON', doc_entities)
    doc_persons = filter(lambda x: len(x.text.strip().split()) >= 2, doc_persons)
    doc_persons = map(lambda x: x.text.strip(), doc_persons)
    doc_persons = list(doc_persons)

    # Assuming that the first Person entity with more than two tokens is the candidate's name
    if len(doc_persons) > 0:
        return doc_persons[0]
    return "NOT FOUND"
def term_match(string_to_search, term):
    try:
        regular_expression = re.compile(term, re.IGNORECASE)
        result = re.findall(regular_expression, string_to_search)
        if len(result) > 0:
            return result[0]
        else:
            return None
    except Exception:
        print('Error occurred during regex search')
        return None
def transform(observations, nlp):
    # Extract candidate name
    observations['candidate_name'] = observations['text'].apply(lambda x: candidate_name_extractor(x, nlp))
    # Extract contact fields
    observations['email'] = observations['text'].apply(lambda x: term_match(x, EMAIL_REGEX))
    observations['phone'] = observations['text'].apply(lambda x: getPhone(x))
    return observations, nlp
def extract_personal_details(main_text_data):
    #observations = extract()
    nlp = spacy.load('en_core_web_sm') #spacy.load("en")
    
    observations = {}
    observations['text'] = [main_text_data]
    observations = pandas.DataFrame(data=observations['text'], columns=['text'])
    # Transform data to have appropriate fields
    observations, nlp = transform(observations, nlp)
    return observations

def doc_2_pdf(in_dir,out_dir):
    subprocess.call("lowriter --convert-to pdf {} --outdir {}".format(in_dir,out_dir))

def doc_2_pdf_bk(dirname):
    #import comtypes.client
    #import comtypes

    print("dirname(doc_2_pdf): ",os.getcwd()+"/media/"+dirname+"/resumes/*")
    files = glob.glob(os.getcwd()+"/media/"+dirname+"/resumes/*")
    print(files)
    print("==========")
    #curr_dir = 
    wdFormatPDF = 17
    for in_file in files:
        spl = in_file.split(".")[-1]
        name = in_file.split("/")[-1].split(".")[0]
        spl1 = in_file.split("/")[0]
        if(spl != "pdf"):
            word = comtypes.client.CreateObject('Word.Application')
            word.Visible = True
            time.sleep(3)
            
            out_file = os.getcwd()+"/media/"+dirname+"/resumes/"+name+'.pdf'
            # print out filenames
            print("*&* ",in_file)
            print("*&*",out_file)

            # convert docx file 1 to pdf file 1
            doc=word.Documents.Open(in_file) # open docx file 1
            doc.SaveAs(out_file, FileFormat=wdFormatPDF) # conversion
            doc.Close() # close docx file 1
            word.Visible = False
            word.Quit() # close Word Application
        else:
            pass
    print("=) done with converting doc2pdf!!!")

def pdf_to_jpg(inputpath,outputpath):
    #inputpath = r"resumes_pdf/Resume_9.pdf"
    #outputpath = r"resumes_images/"
    # To convert single page
    #result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="1")
    #print(result)

    # To convert multiple pages
    #result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="1,0,3")
    #print(result)

    # to convert all pages
    result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="ALL")
    print("=) done with *PDF to JPG* conversion")

def get_text_from_images(file_path):
    print("$$$: ",file_path)
    files = sorted(glob.glob(file_path+"/*"))
    print("&&&&&&&&&: ",files)
    m_text = ""
    for file in files:
        text1 = jpg_to_text(file)
        m_text = m_text+"\n\n"+text1
    #print(m_text)
    return m_text

def combine_all_images(file_path):
    print("filename(combine_all_images): ",file_path)
    print(file_path+"/*")
    files = sorted(glob.glob(file_path+"/*"))
    #print(files)
    #assert(False)
    print("filenames(combine all images): ",files)
    count = 0
    for file in files:

        if(count == 0):
            vis = cv2.imread(file)
            count=1
        else:
            img2 = cv2.imread(file)
            try:
                vis = np.concatenate((vis, img2), axis=0)
            except:
                pass
    cv2.imwrite(file_path+'/out.png', vis)
    print("=) done with *Combining Images*")
#combine_all_images("resumes_images/Resume_9.pdf_dir")

def jpg_to_text(file_path):
    t1 = time.time()
    files = glob.glob(file_path)
    orig_text = ""
    for file in files:
        #preprocessing
        image1=cv2.imread(file)
        img2=cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
        #bullets in the resume are represented by 'e'
        text2 = pytesseract.image_to_string(img2)
        orig_text+=text2.strip()+"\n\n"
    #overall_text
    print("=) done with *JPG to TEXT* conversion")
    print("elapsed time to extract text: {}\n".format(time.time()-t1))
    return orig_text
#jpg_to_text("out.png")

# Extracting Year and Month
def edu_year_month(data_link):
    dt_list = []
    dates = []
    for dt in data_link:
        dt = remove_suffix_symbols(dt)
        match = re.match(r'.*([1-3][0-9]{3})', dt)
        #print(match)
        if match is not None:
            #print(match.group(1))
            try:
                dt1 = is_date(dt,fuzzy=True)
            except:
                continue
            #print(">>",dt1)
            dl = []
            mn_text = dt.replace(match.group(1)," ")
            if(dt1[0]):
                #print("=> ",str(dt1[1]).split()[0])
                dates.append(str(dt1[1]).split()[0])
            else:
                #pass
                dates.append(str(match.group(1))+"-01-01")
        else:
            mn_text = dt
    #print(dates)
    dates.sort(key=lambda x: time.mktime(time.strptime(x,"%Y-%m-%d")))
    #print("Month\tYear")
    #print("===============")
    for d in dates:
        mn = d.split("-")
        year,month = mn[0],calendar.month_name[int(mn[1])]
        print(month[:3],"\t",year)
#edu_year_month(copy_data)

# Extracting *Highest Degree*
def edu_highest_degree(data_link):
    init1 = get_edu_background()
    edu_qual = [init1['edu_phd'],init1['edu_mtech'],init1['edu_btech'],init1['edu_dip'],init1['edu_hsc'],init1['edu_ssc']]
    edu_names = ["PhD","MTech","BTech","Diploma","HSC","SSC"]
    hd_num,high_degree = [],[]

    m_string,_ = key_processing_numbers(data_link)

    for num,ed in enumerate(edu_qual):
        ed = [i1.lower() for i1 in ed]
        #print(ed)
        count = 0
        for i in ed:
            for n,j in enumerate(m_string):
                j = [j1.lower() for j1 in j]
                #print(j)
                if(i in j):
                    count = 1
                    #print(i,"",j)
                    break
            if(count!=0):
                #print(">>>>>updated")
                high_degree.append(edu_names[num])
                hd_num.append(n)
                break
            #assert(False)
    #print("Highest Degree")
    #print("================")
    #for i,j in zip(hd_num,high_degree):
    #    print(i," =>\t",j)
    return high_degree
#edu_highest_degree(copy_data)

def edu_marks(data_link):
    #print("Marks")
    #print("================")

    # For detecting Marks [CGPI & percentage]
    app = ["appearing","appear","ongoing","going on","going","not completed"]
    appear = True
    ment_ind,marks = [],[]
    for ind,dta in enumerate(data_link):
        #print(dta)
        for i1 in app:
            if(i1.strip().lower() in dta.lower() and appear):
                #print(ind," ==> ","On Going")
                ment_ind.append(ind)
                marks.append("On Going")
                appear = False
        l1_nums = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", dta)
        ment = []
        #print(l1_nums)
        if(len(l1_nums)>0 and len(l1_nums[0].replace('.','').strip())>1):
            #print(l1_nums)
            for num,k in enumerate(l1_nums):
                #print(k)
                if(k.strip().startswith("-")):
                    #print(len(k.replace("-","").strip()))
                    if(len(k.replace("-","").strip())==2):
                        l1_nums[num] = "20"+k.strip()[1:]
                elif(k.strip().startswith("0") and len(k.strip())==3):
                    l1_nums[num] = "2"+k.strip()
                #print(l1_nums)
                k = l1_nums[num]
                match = re.match(r'.*([1-5][0-9]{3})', k)
                #print(match)
                if(match is None):
                    nn = ""
                    k = k.strip()
                    if(k.strip().startswith('0') or k.strip().startswith('1') or k.strip().startswith('3')):
                        pass
                    else:
                        for n,i in enumerate(k):
                            if(i not in stop_symbols):
                                #ment.append(k)
                                break
                            else:
                                #print("***",k,i)
                                k = k.replace(i,"")
                                #ment.append(k)
                                #print(k)
                        if(len(k)>=2):
                            ment.append(k)
                            ment
            if(len(ment)!=0):
                marks.append(ment)
                ment_ind.append(ind)

    #for i,j in zip(ment_ind,marks):
    #    print(i," => ",j)
    return marks

#obj,aca,exp,pub,inte,ski,per,ach,inter,proj,dec,det,cou,ext,res,cer = True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True
def occur_headline(en,headline):
    if(headline in aca_dict['objective']):
        return en,"objective"
    elif(headline in aca_dict['academics']):
        return en,"academics"
    elif(headline in aca_dict['experience']):
        return en,"experience"
    elif(headline in aca_dict['publications']):
        return en,"publications"
    elif(headline in aca_dict['internships']):
        return en,"internships"
    elif(headline in aca_dict['skills']):
        return en,"skills"
    elif(headline in aca_dict['personal_info']):
        return en,"personal_info"
    elif(headline in aca_dict['achievements']):
        return en,"achievements"
    elif(headline in aca_dict['interests']):
        return en,"interests"
    #elif(headline in aca_dict['languages']):
    #    return en,"languages"
    elif(headline in aca_dict['projects']):
        return en,"projects"
    elif(headline in aca_dict['declaration']):
        return en,"declaration"
    elif(headline in aca_dict['details']):
        return en,"details"
    elif(headline in aca_dict['courseWork']):
        return en,"courseWork"
    elif(headline in aca_dict['extracurriculars']):
        return en,"extracurriculars"
    elif(headline in aca_dict['responsibility']):
        return en,"responsibility"
    elif(headline in aca_dict['certification']):
        return en,"certification"
    else:

        return "Nothing","Nothing"
#occur_headline("2","dec")
#print(aca_dict.keys())
