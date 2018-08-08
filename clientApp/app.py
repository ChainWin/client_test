# coding: utf-8

import os, pwd, sys
from urllib import parse
import subprocess
import json
import requests
import hmac
import hashlib
import base64


'''
Request_url = "http://install-managesystem.webapp.163.com/task/getTask/"
Return_url = "http://install-managesystem.webapp.163.com/task/result/"
'''
Request_url = "http://127.0.0.1:9090/task/getTask/"
Return_url = "http://127.0.0.1:9090/task/result/"

def build(task):
    read_only_token = None
    try:
        git_address = task['git_address']
        url = git_address
        branch = task['branch']
        time_out = task['time_out']
        File = task['file']
        if 'read_only_token' in task:
            read_only_token = task['read_only_token']
    except Exception as e:
        print(e)
        error = 'the task type not right'
        return {'error': error}
    else:
        user_dir = pwd.getpwuid( os.getuid() )[ 5 ]
        all_task_dir = os.path.join(user_dir, 'BuildTask')
        if os.path.exists(all_task_dir):
            pass
        else:
            os.mkdir(all_task_dir)
        url_list = url.split('/')
        pro_name = url_list[-1].split('.')[0]
        task_dir = os.path.join(all_task_dir, task['task_id'])
        if os.path.exists(task_dir):
            error = 'the build result has been done'
            return {'error': error}
        else: 
            os.mkdir(task_dir)
        pro_dir = os.path.join(task_dir, pro_name)
        log_dir = os.path.join(pro_dir,'log.txt')
        if read_only_token is not None:
            url = ('https://'+url_list[3]+':'+read_only_token+'@'
                +url_list[2]+'/'+ url_list[3]+'/'+url_list[4])
        print("cloning begin...")
        try:
            project_clone = subprocess.Popen(['git', 'clone', '-b', branch, url], cwd=task_dir)
            project_clone.wait()
        except Exception as e:
            print(e)
            error = "clone project error"
            return {'error': error}
        print("cloning finish")
        
        print('building begin...')
        try:
            fhandle = open(log_dir, 'w')
            project_build = subprocess.call(['scons'], cwd=pro_dir, stdout=fhandle)
        except Exception as e:
            print(e)
            print('build project error')
        print("building finish")
 
        result_status = project_build
        f = open(log_dir)
        log_contents = f.read()
        f.close()
        result = {'result_status': result_status, 'log_contents': log_contents}
        if result_status==0:
            upload_dir = os.path.join(pro_dir, 'upload.py')
            if os.path.exists(upload_dir):
                sys.path.append(pro_dir)
                import upload
                result_url = upload.uploadfile(pro_dir)
                result['result_url'] = result_url
            result['description'] = 'succeed'
        else:
            result['description'] = 'failed'
        return result

def Client(project, token, key):
  var = 1
  while var==1: 
    value = {'project': project, 'token': token}
    strToSign = parse.urlencode(value)
    digest = hmac.new(bytes(key, encoding='utf-8'),
                      bytes(strToSign, encoding='utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()
    user_info = {'project': project, 'token': token, 'signature': signature}    
    headers = {'content-type': 'application/json'}
    # request task
    r = requests.post(Request_url, data=json.dumps(user_info), headers=headers)    
    try:
        task = r.json()
    except Exception as e:
        print('Response error')
        return
    if 'error' in task:
        print('task error: ' + task['error'])
        return
    else:
        print('task: '+task['task_id']+' building begins...')
        # building task
        result = build(task)
        result['token'] = token
        result['project'] = project
        result['task_id'] = task['task_id']
        # return building result
        value = {'project': project, 'token': token, 'task_id': result['task_id']}
        if 'error' in result:
            print(result['error'])
            print('building error')
            value['error'] = result['error']
        else:
            value['result_status'] = result['result_status']
            value['description'] = result['description']
            if 'log_contents' in result:
                value['log_contents'] = result['log_contents']
            if 'result_url' in result:
                value['result_url'] = result['result_url']
        strToSign = parse.urlencode(value)
        digest = hmac.new(bytes(key, encoding='utf-8'),
                      bytes(strToSign, encoding='utf-8'), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode()
        result['signature'] = signature
        r = requests.post(Return_url, data=json.dumps(result), headers=headers)    
        feedback = r.json()
        if 'error' in feedback:
            print('server upload failed: ' + feedback['error'])
        else:
            print('succeed: ' + feedback['succeed'])
        
