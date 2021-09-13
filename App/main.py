## Import Libraries
from PIL import Image
#import pytesseract
#pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
import cv2,glob,time
import re,logging,os,sys
import numpy as np
import pandas
import pandas as pd
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
from . import utility_functions as util_fun

## Constants
stop_words = set(stopwords.words('english'))   
#invalidChars = set(string.punctuation.replace("_", ""))
invalidChars = set(string_func.punctuation)
nums = list(map(str,[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]))

## Stop Breaks
main_ext,aca_dict = util_fun.headline_text_extract()
edu_back = util_fun.get_edu_background()
#Get init List
init_list = util_fun.get_flat_list()
#Skills List
flat_skills_list = util_fun.get_skills_list()

## Utility Functions
symbols_log = ["e@","e","@","¢","_","—","°","|",]
def matching_words(l1,l2):
    #print("==============> Matching Words <================")
    match_count=0
    for i in l1:
        if(len(str(i))>2):
            if(str(i) in l2):
                #print(str(i))
                match_count+=1
    return match_count
def get_personal_info(main_text_data):
    # call this functioni to get personal details
    observations = util_fun.extract_personal_details(main_text_data)

    user_mail = observations['email'][0]
    user_phone = observations['phone'][0]

    #print("Email:\t",user_mail)
    #print("Phone:\t",user_phone)
    return user_mail,user_phone
#email,phone = get_personal_info()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Academics Details >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def academics_main(dict1,copy_data,final_data_jd,n_deg):
    ## If "no academics" Records found
    if "academics" not in list(dict1.keys()):
        data_link = copy_data[:min(dict1.values())]
    else:
        try:
            index,start,next_index = util_fun.find_next_index("academics",dict1)
            if(next_index):
                data_link = copy_data[start+1:next_index]
            else:
                data_link = copy_data[start+1:]
        except:
            data_link = copy_data

    #util_fun.edu_year_month(data_link)
    marks = util_fun.edu_marks(data_link)
    high_degree = util_fun.edu_highest_degree(data_link)

    ## Qualification
    degs = ["PhD","MTech","BTech","Diploma","HSC","SSC"]
    degs.reverse()
    if(len(high_degree)!=0):
        r1 = degs.index(high_degree[0])
        r2 = degs.index(n_deg[0])

        if(r1 == r2 and r1 == -1):
            edu_points = 0.2 
        elif(r1 == r2):
            edu_points = 0.5
        elif(r1<r2 or r1>r2):
            edu_points = 0.4
    else:
        edu_points = 0
    #print("Allotted Points for Academics: ",edu_points)

    ## Marks
    if(len(marks)!=0):
        if(not marks[0][0][0].isalpha()):
            marks_points = (int(str(round(float(marks[0][0])))[0])*10)/200
        else:
            marks_points = 0.3
    else:
        marks_points = 0.2  
    print("Allotted points for Marks: ",marks_points)

    aca_points = edu_points+marks_points
    print("\t\tAllotted points for Academics: \t\t\t\t{} out of {}".format(aca_points,1.0))
    return round(aca_points,2)
#aca_points = academics_main()
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Academics Details <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Accolades & Extracurricular Activities >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def ae_main(dict1,copy_data,final_data_jd):
    #print(">>>>>>>>>>>>>>>>>>>>>>>>>> Accolades & Extracurricular Activities <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    #flat_init = util_fun.get_flat_list()init_list
    try:
        index,start,next_index = util_fun.find_next_index("extracurriculars",dict1)
        if(next_index):
            data_link = copy_data[start+1:next_index]
        else:
            data_link = copy_data[start+1:]
    except:
        data_link = copy_data
    #print("data_link: ",data_link)
    hack_count = 0
    for num,i in enumerate(data_link):
        for j in i.split():
            if(j.lower() in init_list['hackathons']):
                if(not data_link[num][0].isalpha()):
                    #print(data_link[num])
                    hack_count+=1
                else:
                    if(data_link[num][0].isupper()):
                        #print(data_link[num])
                        hack_count+=1

                #doc = nlp(data_link[num])
                '''
                for ent in doc.ents:
                    print(ent)
                    if(ent.label_ == "ORG"):
                        #print("Organization Name: ",ent.text)
                        hack_count+=1
                    elif(ent.label_ == 'FAC'):
                        hack_count+=1
                        #print("Organization Name: ",ent.text)
                '''
                break
    # Total Links present in the Resume
    social_count = 0
    web_links = []
    for str1 in copy_data:
        myString = str1
        #print(myString)
        if(re.search("(?P<url>https?://[^\s]+)", myString) is not None):
            web_links.append(re.search("(?P<url>https?://[^\s]+)", myString).group("url"))
            #print(myString)
            social_count+=1

    #print("Total Challenges Participations: ",hack_count+social_count)
    print("hack_count: ",hack_count)
    print("social_count: ",social_count)
    hack_count = hack_count*0.33
    social_count = social_count*0.25
    if(hack_count>1.0):
        hack_count = 1.0
    if(social_count>0.5):
        social_count = 0.5
    ae_points = hack_count+social_count
    print("\t\tAllotted Points for ExtraCurr: \t\t\t\t{} out of {}".format(ae_points,1.5))
    return ae_points
#ae_points = ae_main()
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Accolades & Extracurricular Activities <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Experience Details >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def experience_main(dict1,copy_data,final_data_jd):
    if "experience" in list(dict1):
        index,start,next_index = util_fun.find_next_index("experience",dict1)
        if(next_index):
            project_tokens = copy_data[start+1:next_index]
        else:
            project_tokens = copy_data[start+1:]
        final_data_res = util_fun.keyword_extract(project_tokens)
        keywords_count = matching_words(final_data_res,final_data_jd)
        print("keywords_count: ",keywords_count)

        #print("project_tokens: ",project_tokens)
        #dict1 = util_fun.get_flat_list()
        positions = init_list['pos']
        pos_count = 0
        for i in project_tokens:
            h = util_fun.remove_suffix_symbols(i)
            if(h != None and len(h)>1 and len(i.split())<=4):
                for j in positions:
                    if(j.lower() in i.lower()):
                        pos_count+=1
                        break
        print("pos_count: ",pos_count)
        kc = keywords_count*0.25
        if(kc>0.75):
            kc = 0.75
        pc = pos_count*0.75
        if(pc>2.25):
            pc = 2.25
        total_points = pc+kc
        print(">> pc,kc: ",[pc,kc])
    else:
        total_points = 0.0
    print("\t\tAllotted Points for Experience: \t\t\t{} out of {}".format(total_points,3.0))
    return total_points

def experience_main_bk(dict1,copy_data,final_data_jd):
    #print(">>>>>>>>>>>>>>>> Experience >>>>>>>>>>>>>>>>>>>>>>")
    if "experience" in list(dict1):
        index,start,next_index = util_fun.find_next_index("experience",dict1)
        if(next_index):
            project_tokens = copy_data[start+1:next_index]
        else:
            project_tokens = copy_data[start+1:]
        #Main functions
        #print(project_tokens)
        final_data_res = util_fun.keyword_extract(project_tokens)
        #print(final_data_res)
        exp_count = util_fun.find_proj_list(project_tokens)
        #print("Experience Count: ",exp_count)
        keywords_count = matching_words(final_data_res,final_data_jd)
        #print("Matching Count: ",keywords_count)

        #print("Experiences Count: ",exp_count)
        #print("Matching Keywords: ",keywords_count)
        total_points = exp_count*0.66
        if(total_points>2.0):
            exp_points = 2.0
        else:
            exp_points = total_points
        
        total_points = keywords_count*0.33
        if(total_points>1.0):
            exp_points+=1.0
        else:
            exp_points+=total_points
    else:
        exp_points = 0
    print("\t\tAllotted Points for Experience: \t\t\t{} out of {}".format(exp_points,3.0))
    return exp_points
#exp_points = experience_main()
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Experience Details <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Project Details >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#def projects_main(dict1,copy_data,final_data):
def projects_main(dict1,copy_data,final_data_jd):
    #print("Project Details\n======================")
    invalidChars = set(string_func.punctuation)
    if "projects" in list(dict1):
        index,start,next_index = util_fun.find_next_index("projects",dict1)
        if(next_index):
            project_tokens = copy_data[start+1:next_index]
        else:
            project_tokens = copy_data[start+1:]
        #print("project_tokens: ",project_tokens)
        final_data_res = util_fun.keyword_extract(project_tokens)
        projects_count = util_fun.find_proj_list(project_tokens)
        keywords_count = matching_words(final_data_res,final_data_jd)

        print("Projects Count: ",projects_count)
        print("Matching Keywords: ",keywords_count)

        total_points = projects_count*0.33
        if(total_points>1.0):
            proj_points = 1.0
        else:
            proj_points = total_points
        total_points = keywords_count*0.33
        if(total_points>1.0):
            proj_points+=1.0
        else:
            proj_points+=total_points
    else:
        proj_points = 0
    print("\t\tAllotted Points for Projects: \t\t\t\t{} out of {}".format(proj_points,2.0))
    return proj_points
#proj_points = projects_main()
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Project Details <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Skills Details >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def skills_main(main_text_data,dict1,copy_data,final_data_jd,n_skills):
    try:
        index,start,next_index = find_next_index("skills",dict1)
        print("\n")
        l_sk = copy_data[start+1:next_index]
        #print(l_sk)
    except:
        l_sk = main_text_data.split()
        #print(l_sk)
    #print("Candidate Skills\n================")
    all_skills = util_fun.skills_extraction(l_sk)
    #print(all_skills)
    #for i in all_skills:
    #    print(i)

    ## Matching Skills
    #print("Matched skills:\n=====================")
    ms_count = 0
    for i in all_skills:
        if(i in n_skills):
            ms_count+=1
    print("Matched Skill Count: ",ms_count)
    print("all Skill Count: ",len(all_skills))
    total_match_points = ms_count*0.375
    total_skill_points = len(all_skills)*0.1
    if(total_match_points>1.5):
        total_match_points = 1.5
    if(total_skill_points>1.0):
        total_skill_points = 1.0
    overall_skill_points = total_match_points + total_skill_points

    print("\t\tAllotted points for Skills: \t\t\t\t{} out of {}".format(overall_skill_points,2.5))
    return overall_skill_points
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Skills Details <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#####################################################################################################################################
## Main Function Starts Here

## Job Description
def main_bk(temp_name,jd_name,res_folder_name):
    ############################# JD Text Extraction ################################
    jd_name = jd_name.replace(" ","_")
    print(jd_name)
    jd_dir = jd_name.replace("/"+jd_name.split('/')[-1],"/")    
    final_data_jd,n_skills,n_deg = util_fun.get_jd_data(temp_name,jd_dir,jd_name)
    
    ############################# Resumes Text Extraction ###########################
    files = glob.glob(res_folder_name+"/*")
    for file in files:
        if(file.split('.')[-1] == 'pdf'):
            in_file = file
            out_file =  file.replace("."+file.split(".")[-1],".txt")
            os.system("sudo pdftotext {} {}".format(in_file,out_file))
    #RAW files to PDF
    print("res_folder_name: ",res_folder_name)
    files = glob.glob(res_folder_name+"/*.doc*")
    print("converting list files: ",files)
    for file in files:
        #util_fun.doc_2_pdf(file)
        nn = res_folder_name
        util_fun.doc_to_pdf(file,nn)
    
    files = glob.glob(res_folder_name+"/*.pdf")
    print(">>>>>>>>")
    print(files)
    print("<<<<<<<<<")
    #assert(False)
    df = pd.DataFrame(columns=['File Name','Email','Phone','Earned Points','Total Points','p_aca','p_ae','p_exp','p_proj','p_skill'])
    row = 0

    for file in files:
        file_name = file.split("/")[-1]
        #print("Resume Title: ",file_name)
        #file_name = "RajashekharG_resume_advanced.pdf"
        #print(file_name)
        #inpath = r"resumes_pdf/{}".format(file_name)
        #outpath = r"resumes_images/"
        out_dir = os.getcwd()+"/media/"+temp_name+"/temp_images"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        #print(file,out_dir)

        util_fun.pdf_to_jpg(file,out_dir)
        '''
        #combine all JPGs
        util_fun.combine_all_images(out_dir+"/{}_dir".format(file_name))
        #Extract Text from image
        #print("************"+out_dir+"/{}_dir/out.png".format(file_name)+)
        main_text_data = util_fun.jpg_to_text(out_dir+"/{}_dir/out.png".format(file_name))
        #print(main_text_data)
        '''
        # main_text_data = util_fun.docx_to_text(file)        
        main_text_data = util_fun.get_text_from_images(os.getcwd()+"/media/"+temp_name+"/temp_images/"+file_name+"_dir")
        #print(main_text_data)
        rl,copy_data = util_fun.data_process(main_text_data)
        #print(rl)
        print("Headline Extraction: ")
        _,dict1 = util_fun.key_processing_bk(rl)
        dict1 = collections.OrderedDict(sorted(dict1.items(), key=operator.itemgetter(1)))
        
        tot_points = 0.8+0.5+3.0+2.0+2.5
        email,phone = get_personal_info(main_text_data)
        if(len(dict1) == 0):
            print("Resume is not in Standard Format")
            
            det_for_df = [file_name,email,phone,0,tot_points,0,0,0,0,0]
            df.loc[row] = det_for_df
            #print(det_for_df)
        else:    
            ## Total Allotted Points
            print("\nPoints Allotment: ")
            aca_points = academics_main(dict1,copy_data,final_data_jd,n_deg)
            ae_points = ae_main(dict1,copy_data,final_data_jd)
            exp_points = experience_main(dict1,copy_data,final_data_jd)
            proj_points = projects_main(dict1,copy_data,final_data_jd)
            skill_points = skills_main(main_text_data,dict1,copy_data,final_data_jd,n_skills)

            got_points = aca_points+ae_points+exp_points+proj_points+skill_points
            got_points = round(got_points,2)
            print("\n# *Got {} Points out of {} Points*...".format(got_points,tot_points))

            det_for_df = [file_name,email,phone,got_points,tot_points,aca_points,ae_points,exp_points,proj_points,skill_points]
            df.loc[row] = det_for_df
            #row+=1
            #print(det_for_df)

        ### Saving Dataframe
        file_path = os.getcwd()+"/media/"+temp_name+"/User_Info.csv"
        if(os.path.exists(file_path)):
            main_df = pd.read_csv(file_path)
            main_df = main_df.append(df)
            main_df = main_df[['File Name','Email','Phone','Earned Points','Total Points','p_aca','p_ae','p_exp','p_proj','p_skill']]
            #print("main_df: ",main_df)
            main_df.reset_index(drop=True,inplace=True)
            main_df.to_csv(file_path)
        else:
            #os.makedirs("output/")
            df.to_csv(file_path)
        print("======================================\n")
        #break
    df1 = pd.read_csv(file_path)
    df1 = df1[['File Name','Email','Phone','Earned Points','Total Points','p_aca','p_ae','p_exp','p_proj','p_skill']]
    df1 = df1.sort_values(by=['Earned Points'],ascending=False)
    df1 = df1.reset_index().drop(['index'],axis=1)
    final_path = os.getcwd()+"/media/"+temp_name+"/final_results.csv"
    df1.to_csv(final_path)
    return final_path
#print("somehint")
#main("PA JD.docx","resumes_doc")

## Job Description
def main(temp_name,jd_name,res_folder_name):
    t11 = time.time()
    ############################# JD Text Extraction ################################
    jd_name = jd_name.replace(" ","_")
    #print(jd_name)
    jd_dir = jd_name.replace("/"+jd_name.split('/')[-1],"/")    
    is_jd = True
    main_jd_data,final_data_jd,n_skills,n_deg = util_fun.get_jd_data(temp_name,jd_dir,jd_name,is_jd)
    ############################# Resumes Text Extraction ###########################
    files = glob.glob(res_folder_name+"/*")
    #print("resumes_list: ",files)
    #print("res_folder_name: ",res_folder_name)
    
    df = pd.DataFrame(columns=['File Name','Email','Phone','Earned Points','Total Points','p_aca','p_ae','p_exp','p_proj','p_skill'])
    row = 0    

    is_jd = False
    for file in files:
        file_name = file.split("/")[-1]
        main_text_data,final_data,n_skills,n_deg = util_fun.get_jd_data(temp_name,res_folder_name,file,is_jd)
        l11 = []
        l11.append(main_text_data)
        rl,copy_data = util_fun.data_process(main_text_data)
        #print(rl)
        print("Headline Extraction: ")
        _,dict1 = util_fun.key_processing_bk(rl)
        dict1 = collections.OrderedDict(sorted(dict1.items(), key=operator.itemgetter(1)))
        
        tot_points = 1.0+3.0+1.5+2.0+2.5
        email,phone = get_personal_info(main_text_data)
        if(len(dict1) == 0):
            print("Resume is not in Standard Format")
           
            det_for_df = [file_name,email,phone,0,tot_points,0,0,0,0,0]
            df.loc[row] = det_for_df
            #print(det_for_df)
        else:    
            ## Total Allotted Points
            print("\nPoints Allotment: ")
            aca_points = academics_main(dict1,copy_data,final_data_jd,n_deg)
            ae_points = ae_main(dict1,copy_data,final_data_jd)
            exp_points = experience_main(dict1,copy_data,final_data_jd)
            proj_points = projects_main(dict1,copy_data,final_data_jd)
            skill_points = skills_main(main_text_data,dict1,copy_data,final_data_jd,n_skills)

            print("Points: [{},{},{},{},{}]".format(aca_points,ae_points,exp_points,proj_points,skill_points))
            got_points = (((aca_points/1.0)*100)+((ae_points/1.5)*100)+((exp_points/3.0)*100)+((proj_points/2.0)*100)+((skill_points/2.5)*100))/5
            got_points = round(got_points,2)
            print("\n *Got {} Points out of {} Points*...".format(got_points,tot_points*10))

            det_for_df = [file_name,email,phone,got_points,tot_points,aca_points,ae_points,exp_points,proj_points,skill_points]
            df.loc[row] = det_for_df
            #row+=1
            #print(det_for_df)

        ### Saving Dataframe
        file_path = os.getcwd()+"/media/"+temp_name+"/User_Info.csv"
        if(os.path.exists(file_path)):
            main_df = pd.read_csv(file_path)
            main_df = main_df.append(df)
            main_df = main_df[['File Name','Email','Phone','Earned Points','Total Points','p_aca','p_ae','p_exp','p_proj','p_skill']]
            #print("main_df: ",main_df)
            main_df.reset_index(drop=True,inplace=True)
            main_df.to_csv(file_path)
        else:
            #os.makedirs("output/")
            df.to_csv(file_path)
        print("======================================\n")
    df1 = pd.read_csv(file_path)
    df1 = df1[['File Name','Email','Phone','Earned Points','Total Points','p_aca','p_ae','p_exp','p_proj','p_skill']]
    df1 = df1.sort_values(by=['Earned Points'],ascending=False)
    df1 = df1.reset_index().drop(['index'],axis=1)
    final_path = os.getcwd()+"/media/"+temp_name+"/final_results.csv"
    df1.to_csv(final_path)
    print("Total Elapsed time: ",time.time()-t11)
    return final_path