"""
Jinja2 template generation.

Included as strings because I'm too lazy to have multiple files.
"""

import jinja2


def _make_template(raw: str) -> jinja2.Template:
    return jinja2.Environment(loader=jinja2.BaseLoader).from_string(raw)


ENTRY = _make_template(
    r"""
<span class = "entry">
<h2>{{entry.title}}</h2>
<ul>
<li>Time: {{entry.time}}</li>
<li>Feed: {{entry.feed}}</li>
<li>Link: <a href="{{entry.link}}">Link</a></li>
</ul>
{{entry.summary}}
</hr>
</span>
"""
)

CLIPPING = _make_template(
    r"""
<!DOCTYPE html>
<html>
<head>
<title>{{title}}</title>
</head>
<body>
<h1>{{title}}</h1>
<p>Pattern = {{pattern}}</p>
{% for entry in entries %}
{{ entry.as_html() }}
{% endfor %}
</body></html>
"""
)
