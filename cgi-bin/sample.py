import cgi
import cgitb
cgitb.enable()

print("Content-Type: text/html") 

form = cgi.FieldStorage()

v1 = form.getfirst("foo")
v2 = form.getfirst("bar")

print(v1,v2)

print("Content-Type: text/html")
print()
htmlText = '''
<!DOCTYPE html>
<html>
    <head><meta charset="shift-jis" /></head>
<body bgcolor="lightyellow">
    <h1>VALUE</h1>
    <p>value is&nbsp; %s, %s<br/></p>
    <hr/>
    <a href="../form1.html">return</a>　
</body>
</html>
'''%(v1,v2)
