def tag(tag: str):
    def custom_tag(*inner_html, classes=None, **attrs):
        inner_html = "".join(inner_html)
        class_attr = f" class='{ ' '.join(classes) }'" if classes else ""
        other_attrs = " ".join(f"{key}='{value}'" for key, value in attrs.items())

        if inner_html:
            return f"<{tag}{class_attr} {other_attrs}>{inner_html}</{tag}>"
        else:
            return f"<{tag}{class_attr} {other_attrs} />"
    return custom_tag


def html(body_content="", head_content="", styles=""):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        {head_content}
        {styles}
    </head>
    <body>
        {body_content}
    </body>
    </html>
    """


p = tag("p")
div = tag("div")
span = tag("span")
h1 = tag("h1")
h2 = tag("h2")
h3 = tag("h3")
h4 = tag("h4")
h5 = tag("h5")
h6 = tag("h6")
ul = tag("ul")
ol = tag("ol")
li = tag("li")
a = tag("a")
img = tag("img")
button = tag("button")
input_ = tag("input")  # `input` is a reserved keyword in Python
form = tag("form")
label = tag("label")
table = tag("table")
thead = tag("thead")
tbody = tag("tbody")
tr = tag("tr")
th = tag("th")
td = tag("td")
section = tag("section")
article = tag("article")
header = tag("header")
footer = tag("footer")
main = tag("main")
nav = tag("nav")
blockquote = tag("blockquote")
code = tag("code")
pre = tag("pre")
strong = tag("strong")
em = tag("em")
small = tag("small")
hr = tag("hr")
br = tag("br")
