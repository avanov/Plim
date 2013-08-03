<%
x = 1
y = x + 1
if True:
    y += 1
else:
    y -= 1
%>
<%
z = y + 1
%>
<%
a = z + y + x
%>
<%!
from abcde import fghi
from module import func
%>
<%
a = u'Привет Мир!'
%>
<%

for i in i_list:
    for j in j_list:
        print i, j
    if i == j:
        print "Equal"
if True:
    print "True"
%>
