# coding = utf-8

from app import Client

if __name__ == '__main__':
    f = open('./requirements.txt')
    lines = f.readlines()
    project = lines[0].strip('project:').strip('\n').strip()
    token = lines[1].strip('token:').strip('\n').strip()
    key = lines[2].strip('key:').strip('\n').strip()
    Client(project, token, key)
