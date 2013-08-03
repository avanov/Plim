%for item in ['a','b','c',':'][::][1:]:
<li><strong>${Case1}</strong></li>
%endfor

%for item in ['a','b','c',':'][::][1:]:
<li><strong>${Case2}</strong></li>
%endfor

%for item in ['a','b','c',':'][::][1:]:
<li>
%for item2 in ['a','b','c',':'][::][1:]:
<strong>${Case3}</strong>
%endfor
</li>
%endfor
<ul>
%for item in {1, 2, 3}:
<li class="link"><a href="${route_to(item)}">${item}</a></li>
%endfor
</ul><ul>
%for link in ['About','Blog','Sitemap']:
<li><a href="${route_to(link)}">${link}</a></li>
%endfor
</ul><table>
%for item in items:
<tr><td>${item.name}</td><td>${item.price}</td></tr>
%endfor
</table>
