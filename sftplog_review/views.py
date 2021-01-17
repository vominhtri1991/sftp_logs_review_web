from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
import os 
from datetime import date, timedelta, datetime
session_lst=[]

class Session:
	def __init__(self, id, time, log_str):
		self.id=id
		self.time=time
		self.datestr=time.split(' ')[0]+" "+time.split(' ')[1]
		self.log_str=log_str
		self.user=""
	def __str__(self):
		return "Session ID: "+self.id+" - Time: "+self.time+" -User: "+self.user+" - Action: "+self.log_str

def create_sessions_objects():
	local_file=os.path.join(settings.MEDIA_ROOT, 'sftp.log')
	print(local_file)
	fs=open(local_file,'r')
	fs_check_user=fs.readlines()
	count=0
	oneline=fs_check_user[0]
	str_lst=oneline.split(' ')
	begin_log_time=str_lst[0]+" "+str_lst[1]+" "+str_lst[2]
	server_log=str_lst[3]
	global session_lst
	for aLine in fs_check_user:
		str_lst=aLine.split(' ')
		ses_time=str_lst[0]+" "+str_lst[1]+" "+str_lst[2]
		ses_id_str=str_lst[4]
		ses_id=ses_id_str[ses_id_str.find('[')+1:ses_id_str.find(']')]
		ses_log_str=str_lst[5]
		ses_log=aLine[aLine.find(']: ')+2:]
		a_session=Session(ses_id,ses_time,ses_log)
		for aline_user in fs_check_user:
			if (aline_user.find(ses_id_str)>0 and aline_user.find("session opened for local user")>0):
				#print(aline_user)
				user_str=aline_user[aline_user.find("user")+5:aline_user.find("from")-1]
				a_session.user=user_str
				break
		fs.close()
		session_lst.append(a_session)

	fs.close()

@login_required(login_url='/admin/login/')
def home(request):
	return render(request,'sftplog_review/index.html')

@login_required(login_url='/admin/login/')
def upload(request):
	if request.method == 'POST' and request.FILES['myfile']:
		myfile = request.FILES['myfile']
		local_file=os.path.join(settings.MEDIA_ROOT, 'sftp.log')
		if os.path.isfile(local_file):
			os.remove(local_file)
		fs = FileSystemStorage()
		filename = fs.save('sftp.log', myfile)
		uploaded_file_url = fs.url(filename)
		print(uploaded_file_url)
		create_sessions_objects()
		for a_session in session_lst:
			print(a_session)
		return HttpResponseRedirect('/search')
		
	else:
		return render(request,'sftplog_review/upload.html')
def create_datelist(begin,end):
	date_list=[]
	sdate = datetime.strptime(begin,'%Y-%m-%d')   # start date
	edate = datetime.strptime(end,'%Y-%m-%d')   # end date
	delta = edate - sdate       # as timedelta
	for i in range(delta.days + 1):
		day = sdate + timedelta(days=i)
		date_list.append(day.strftime('%b %d'))
	return date_list

@login_required(login_url='/admin/login/')
def search(request):
	global session_lst
	local_file=os.path.join(settings.MEDIA_ROOT, 'sftp.log')
	print(local_file)
	fs=open(local_file,'r')
	count=0
	oneline=fs.readline()
	str_lst=oneline.split(' ')
	begin_log_time=str_lst[0]+" "+str_lst[1]+" "+str_lst[2]
	server_log=str_lst[3]
	
	if request.method == 'POST':
		create_sessions_objects()
		user=request.POST.get("user", "")
		begin=request.POST.get("begin", "")
		end=request.POST.get("end", "")
		print(user+"/"+begin+"/"+end)
		date_list=create_datelist(begin,end)
		print(date_list)
		result_session=[]
		if(user=="All Users" or user==""):
			for a_session in session_lst:
				if(a_session.datestr in date_list):
					print(a_session)
					result_session.append(a_session)
		else:
			for a_session in session_lst:
				if((a_session.datestr in date_list) and a_session.user==user):
					print(a_session)
					result_session.append(a_session)
		
		return render(request,'sftplog_review/result.html',{'result':result_session})
	return render(request,'sftplog_review/searching.html',{'server':server_log,'begin_time':begin_log_time,'session_log':session_lst})


@login_required(login_url='/admin/login/')
def result(request):
	return render(request,'sftplog_review/result.html')

@login_required(login_url='/admin/login/')
def about(request):
	return render(request,'sftplog_review/abouts.html')
# Create your views here
