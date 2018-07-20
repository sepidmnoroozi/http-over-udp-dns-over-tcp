# from urllib.parse import urlparse
# o = urlparse('http://up2www.com/uploads/7732tree-1-.jpg')
# print(o.hostname)
import hashlib

a = hashlib.md5("""GET / HTTP/1.1
Host: aut.ac.ir
Connection: close

""".encode()).hexdigest()
print(a)


b = hashlib.md5("hellli".encode()).hexdigest()
print(b)