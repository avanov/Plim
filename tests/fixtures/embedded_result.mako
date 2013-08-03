<a href="#">Embedded <strong>string</strong> everywhere</a>
---
<a href="#">Embedded <strong>string</strong><i>s</i> everywhere</a>
---
This is a <a href="#">link</a> embedded <br/> into a literal block.
---
another <a href="#">very <strong>funny <i>recursive</i></strong></a> test
---
Embed everything <div id="even">statements
%for word in ['like', 'this']:
${word}
%endfor
</div>.
---
Try using multi-line embedded markup <a href="#">Like this <strong data-something="true">test</strong></a>
