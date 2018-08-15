#coding: utf-8


a = b"Cloning into 'test'...\nfatal: Remote branch \xe5\x88\x86\xe6\x94\xaf1 not found in upstream origin\nUnexpected end of command stream\n"
a.decode('utf-8')
b= b"Cloning into 'test'...\n"
print(a)
print(b)
