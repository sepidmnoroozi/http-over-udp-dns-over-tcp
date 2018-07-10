s = """ f=0;seq=0;
HTTP/1.1 302 Moved Temporarily
Content-Type: text/html; charset=UTF-8
Location: http://www.aut.ac.ir/aut/fa/
Vary: Accept-Encoding
Server: AUT
Date: Sun, 08 Jul 2018 08:38:09 GMT
Content-Length: 0
""".encode()
print(s.decode())
s1 = "alireza hastam az behshahr".encode()
contolline = s.splitlines()[0]
contolline = contolline.decode()
contolbits = contolline.split(";")
f = contolbits[0].split("=")[1]
seq = contolbits[1].split("=")[1]
num = int(seq)
ack = "seq="+str(num+1)
print(ack)
# snew = []
# n = False
# h = "\r\n".encode()
# print(s.splitlines())
# for line in s.splitlines():
#     if n :
#         snew.append(line+h)
#     n = True
# data = bytearray().join(snew)
# print(data.decode())
