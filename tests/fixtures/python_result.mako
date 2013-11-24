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
<%
# Test that `embedded markup` is not parsed
a = "`test test`"
%>
<%
text = 'new-style python blocks'
%>
<div><%
count = 10
for i in range(count):
    print i
%>
</div><div><%
count = 0
count += 1
%>
</div><div><%
under_the_line = True
%>
</div><%
count = 1
for i in range(count):
    print i
%>
<%
# Inline feature is primarily for placing comments as here
var = 1
%>
<%!
from datetime import datetime
%>
<%!
from json import dumps
%>
