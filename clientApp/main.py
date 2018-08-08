# coding = utf-8

from app import Client

if __name__ == '__main__':
    project = input("项目名：")
    token = input("打包机token：")
    key = input("打包机key：")
    Client(project, token, key)
