# coding: utf-8

import time
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
        error = 'error: the task type not right'
        return {'description': error, 'result_status': 1}
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
            error = 'error: the build result has been done'
            return {'description': error, 'result_status': 1}
        else: 
            os.mkdir(task_dir)
        pro_dir = os.path.join(task_dir, pro_name)
        log_dir = os.path.join(pro_dir,'log.txt')
        if read_only_token is not None:
            url = ('https://'+url_list[3]+':'+read_only_token+'@'
                +url_list[2]+'/'+ url_list[3]+'/'+url_list[4])
        print("cloning begin...")
        try:
            project_clone = subprocess.check_call(['git', 'clone', '-b', branch, url], cwd=task_dir)
        except Exception as e:
            print(e)
            return {'description': str(e), 'result_status': 128}
        print("cloning finish")
        
        print('building begin...')
        try:
            fhandle = open(log_dir, 'w')
            project_build = subprocess.check_call(['scons'], cwd=pro_dir, stdout=fhandle)
        except Exception as e:
            print(e)
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
            result['description'] = 'project building succeed'
        else:
            result['description'] = 'project building failed'
        return result

def Client(project, token, key):
    var = 1
    value = {'project': project, 'token': token}
    strToSign = parse.urlencode(value)
    digest = hmac.new(bytes(key, encoding='utf-8'),
                      bytes(strToSign, encoding='utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()
    user_info = {'project': project, 'token': token, 'signature': signature}    
    headers = {'content-type': 'application/json'}
    while var==1: 
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
        elif 'empty' in task:
            time.sleep(30)
            continue 
        else:
            print('task: '+task['task_id']+' building begins...')
            # building task
            result = build(task)
            print(result['description'])
            result['token'] = token
            result['project'] = project
            result['task_id'] = task['task_id']
            # return building result
            value = {'project': project, 'token': token, 'task_id': result['task_id'],
              'description': result['description'], 'result_status': result['result_status']}
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
        
