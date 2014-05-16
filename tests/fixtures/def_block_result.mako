<%def name="hello()">
hello world</%def>
<%def name="account()">
Account for ${username}:<br/>
%for row in accountdata:
Value: ${row}<br/>
%endfor
</%def>
<%def name="account(accountname, type=u'中文')">
account name: ${accountname}, type: ${type}</%def>
<%def name="mydef()">
<%def name="subdef()">
a sub def</%def>
i'm the def, and the subcomponent is ${subdef()}</%def>
<html><body><%block>
this is a block.</%block>
</body></html><%block filter="h">
<html>this is some escaped html.</html></%block>
<span class="post_prose"><%block name="post_prose" args="post">
${post.content}</%block>
</span><%block name="post_prose">
${pageargs['post'].content}</%block>
<%block name="post_prose">
${pageargs['post'].content}</%block>