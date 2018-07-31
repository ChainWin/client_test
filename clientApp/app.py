# coding: utf-8

from urllib import parse
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
    result_status = 'succeed'
    description = 'test'
    url = 'https://www.baidu.com'
    result = {'result_status': result_status, 'description': description,
              'url': url, 'task_id': task['task_id']}
    return result


def Client(project, token, key):
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
    else:
        print('building begins...')
        # building task
        result = build(task)
        # return building result
        result['token'] = token
        result['project'] = project
        value = {'project': project, 'token': token, 'task_id': result['task_id'],
             'result_status': result['result_status'], 'description': result['description']}
        if 'log_url' in result:
            value['log_url'] = result['log_url']
        if 'url' in result:
            value['url'] = result['url']
        strToSign = parse.urlencode(value)
        digest = hmac.new(bytes(key, encoding='utf-8'),
                      bytes(strToSign, encoding='utf-8'), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode()
        result['signature'] = signature
        r = requests.post(Return_url, data=json.dumps(result), headers=headers)
        feedback = r.json()
        if 'error' in feedback:
            print('server error: ' + feedback['error'])
        else:
            print('succeed: ' + feedback['succeed'])






