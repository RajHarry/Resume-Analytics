from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.conf import settings
import os.path
import pandas as pd
import random
import os,re
from . import main
from datetime import datetime
#dirname = datetime.now().strftime('%Y.%m.%d.%H.%M.%S') #2010.08.09.12.08.45 
# The root path in this python project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
global_points = 10.0

def _handle_uploaded_file(dirname,file,flg):
    """Deal with file upload   
    """
    # Write the file to media folder
    try:
        os.mkdir(os.path.join(BASE_DIR,'media/', dirname))
    except:
        pass
    try:
        os.mkdir(os.path.join(BASE_DIR,'media/', dirname+"/resumes"))
    except:
        pass
    
    destination = ""
    ext_name = str(file.name).split(".")[-1]
    file_name = str(file.name).replace("."+ext_name,"")

    file_name = re.sub(r'[^\w]', ' ', file_name).replace(" ","_")
    full_file_name = file_name+"."+ext_name
    print("file_name:{}, \next_name:{},\nfull_file_name:{}".format(file_name,ext_name,full_file_name))
    if flg == 0:
        destination = open(os.path.join(BASE_DIR, 'media/'+dirname+'/{}'.format(full_file_name)), 'wb+')
    else:
        destination = open(os.path.join(BASE_DIR, 'media/'+dirname+'/resumes/{}'.format(full_file_name)), 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()


def get_index(request):
    return render(request, 'index.html', {})
def get_score_points(ind):
    file_path = os.getcwd()+"/media/"+dirname+"/final_results.csv"
    data = pd.read_csv(file_path)

    earned_score = data.iloc[int(ind)-1]["Earned Points"]
    #print(earned_score)
    total_score = data.iloc[int(ind)-1]["Total Points"]

    #percentage = (earned_score/float(total_score))*100
    d1 = {}
    d1['academic'] = ((data.iloc[int(ind)-1]["p_aca"])/float(1.0))*100   #random.randint(0,100)
    d1['extra_curr'] = ((data.iloc[int(ind)-1]["p_ae"])/float(1.5))*100   #random.randint(0,100)
    d1['experience'] = ((data.iloc[int(ind)-1]["p_exp"])/float(3.0))*100  #random.randint(0,100)
    d1['projects'] = ((data.iloc[int(ind)-1]["p_proj"])/float(2.0))*100   #random.randint(0,100)
    d1['skills'] = ((data.iloc[int(ind)-1]["p_skill"])/float(2.5))*100    #random.randint(0,100)

    print("Allotted Points: >>>",d1['academic'],d1['extra_curr'],d1['experience'],d1['projects'],d1['skills'])
    d1['percentage'] = (d1['academic'] + d1['extra_curr'] + d1['experience'] + d1['projects'] + d1['skills'])/5
    return d1

def get_score(request):
    global dirname
    ind = request.GET.get('id','')
    if ind == '':
        return HttpResponse("<h1>404 Not Found</h1>")
    
    dict1 = get_score_points(ind)
    return render(request, 'score.html', {'score':dict1['percentage'],'p_aca':dict1['academic'],'p_ae':dict1['extra_curr'],'p_exp':dict1['experience'],'p_proj':dict1['projects'],'p_skill':dict1['skills']})
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
    #print(")***************************(")
    return rl,proj_copy
def upload_files(request):
    global dirname
    files = request.FILES.getlist('files')
    jobDescription = request.FILES.get('jobDescription')
    dirname = datetime.now().strftime('%Y.%m.%d.%H.%M.%S') #2010.08.09.12.08.45 
    _handle_uploaded_file(dirname,jobDescription,0)
    # Iterate the multiple files
    for afile in files:
        _handle_uploaded_file(dirname,afile,1)
    res_files = os.getcwd()+"/media/"+dirname+"/resumes"
    jds = os.getcwd()+"/media/"+dirname+"/"+str(jobDescription.name)
    file_path = main.main(dirname,jds,res_files)
    data = pd.read_csv(file_path)
    file_name = data.iloc[:,1].values
    sqNo = [i for i in range(1,len(file_name)+1)]
    #print(file_name)
    p_ern = []
    #print(data)
    for i in range(len(data)):
        di1 = get_score_points(i+1)
        p_ern.append(round(di1['percentage'],2))

    #dict1 = [get_score_points(i) for i in len(data)]
    #p_ern = [round(float((i/global_points)*100),1) for i in data["Earned Points"].values]
    #print("p_ern: ",p_ern)
    email = data['Email'].values
    return render(request,'resume_scores.html',{'data':zip(sqNo,file_name,email,p_ern)})