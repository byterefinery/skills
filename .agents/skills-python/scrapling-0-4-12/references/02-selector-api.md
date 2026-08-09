# Selector API Reference

## Creating Selectors

```python
from scrapling import Selector
from scrapling.fetchers import Fetcher

# From HTML string
page = Selector('<html><body><h1>Hello</h1></body></html>')

# From bytes
page = Selector(b'<html><body><p>Text</p></body></html>')

# From fetcher (returns Response, which inherits Selector)
page = Fetcher.get('https://example.com')

# Options
page = Selector(html_string, url='https://example.com', encoding='utf-8', huge_tree=True)
page = Selector(html_string, keep_comments=True, keep_cdata=True)
```

## CSS Selection

### Basic Selectors

```python
page.css('h1')                    # all h1 elements
page.css('.class')                # by class
page.css('#id')                   # by id
page.css('div > p')               # direct children
page.css('div p')                 # descendants
page.css('a[href]')               # elements with attribute
page.css('input[type="text"]')    # attribute value
page.css('div:first-child')       # pseudo-class
page.css('.a, .b, .c')            # multiple selectors
```

### Pseudo-elements (Scrapy/Parsel-style)

```python
# Text content
page.css('h1::text').get()        # first match as string
page.css('p::text').getall()      # all matches as list

# Attribute values
page.css('a::attr(href)').getall()
page.css('img::attr(src)').get()

# Inner HTML
page.css('div::html').get()

# Combined
page.css('.item .title::text').get()
page.css('.item .price::text').getall()
```

### Chaining

```python
# Chain selectors
page.css('.product').css('.name::text').getall()

# Index into results
page.css('.item')[0].css('.title::text').get()
page.css('.item')[1].css('.price::text').get()

# Navigation then selection
page.css('#main')[0].parent.css('.sidebar a::attr(href)').getall()
```

## XPath Selection

```python
# Basic XPath
page.xpath('//div[@class="quote"]')
page.xpath('//h1/text()')
page.xpath('//a/@href')

# Complex expressions
page.xpath('//div[contains(@class, "item")]/span/text()')
page.xpath('//ul/li[position()>2]/a/@href')

# Relative XPath (from current node)
item = page.css('.item')[0]
item.xpath('.//span[@class="price"]/text()')

# get() and getall()
page.xpath('//title/text()').get()     # first match
page.xpath('//a/@href').getall()       # all matches
```

## BeautifulSoup-style Selection

```python
# find_all — tag, attributes, text
page.find_all('div')
page.find_all('div', class_='quote')
page.find_all('div', {'class': 'quote', 'id': 'main'})
page.find_all(['div', 'p'], class_='text')
page.find_all(class_='item')           # tag-agnostic
page.find_all('a', href=True)          # attribute presence

# Reserved words use underscore suffix
page.find_all('td', class_='name')     # not 'class'
page.find_all('label', for_='email')   # not 'for'

# find — single element
page.find('h1')
page.find('div', class_='header')
```

## Text Search

```python
# Find elements by text content
page.find_by_text('quote', tag='div')
page.find_by_text('Buy Now', tag='button')
page.find_by_text(r'Price: \$\d+', regex=True, tag='span')
```

## Navigation

```python
# Parent
item.parent

# Siblings
item.next_sibling
item.previous_sibling

# Children
item.children          # direct children (list)
item.below_elements()  # all descendants

# Index access
items = page.css('.item')
items[0]               # first
items[-1]              # last
items[1:3]             # slice

# First/last helpers
page.css('.item').first
page.css('.item').last
```

## Data Extraction

### Text

```python
# Single element text
page.css('h1::text').get()

# All matching texts
page.css('.item::text').getall()

# Full page text
page.get_all_text(strip=True)
page.get_all_text(ignore_tags=('script', 'style'))

# Cleaned text (whitespace normalized)
page.get_all_text(strip=True, ignore_tags=('script', 'style', 'noscript', 'svg', 'iframe'))
```

### Attributes

```python
# Single attribute
page.css('a')[0].attrib['href']
page.css('a')[0].attrib.get('title', 'default')

# All attributes
page.css('input')[0].attrib

# Via pseudo-element
page.css('a::attr(href)').get()
page.css('img::attr(src)').getall()
```

### HTML Content

```python
# Raw HTML of element
page.css('div')[0].html_content

# Inner HTML via pseudo-element
page.css('div::html').get()
```

## Response Object

Fetcher methods return a `Response` object (Selector + HTTP metadata):

```python
page = Fetcher.get('https://example.com')

# HTTP metadata
page.status_code           # int, e.g. 200
page.reason                # str, e.g. "OK"
page.url                   # final URL (after redirects)
page.headers               # response headers (dict)
page.request_headers       # sent request headers (dict)
page.cookies               # response cookies
page.history               # list of redirect Response objects
page.body                  # raw bytes
page.encoding              # detected encoding
page.captured_xhr          # captured XHR responses (browser fetchers)
page.meta                  # metadata dict (e.g., proxy used)

# Selector methods (inherited)
page.css('h1::text').get()
page.xpath('//title/text()').get()
page.html_content          # full HTML as string
```

## Adaptive Scraping

Save element fingerprints and relocate after website changes:

```python
from scrapling.fetchers import Fetcher

# First run — save fingerprints
page = Fetcher.get('https://example.com')
items = page.css('.product', auto_save=True)

# Later, if the site structure changes
page = Fetcher.get('https://example.com')
items = page.css('.product', adaptive=True)  # relocate using saved fingerprints

# Enable globally
Fetcher.adaptive = True
```

Data is stored in `elements_storage.db` (SQLite) in the scrapling package directory. Customize with `storage_args`.

## Similar Elements

```python
# Find elements similar to a matched element
first_item = page.css('.product')[0]
similar = first_item.find_similar()

# Extract from similar elements
for item in similar:
    print(item.css('.name::text').get())
```

## Auto-generated Selectors

```python
# Generate robust CSS selector for an element
element = page.css('#unique-id .nested')[0]
css = element.generate_css_selector()    # CSS selector string
xpath = element.generate_xpath_selector()  # XPath selector string
```

## Selectors Collection

Multiple selectors returned from `css()`/`xpath()` form a `Selectors` collection:

```python
items = page.css('.item')

# Iteration
for item in items:
    print(item.css('.title::text').get())

# Indexing
items[0]
items[-1]

# Length
len(items)

# Chaining (applies to all)
items.css('.child::text').getall()

# First/last
items.first
items.last
```

## Configuration

```python
# Display current config
Fetcher.display_config()

# Configure parser settings globally
Fetcher.configure(
    keep_comments=False,       # strip HTML comments
    keep_cdata=False,          # strip CDATA sections
    huge_tree=True,            # enable lxml huge_tree for large docs
    adaptive=False,            # adaptive element tracking
)

# Per-request override
page = Fetcher.get('https://example.com', selector_config={'keep_comments': True})
```

## Gotchas

- **`::text` returns direct text only** — it does not include text from child elements. Use `get_all_text()` for full text extraction including nested content.
- **`get()` returns `None` on no match** — not an empty string. Check with `if result:` or use `get(default='fallback')`.
- **`getall()` returns empty list on no match** — never `None`.
- **CSS selectors are case-sensitive for class/id** — `.Class` ≠ `.class`. HTML is case-insensitive but CSS selectors are not.
- **`find_all` uses underscore for reserved words** — `class_` not `class`, `for_` not `for`.
- **`page.encoding` is detected from HTML meta or HTTP headers** — override with `Selector(html, encoding='utf-8')` if detection is wrong.
- **`auto_save` writes to SQLite** — default storage is `elements_storage.db` in the scrapling package directory. Use `storage_args` to customize the path.
- **`Response` inherits from `Selector`** — all Selector methods work on Response objects returned by fetchers.
- **`page.html_content` vs `page.body`** — `html_content` returns a string; `body` returns raw bytes.
