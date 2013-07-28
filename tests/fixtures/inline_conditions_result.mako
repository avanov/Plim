%if i > 7:
<li><a href="${route_to(i)}">${i}</a></li>
%endif
%if i > 7:
%if i < 10:
<a href="${route_to(i)}">${i}</a>
%else:
No link
%endif
%endif
<h2 class="caption">
%if is_editor:
<a href="#">Edit</a>
%elif (is_admin):
<a href="#">Delete</a>
%elif is_guest:
No Caption
%else:
Caption
%endif
</h2><h3>
%if idea:
Idea
%elif is_day:
Think about it
%else:
Sleep
%endif
</h3>Cool!
