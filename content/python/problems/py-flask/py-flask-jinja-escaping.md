---
id: py-flask-jinja-escaping
title: Jinja Templates, Inheritance and Autoescaping
difficulty: Medium
order: 4
tags: Flask, Jinja2, template inheritance, blocks, filters, autoescape, XSS, safe, DictLoader
time_limit: 5
---
## Statement
Render a small shop with **Jinja2 templates** that you keep in a dict (no template folder needed):

```python
TEMPLATES: dict[str, str] = {...}     # at least "base.html", "list.html", "detail.html"
def create_app(products: list[dict], banner_html: str) -> Flask: ...
```

In `create_app`, set `app.jinja_loader = jinja2.DictLoader(TEMPLATES)`. Use `render_template`, and register a template filter named `money` that turns integer cents into dollars with thousands separators: `123456` → `$1,234.56`, `5` → `$0.05`.

A product is `{"id": int, "name": str, "price_cents": int, "comments": [str, ...]}`. `banner_html` is **trusted** HTML written by the shop owner. Names, comments and the search text are **untrusted** and must be escaped. Keep Flask's autoescaping on, and mark only the banner as safe.

`list.html` and `detail.html` must **extend** `base.html`, which renders exactly these lines (the `…` parts come from blocks):

```text
<!doctype html>
<title>{TITLE} | Shop</title>
<header>{banner_html, unescaped}</header>
<main>
…content block…
</main>
<footer>{FOOTER}</footer>
```

**`GET /products?q=`** — title `Products`. Products are filtered by case-insensitive substring of the name when `q` is non-empty, keeping their order. Content:
```text
<h1>Products</h1>
<p>Results for: {q}</p>                       (only when q is non-empty)
<ul>
<li class="product">{n}. {name} - {price|money}</li>      (n = 1, 2, … in the filtered list)
</ul>
```
If nothing matches, the `<ul>…</ul>` is replaced by `<p class="empty">No products</p>`. The footer is `1 product` or `{k} products` (k = number shown, `0 products` included).

**`GET /products/<int:id>`** — title is the product name. Unknown id → 404. Content:
```text
<h1>{name}</h1>
<p class="price">{price|money}</p>
<h2>Comments ({count})</h2>
<ul>
<li>{comment}</li>
</ul>
```
With no comments, the `<ul>…</ul>` is replaced by `<p>No comments yet</p>`. The footer is base's default: `Shop`.

The driver strips each line and drops empty lines before printing, so indentation and blank lines don't matter, but each element must be on its own line as shown.

## Starter
```python
import jinja2
from flask import Flask, abort, render_template, request

TEMPLATES = {
    "base.html": "<!doctype html>\n<title>Shop</title>\n{% block content %}{% endblock %}",
    "list.html": "{% extends 'base.html' %}{% block content %}{% for p in products %}{{ p.name }}{% endfor %}{% endblock %}",
    "detail.html": "{% extends 'base.html' %}",
}


def create_app(products, banner_html):
    app = Flask(__name__)
    app.jinja_loader = jinja2.DictLoader(TEMPLATES)

    @app.get("/products")
    def product_list():
        return render_template("list.html", products=products)

    return app
```

## Driver
```python
import sys

CATALOG = [
    {"id": 1, "name": "Pen", "price_cents": 150, "comments": ["Writes well", "<img src=x onerror=alert(1)>"]},
    {"id": 2, "name": "Tom & Jerry DVD", "price_cents": 1999, "comments": []},
    {"id": 3, "name": "<script>alert('pwn')</script>", "price_cents": 5, "comments": ["\"quoted\" & 'single'"]},
    {"id": 4, "name": "Standing Desk", "price_cents": 123456, "comments": ["Sturdy"]},
    {"id": 5, "name": "pencil", "price_cents": 100000000, "comments": ["ok"]},
]

def show(c, path):
    r = c.get(path)
    print(f"GET {path} -> {r.status_code}")
    if r.status_code == 200:
        for line in r.get_data(as_text=True).splitlines():
            if line.strip():
                print("  " + line.strip())

for g in sys.stdin.read().split():
    print("#", g)
    if g == "list":
        c = create_app(CATALOG[:2], "<strong>Sale!</strong>").test_client()
        show(c, "/products")
        show(c, "/products?q=")
    elif g == "search":
        c = create_app(CATALOG, "<em>New</em> & improved").test_client()
        show(c, "/products?q=PEN")
        show(c, "/products?q=desk")
        show(c, "/products?q=%3Cb%3Enone%3C/b%3E")
        show(c, "/products?q=script")
    elif g == "detail":
        c = create_app(CATALOG, "<b>B</b>").test_client()
        for i in (1, 2, 3, 4, 9):
            show(c, f"/products/{i}")
    elif g == "money":
        app = create_app([], "")
        f = app.jinja_env.filters["money"]
        print([f(x) for x in (0, 5, 99, 100, 1234, 123456, 100000000, 987654321)])
        print("extends", all("{% extends" in TEMPLATES[t] for t in ("list.html", "detail.html")))
        show(app.test_client(), "/products?q=x")
```

## Tests
=== sample
list
---
# list
GET /products -> 200
  <!doctype html>
  <title>Products | Shop</title>
  <header><strong>Sale!</strong></header>
  <main>
  <h1>Products</h1>
  <ul>
  <li class="product">1. Pen - $1.50</li>
  <li class="product">2. Tom &amp; Jerry DVD - $19.99</li>
  </ul>
  </main>
  <footer>2 products</footer>
GET /products?q= -> 200
  <!doctype html>
  <title>Products | Shop</title>
  <header><strong>Sale!</strong></header>
  <main>
  <h1>Products</h1>
  <ul>
  <li class="product">1. Pen - $1.50</li>
  <li class="product">2. Tom &amp; Jerry DVD - $19.99</li>
  </ul>
  </main>
  <footer>2 products</footer>
=== hidden
search
---
# search
GET /products?q=PEN -> 200
  <!doctype html>
  <title>Products | Shop</title>
  <header><em>New</em> & improved</header>
  <main>
  <h1>Products</h1>
  <p>Results for: PEN</p>
  <ul>
  <li class="product">1. Pen - $1.50</li>
  <li class="product">2. pencil - $1,000,000.00</li>
  </ul>
  </main>
  <footer>2 products</footer>
GET /products?q=desk -> 200
  <!doctype html>
  <title>Products | Shop</title>
  <header><em>New</em> & improved</header>
  <main>
  <h1>Products</h1>
  <p>Results for: desk</p>
  <ul>
  <li class="product">1. Standing Desk - $1,234.56</li>
  </ul>
  </main>
  <footer>1 product</footer>
GET /products?q=%3Cb%3Enone%3C/b%3E -> 200
  <!doctype html>
  <title>Products | Shop</title>
  <header><em>New</em> & improved</header>
  <main>
  <h1>Products</h1>
  <p>Results for: &lt;b&gt;none&lt;/b&gt;</p>
  <p class="empty">No products</p>
  </main>
  <footer>0 products</footer>
GET /products?q=script -> 200
  <!doctype html>
  <title>Products | Shop</title>
  <header><em>New</em> & improved</header>
  <main>
  <h1>Products</h1>
  <p>Results for: script</p>
  <ul>
  <li class="product">1. &lt;script&gt;alert(&#39;pwn&#39;)&lt;/script&gt; - $0.05</li>
  </ul>
  </main>
  <footer>1 product</footer>
=== hidden
detail
---
# detail
GET /products/1 -> 200
  <!doctype html>
  <title>Pen | Shop</title>
  <header><b>B</b></header>
  <main>
  <h1>Pen</h1>
  <p class="price">$1.50</p>
  <h2>Comments (2)</h2>
  <ul>
  <li>Writes well</li>
  <li>&lt;img src=x onerror=alert(1)&gt;</li>
  </ul>
  </main>
  <footer>Shop</footer>
GET /products/2 -> 200
  <!doctype html>
  <title>Tom &amp; Jerry DVD | Shop</title>
  <header><b>B</b></header>
  <main>
  <h1>Tom &amp; Jerry DVD</h1>
  <p class="price">$19.99</p>
  <h2>Comments (0)</h2>
  <p>No comments yet</p>
  </main>
  <footer>Shop</footer>
GET /products/3 -> 200
  <!doctype html>
  <title>&lt;script&gt;alert(&#39;pwn&#39;)&lt;/script&gt; | Shop</title>
  <header><b>B</b></header>
  <main>
  <h1>&lt;script&gt;alert(&#39;pwn&#39;)&lt;/script&gt;</h1>
  <p class="price">$0.05</p>
  <h2>Comments (1)</h2>
  <ul>
  <li>&#34;quoted&#34; &amp; &#39;single&#39;</li>
  </ul>
  </main>
  <footer>Shop</footer>
GET /products/4 -> 200
  <!doctype html>
  <title>Standing Desk | Shop</title>
  <header><b>B</b></header>
  <main>
  <h1>Standing Desk</h1>
  <p class="price">$1,234.56</p>
  <h2>Comments (1)</h2>
  <ul>
  <li>Sturdy</li>
  </ul>
  </main>
  <footer>Shop</footer>
GET /products/9 -> 404
=== hidden
money
---
# money
['$0.00', '$0.05', '$0.99', '$1.00', '$12.34', '$1,234.56', '$1,000,000.00', '$9,876,543.21']
extends True
GET /products?q=x -> 200
  <!doctype html>
  <title>Products | Shop</title>
  <header></header>
  <main>
  <h1>Products</h1>
  <p>Results for: x</p>
  <p class="empty">No products</p>
  </main>
  <footer>0 products</footer>

## Hints
- In `base.html`, write `{% block title %}{% endblock %}`, `{% block content %}{% endblock %}` and `{% block footer %}Shop{% endblock %}`. Children use `{% extends "base.html" %}`.
- Never put `|safe` on names, comments or `q`. Put it only on the banner (inject it with a context processor or pass it to every `render_template`).
- `money`: integer-divide by 100 and format with `:,`, then append `% 100` padded with `:02d`. For "product"/"products", use `products|length` in the footer block.

## Solution
**Inheritance.** `base.html` owns the page skeleton and declares `{% block %}` holes. Child templates `{% extends %}` it and fill only the blocks they care about. A block a child doesn't override (the detail page's footer) keeps the base's default content.

**Autoescaping is the XSS defence.** Flask enables autoescaping for `.html` templates, so `{{ p.name }}` renders `<script>` as `&lt;script&gt;`, and `&`, `"` and `'` become entities too. Untrusted text can never become markup. `|safe` switches that off, so use it only for content you trust (the owner's banner). Using `|safe` on a comment would let any visitor run JavaScript in every other visitor's browser (stored XSS).

**Filters and context processors.** A template filter (`@app.template_filter("money")`) keeps formatting logic out of views and templates: `f"${cents // 100:,}.{cents % 100:02d}"` adds thousands separators and two-digit cents with integer arithmetic (no float rounding). A context processor injects variables (the banner) into every template.

**Loop helpers.** `loop.index` is 1-based, and `|length` counts items. `{% if products %}…{% else %}…{% endif %}` handles the empty state.

Complexity: O(total size of the rendered page).

```python
import jinja2
from flask import Flask, abort, render_template, request

TEMPLATES = {
    "base.html": """<!doctype html>
<title>{% block title %}{% endblock %} | Shop</title>
<header>{{ banner|safe }}</header>
<main>
{% block content %}{% endblock %}
</main>
<footer>{% block footer %}Shop{% endblock %}</footer>
""",
    "list.html": """{% extends "base.html" %}
{% block title %}Products{% endblock %}
{% block content %}
<h1>Products</h1>
{% if q %}
<p>Results for: {{ q }}</p>
{% endif %}
{% if products %}
<ul>
{% for p in products %}
<li class="product">{{ loop.index }}. {{ p.name }} - {{ p.price_cents|money }}</li>
{% endfor %}
</ul>
{% else %}
<p class="empty">No products</p>
{% endif %}
{% endblock %}
{% block footer %}{{ products|length }} product{{ "" if products|length == 1 else "s" }}{% endblock %}
""",
    "detail.html": """{% extends "base.html" %}
{% block title %}{{ p.name }}{% endblock %}
{% block content %}
<h1>{{ p.name }}</h1>
<p class="price">{{ p.price_cents|money }}</p>
<h2>Comments ({{ p.comments|length }})</h2>
{% if p.comments %}
<ul>
{% for c in p.comments %}
<li>{{ c }}</li>
{% endfor %}
</ul>
{% else %}
<p>No comments yet</p>
{% endif %}
{% endblock %}
""",
}


def create_app(products, banner_html):
    app = Flask(__name__)
    app.jinja_loader = jinja2.DictLoader(TEMPLATES)

    @app.template_filter("money")
    def money(cents):
        return f"${cents // 100:,}.{cents % 100:02d}"

    @app.context_processor
    def inject_banner():
        return {"banner": banner_html}

    @app.get("/products")
    def product_list():
        q = request.args.get("q", "")
        shown = [p for p in products if q.lower() in p["name"].lower()] if q else list(products)
        return render_template("list.html", products=shown, q=q)

    @app.get("/products/<int:pid>")
    def product_detail(pid):
        p = next((p for p in products if p["id"] == pid), None)
        if p is None:
            abort(404)
        return render_template("detail.html", p=p)

    return app
```
