%while i:
<div>${i}</div>
%endwhile
<div>2 Test</div>------------------------------------


%while i in var:
<div>${i}</div>
%if i:
<div>4 Test</div>
%endif
<div>5 Test</div>
%while i:
<div>${i}</div>
%if i:
<div>4 Test</div>
%endif
<div>5 Test</div>
%endwhile

%endwhile

%while i in []:

%endwhile
%while i in [1,2,3,4,5]:

%endwhile