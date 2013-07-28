<a
%for __plim_key__, __plim_value__ in attrs.items():
${__plim_key__}="${__plim_value__}"
%endfor
>Test</a><a
%for __plim_key__, __plim_value__ in attrs.items():
${__plim_key__}="${__plim_value__}"
%endfor
>Test2 </a><a
%for __plim_key__, __plim_value__ in attrs(data=**{'a':'b'}).items():
${__plim_key__}="${__plim_value__}"
%endfor
>Test3</a><a
%for __plim_key__, __plim_value__ in attrs.items():
${__plim_key__}="${__plim_value__}"
%endfor

%for __plim_key__, __plim_value__ in attrs2.items():
${__plim_key__}="${__plim_value__}"
%endfor
 disabled="disabled">Test4</a>
