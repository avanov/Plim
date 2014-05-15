%if True:
<div>1 Test</div>
%endif
<div>2 Test</div>------------------------------------

%if False:
<div>3 False Test</div>
%if True:
<div>4 Test</div>
%endif
<div>5 Test</div>
%elif True:
<div>6 True Test</div>
%elif 1 == 1:
<div>7 Test</div>
%else:
<div>8 Else Test</div>
%endif

%if False:

%elif True:

%else:

%endif
%if (a == b) or (c == d):
Test
%elif (e == f):
Test2
%endif
%if "permission:admin" in effective_principals(request):
<p>Allow</p>
%endif