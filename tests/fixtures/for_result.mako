%for i in [1,2,3,4,5]:
<div>${i}</div>
%endfor
<div>2 Test</div>------------------------------------

%for i in var:
<div>${i}</div>
%if i:
<div>4 Test</div>
%endif
<div>5 Test</div>
%for i in var:
<div>${i}</div>
%if i:
<div>4 Test</div>
%endif
<div>5 Test</div>
%endfor

%endfor

%for i in []:

%endfor

%for i in  [1,2,3,4,5]:
${i}
%endfor

%for i in []:
${i}
%else:
%for i in []:
%if i is not None:
${i}
%else:
%if True:
Always
%else:
Never
%endif
%endif
%else:
Oh my else
%endfor
%endfor
