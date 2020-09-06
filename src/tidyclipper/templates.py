"""
Jinja2 template generation.

Included as strings because I'm too lazy to have multiple files.
"""

import jinja2


def _make_template(raw: str) -> jinja2.Template:
    return jinja2.Environment(loader=jinja2.BaseLoader()).from_string(raw)


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
</span>
"""
)

CLIPPING = _make_template(
    r"""
<!DOCTYPE html>
<html>
<head>
<title>{{title}}</title>
  <style type="text/css">
  body {
    max-width: 1000px;
    margin: auto;
    padding: 1em;
    line-height: 20px;
    background-color: hsl(25, 75%, 85%);
    color: #000000;
    font-family: sans-serif;
    font-size: 13px;
  }
  hr {
    color: #000000;
    height:0px;
    border-top:2px dashed;
    border-bottom: none;
    max-width: 90%;
  }
  h1 {
    text-align: center;
    font-size: 2.2em;

    border: 5px solid #000000;
    padding-top: 20px;
    padding-right: 20px;
    padding-left: 20px;
    padding-bottom: 20px;
    border-radius: 25px;
    background-color: hsl(25, 70%, 50%);
  }
  h2 {
    font-size: 1.5em;
    text-align: center;
    text-decoration: underline;
    padding-top: 5px;
    padding-bottom: 5px;
  }
  </style>
</head>
<body>
<h1>{{title}}</h1>
<p>Pattern = {{pattern}}</p>
<hr>
{% for entry in entries %}
{{ entry.as_html() }}
<hr>
{% endfor %}
</body></html>
"""
)
