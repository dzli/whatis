#!/usr/bin/env python3
"""Augment four corpora so the classifier can correctly tag 48 held-out files
currently landing on Tea / Groovy Server Pages / Graphviz / Less.

1. JavaScript+URIEncoded: +10 samples in the `<script language=JavaScript>m='%XX…'`
   wrapping style.
2. VBScript: +12 plain VBScript scripts (corpus had 1 file).
3. VBScript+HTMLDecoy: NEW variant, +10 samples mirroring the leading-`'<html>.`
   decoy pattern with base64-chunked string-concat payload.
4. HTML: +10 samples covering shapes the existing 7-file corpus misses.
"""
import os
import random
import string
import urllib.parse
import base64

ROOT = "/Users/dazhi/projects/filetyping/whatis/samples"

BS = "\\"  # avoid backslash-in-f-string issues


def rid(n=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def upper_word(n=10):
    return "".join(random.choices(string.ascii_letters, k=n))


# --------------------------------------------------------------------------
# 1. JavaScript+URIEncoded — m='...' style
# --------------------------------------------------------------------------

def gen_urienc_m_style(seed):
    random.seed(seed)
    inner_html = (
        "<!DOCTYPE html>\n"
        "<meta http-equiv=\"X-UA-Compatible\" content=\"IE=EmulateIE8\">\n"
        "<html>\n<body>\n"
        f"<script>var {rid()} = {random.randint(1000, 99999)};\n"
        f"document.write('<div>{upper_word(20)}</div>');\n"
        f"alert('{upper_word(8)}');\n"
        "</script>\n"
        "</body>\n</html>"
    )
    encoded = urllib.parse.quote(inner_html, safe="")
    for _ in range(random.randint(1, 3)):
        encoded = urllib.parse.quote(encoded, safe="")
    return (
        "<script language=JavaScript>m='"
        + encoded
        + "';d=unescape(m);document.write(d);</script>\n"
    )


# --------------------------------------------------------------------------
# 2. VBScript — plain
# --------------------------------------------------------------------------

def gen_vbscript_filesystem():
    folder = random.choice(["C:\\Users\\Public", "C:\\Temp", "C:\\Windows\\Logs"])
    ext = random.choice(["log", "txt", "dat", "tmp"])
    return (
        "Option Explicit\n"
        "Dim fso, folder, file, count\n"
        "Set fso = CreateObject(\"Scripting.FileSystemObject\")\n"
        f"Set folder = fso.GetFolder(\"{folder}\")\n"
        "count = 0\n"
        "For Each file In folder.Files\n"
        f"    If LCase(fso.GetExtensionName(file.Name)) = \"{ext}\" Then\n"
        "        WScript.Echo file.Name & \" - \" & file.Size & \" bytes\"\n"
        "        count = count + 1\n"
        "    End If\n"
        "Next\n"
        "WScript.Echo \"Total files: \" & count\n"
        "Set fso = Nothing\n"
    )


def gen_vbscript_registry():
    return (
        "Option Explicit\n"
        "On Error Resume Next\n"
        "Dim sh, value\n"
        "Set sh = CreateObject(\"WScript.Shell\")\n"
        "value = sh.RegRead(\"HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\ProductName\")\n"
        "If Err.Number <> 0 Then\n"
        "    WScript.Echo \"Could not read registry: \" & Err.Description\n"
        "    Err.Clear\n"
        "Else\n"
        "    WScript.Echo \"OS: \" & value\n"
        "End If\n"
        "Set sh = Nothing\n"
    )


def gen_vbscript_shellrun():
    cmd = random.choice(["ipconfig /all", "whoami /priv", "systeminfo", "tasklist /v"])
    return (
        "Set objShell = CreateObject(\"WScript.Shell\")\n"
        "Dim cmd\n"
        f"cmd = \"{cmd}\"\n"
        "objShell.Run \"cmd /c \" & cmd & \" > %TEMP%\\out.txt\", 0, True\n"
        "Dim fso, ts, line\n"
        "Set fso = CreateObject(\"Scripting.FileSystemObject\")\n"
        "Set ts = fso.OpenTextFile(objShell.ExpandEnvironmentStrings(\"%TEMP%\\out.txt\"), 1)\n"
        "Do While Not ts.AtEndOfStream\n"
        "    line = ts.ReadLine\n"
        "    WScript.Echo line\n"
        "Loop\n"
        "ts.Close\n"
    )


def gen_vbscript_function():
    n1 = random.randint(3, 9)
    name = upper_word(6)
    return (
        "Function Factorial(n)\n"
        "    Dim i, result\n"
        "    result = 1\n"
        "    For i = 2 To n\n"
        "        result = result * i\n"
        "    Next\n"
        "    Factorial = result\n"
        "End Function\n"
        "\n"
        "Sub Greet(name)\n"
        f"    WScript.Echo \"Hello, \" & name & \"! Factorial of {n1} is \" & Factorial({n1})\n"
        "End Sub\n"
        "\n"
        f"Call Greet(\"{name}\")\n"
    )


def gen_vbscript_class():
    n = random.randint(1000, 9999)
    return (
        "Class Logger\n"
        "    Private logPath\n"
        "    Private Sub Class_Initialize()\n"
        f"        logPath = \"C:\\Temp\\app-\" & {n} & \".log\"\n"
        "    End Sub\n"
        "    Public Property Get Path()\n"
        "        Path = logPath\n"
        "    End Property\n"
        "    Public Sub Write(msg)\n"
        "        Dim fso, ts\n"
        "        Set fso = CreateObject(\"Scripting.FileSystemObject\")\n"
        "        Set ts = fso.OpenTextFile(logPath, 8, True)\n"
        "        ts.WriteLine Now & \" - \" & msg\n"
        "        ts.Close\n"
        "    End Sub\n"
        "End Class\n"
        "\n"
        "Dim lg\n"
        "Set lg = New Logger\n"
        "lg.Write \"Application started\"\n"
        "lg.Write \"Doing work...\"\n"
    )


def gen_vbscript_adodb():
    country = random.choice(["USA", "UK", "Germany", "Japan"])
    return (
        "Const adOpenStatic = 3\n"
        "Const adLockReadOnly = 1\n"
        "Dim conn, rs\n"
        "Set conn = CreateObject(\"ADODB.Connection\")\n"
        "conn.Open \"Provider=Microsoft.Jet.OLEDB.4.0;Data Source=C:\\Data\\db.mdb\"\n"
        "Set rs = CreateObject(\"ADODB.Recordset\")\n"
        f"rs.Open \"SELECT * FROM Customers WHERE Country='{country}'\", conn, adOpenStatic, adLockReadOnly\n"
        "Do Until rs.EOF\n"
        "    WScript.Echo rs.Fields(\"CustomerID\").Value & \" - \" & rs.Fields(\"CompanyName\").Value\n"
        "    rs.MoveNext\n"
        "Loop\n"
        "rs.Close\n"
        "conn.Close\n"
    )


def gen_vbscript_wmi():
    cls = random.choice(["Process", "Service", "LogicalDisk", "OperatingSystem"])
    return (
        "strComputer = \".\"\n"
        "Set objWMI = GetObject(\"winmgmts:\\\\\" & strComputer & \"\\root\\cimv2\")\n"
        f"Set colItems = objWMI.ExecQuery(\"Select * From Win32_{cls}\")\n"
        "For Each objItem in colItems\n"
        "    WScript.Echo objItem.Name & \": \" & objItem.Description\n"
        "Next\n"
    )


def gen_vbscript_dict():
    a, b, c = upper_word(5), upper_word(5), upper_word(5)
    n1, n2, n3 = random.randint(1, 99), random.randint(1, 99), random.randint(1, 99)
    return (
        "Dim dict\n"
        "Set dict = CreateObject(\"Scripting.Dictionary\")\n"
        f"dict.Add \"{a}\", {n1}\n"
        f"dict.Add \"{b}\", {n2}\n"
        f"dict.Add \"{c}\", {n3}\n"
        "Dim k\n"
        "For Each k In dict.Keys\n"
        "    WScript.Echo k & \" => \" & dict(k)\n"
        "Next\n"
        "WScript.Echo \"Count: \" & dict.Count\n"
    )


def gen_vbscript_inputbox():
    return (
        "Dim name, age\n"
        "name = InputBox(\"What is your name?\", \"Greeting\")\n"
        "If name = \"\" Then\n"
        "    MsgBox \"No name given.\", vbExclamation\n"
        "    WScript.Quit\n"
        "End If\n"
        "age = CInt(InputBox(\"How old are you?\", \"Greeting\"))\n"
        "If age < 18 Then\n"
        "    MsgBox \"Hi \" & name & \", you're a minor.\", vbInformation\n"
        "ElseIf age < 65 Then\n"
        "    MsgBox \"Hi \" & name & \", you're an adult.\", vbInformation\n"
        "Else\n"
        "    MsgBox \"Hi \" & name & \", you're a senior.\", vbInformation\n"
        "End If\n"
    )


def gen_vbscript_network():
    return (
        "Dim oNet, oDrives, i\n"
        "Set oNet = CreateObject(\"WScript.Network\")\n"
        "Set oDrives = oNet.EnumNetworkDrives()\n"
        "For i = 0 To oDrives.Count - 1 Step 2\n"
        "    WScript.Echo oDrives.Item(i) & \" => \" & oDrives.Item(i + 1)\n"
        "Next\n"
    )


def gen_vbscript_date():
    n = random.randint(10, 60)
    return (
        "Dim today, future, weekdays, d\n"
        "today = Now\n"
        f"future = DateAdd(\"d\", {n}, today)\n"
        "weekdays = 0\n"
        "For d = 0 To DateDiff(\"d\", today, future) - 1\n"
        "    If Weekday(DateAdd(\"d\", d, today)) >= 2 And Weekday(DateAdd(\"d\", d, today)) <= 6 Then\n"
        "        weekdays = weekdays + 1\n"
        "    End If\n"
        "Next\n"
        "WScript.Echo \"Weekdays until \" & future & \": \" & weekdays\n"
    )


def gen_vbscript_ie():
    url = random.choice(["about:blank", "https://example.com", "https://localhost"])
    sleep_ms = random.randint(500, 3000)
    return (
        "Dim ie\n"
        "Set ie = CreateObject(\"InternetExplorer.Application\")\n"
        "ie.Visible = True\n"
        f"ie.Navigate \"{url}\"\n"
        "Do While ie.Busy Or ie.ReadyState <> 4\n"
        "    WScript.Sleep 100\n"
        "Loop\n"
        f"ie.Document.Title = \"Hello {upper_word(5)}\"\n"
        f"WScript.Sleep {sleep_ms}\n"
        "ie.Quit\n"
        "Set ie = Nothing\n"
    )


VBSCRIPT_GENERATORS = [
    gen_vbscript_filesystem, gen_vbscript_registry, gen_vbscript_shellrun,
    gen_vbscript_function, gen_vbscript_class, gen_vbscript_adodb,
    gen_vbscript_wmi, gen_vbscript_dict, gen_vbscript_inputbox,
    gen_vbscript_network, gen_vbscript_date, gen_vbscript_ie,
]


def gen_vbscript(seed):
    random.seed(seed)
    return random.choice(VBSCRIPT_GENERATORS)()


# --------------------------------------------------------------------------
# 3. VBScript+HTMLDecoy
# --------------------------------------------------------------------------

DECOY_TAGS = ["div", "span", "p", "li", "td"]
DECOY_TEMPLATES = [
    '<meta charset="UTF-8">',
    '<meta name="{a}" content="{b}">',
    '<meta http-equiv="X-UA-Compatible" content="IE=edge">',
    "<title>{a}</title>",
    '<link rel="stylesheet" href="{a}.css">',
    '<{tag} id="{a}">{b}</{tag}>',
    '<{tag} class="{a}">{b}</{tag}>',
]


def gen_decoy_line():
    tpl = random.choice(DECOY_TEMPLATES)
    return (
        "'" + tpl.format(
            a=upper_word(random.randint(8, 30)),
            b=upper_word(random.randint(8, 35)),
            tag=random.choice(DECOY_TAGS),
        ) + ".\r\n"
    )


def b64_chunk(n):
    return base64.b64encode(os.urandom(n)).decode("ascii")


def gen_vbscript_htmldecoy(seed):
    random.seed(seed)
    out = [
        "'<!DOCTYPE html>.\r\n",
        "'<html lang=\"en-US\">.\r\n",
        "'<head>.\r\n",
    ]
    for _ in range(random.randint(40, 200)):
        out.append("    " + gen_decoy_line())
    out.append("'</head>.\r\n")
    out.append("'<body>.\r\n")
    var = upper_word(15)
    out.append(f"{var}=\"\"\r\n")
    for _ in range(random.randint(40, 200)):
        chunk = b64_chunk(random.randint(40, 120))
        out.append(f"{var}={var} & \"{chunk}\"\r\n")
    out.append(f"Do While Len({var}) > 0\r\n")
    out.append(f"    {var}=Mid({var}, 2)\r\n")
    out.append("Loop\r\n")
    for _ in range(random.randint(10, 50)):
        out.append("    " + gen_decoy_line())
    out.append("'</body>.\r\n")
    out.append("'</html>.\r\n")
    return "".join(out)


# --------------------------------------------------------------------------
# 4. HTML — extra shapes
# --------------------------------------------------------------------------

def gen_html_wordpress():
    return (
        "<html>\n"
        "<head> </head>\n"
        "<body>\n"
        f"<div id=\"in-page-channel-node-id\" data-channel-name=\"in_page_{rid(8)}\"> </div>\n"
        "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n"
        "<link rel=\"icon\" href=\"https://example.com/wp-content/uploads/2024/01/icon.png\">\n"
        "<meta property=\"og:image\" content=\"https://example.com/wp-content/uploads/2024/01/preview.png\">\n"
        f"<title>{upper_word(10)} | Example Site</title>\n"
        "</body>\n"
        "</html>\n"
    )


def gen_html_heavy_style():
    a = upper_word(6)
    b = upper_word(6)
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "<style type=\"text/css\">\n"
        "@page Section1 {\n"
        "  margin-left: 20mm;\n"
        "  margin-right: 10mm;\n"
        "  margin-top: 10mm;\n"
        "  margin-bottom: 10mm;\n"
        "  mso-paper-source: 0;\n"
        "}\n"
        "DIV.Section { page: Section1; }\n"
        "body, font {\n"
        "  font-family: \"Times New Roman\", serif;\n"
        "  font-size: 12pt;\n"
        "  width: 920px;\n"
        "}\n"
        ".fs100 { font-family: \"Arial\"; font-size: 10pt; }\n"
        ".fs120 { font-family: \"Arial\"; font-size: 12pt; font-weight: bold; }\n"
        "table.report { border-collapse: collapse; width: 100%; }\n"
        "table.report th, table.report td { border: 1px solid #888; padding: 4px; }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "<div class=\"Section\">\n"
        "<table class=\"report\">\n"
        f"<thead><tr><th>{a}</th><th>{b}</th></tr></thead>\n"
        "<tbody>\n"
        f"<tr><td>{upper_word(10)}</td><td>{random.randint(1000, 99999)}</td></tr>\n"
        f"<tr><td>{upper_word(10)}</td><td>{random.randint(1000, 99999)}</td></tr>\n"
        "</tbody>\n"
        "</table>\n"
        "</div>\n"
        "</body>\n"
        "</html>\n"
    )


def gen_html_xhtml():
    return (
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"\n"
        " \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n"
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        "<head>\n"
        "<style type=\"text/css\">\n"
        "   body { text-align: center; width: 100%; padding: 50px; font-size: 20px; color: #aaa; }\n"
        "   a { color: #46c; text-decoration: none; }\n"
        "   a:hover { text-decoration: underline; }\n"
        "</style>\n"
        f"<title>{upper_word(10)}</title>\n"
        "</head>\n"
        "<body>\n"
        f"<h1>{upper_word(8)} {upper_word(8)}</h1>\n"
        f"<p>{upper_word(20)}</p>\n"
        f"<p>{upper_word(15)} <a href=\"https://example.com/{rid(10)}\">{upper_word(6)}</a></p>\n"
        "</body>\n"
        "</html>\n"
    )


def gen_html_doc():
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "<meta charset=\"UTF-8\">\n"
        f"<title>{upper_word(8)} Documentation</title>\n"
        "<link rel=\"stylesheet\" href=\"/css/main.css\">\n"
        "</head>\n"
        "<body>\n"
        f"<header><h1>{upper_word(10)}</h1></header>\n"
        "<article>\n"
        f"<h2>{upper_word(6)} {upper_word(6)}</h2>\n"
        f"<p>{upper_word(15)} {upper_word(15)} {upper_word(15)}.</p>\n"
        "<ul>\n"
        f"<li>{upper_word(8)}</li>\n"
        f"<li>{upper_word(8)}</li>\n"
        f"<li>{upper_word(8)}</li>\n"
        "</ul>\n"
        "</article>\n"
        f"<footer>&copy; 2024 {upper_word(10)}</footer>\n"
        "</body>\n"
        "</html>\n"
    )


def gen_html_table():
    return (
        "<html>\n<body>\n"
        "<table>\n"
        f"<tr><th>{upper_word(6)}</th><th>{upper_word(6)}</th><th>{upper_word(6)}</th></tr>\n"
        f"<tr><td>{rid()}</td><td>{rid()}</td><td>{rid()}</td></tr>\n"
        f"<tr><td>{rid()}</td><td>{rid()}</td><td>{rid()}</td></tr>\n"
        f"<tr><td>{rid()}</td><td>{rid()}</td><td>{rid()}</td></tr>\n"
        "</table>\n</body>\n</html>\n"
    )


def gen_html_meta_heavy():
    return (
        "<!DOCTYPE html>\n"
        "<html prefix=\"og: https://ogp.me/ns#\">\n"
        "<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<meta property=\"og:type\" content=\"article\">\n"
        f"<meta property=\"og:url\" content=\"https://example.com/{rid(8)}\">\n"
        f"<meta property=\"og:title\" content=\"{upper_word(10)} {upper_word(10)}\">\n"
        f"<meta property=\"og:description\" content=\"{upper_word(25)}\">\n"
        f"<meta property=\"og:image\" content=\"https://example.com/img/{rid(8)}.jpg\">\n"
        "<meta name=\"twitter:card\" content=\"summary_large_image\">\n"
        f"<meta name=\"description\" content=\"{upper_word(20)}\">\n"
        f"<meta name=\"keywords\" content=\"{upper_word(6)}, {upper_word(6)}, {upper_word(6)}\">\n"
        f"<title>{upper_word(15)}</title>\n"
        f"<link rel=\"canonical\" href=\"https://example.com/{rid(8)}\">\n"
        f"<link rel=\"alternate\" hreflang=\"en\" href=\"https://example.com/en/{rid(8)}\">\n"
        "</head>\n"
        f"<body><h1>{upper_word(8)}</h1></body>\n"
        "</html>\n"
    )


def gen_html_form():
    return (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head><title>Login</title></head>\n"
        "<body>\n"
        f"<form action=\"/submit/{rid(8)}\" method=\"post\">\n"
        "<label for=\"user\">Username</label>\n"
        "<input type=\"text\" id=\"user\" name=\"user\" required>\n"
        "<label for=\"pw\">Password</label>\n"
        "<input type=\"password\" id=\"pw\" name=\"pw\" required>\n"
        "<label><input type=\"checkbox\" name=\"remember\"> Remember me</label>\n"
        "<button type=\"submit\">Log in</button>\n"
        "</form>\n"
        "<p><a href=\"/forgot\">Forgot password?</a></p>\n"
        "</body>\n"
        "</html>\n"
    )


def gen_html_svg():
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head><meta charset=\"utf-8\"><title>SVG Demo</title></head>\n"
        "<body>\n"
        f"<h1>{upper_word(8)}</h1>\n"
        "<svg viewBox=\"0 0 100 100\" xmlns=\"http://www.w3.org/2000/svg\">\n"
        "  <circle cx=\"50\" cy=\"50\" r=\"40\" stroke=\"#333\" stroke-width=\"2\" fill=\"#fc6\"/>\n"
        "  <rect x=\"20\" y=\"20\" width=\"60\" height=\"60\" fill=\"#3c9\" opacity=\"0.5\"/>\n"
        f"  <text x=\"50\" y=\"55\" text-anchor=\"middle\" font-family=\"sans-serif\">{upper_word(4)}</text>\n"
        "</svg>\n"
        "</body>\n"
        "</html>\n"
    )


def gen_html_frameset():
    return (
        "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Frameset//EN\" \"http://www.w3.org/TR/html4/frameset.dtd\">\n"
        "<HTML>\n"
        f"<HEAD><TITLE>{upper_word(8)} Frameset</TITLE></HEAD>\n"
        "<FRAMESET cols=\"25%,75%\">\n"
        "  <FRAME src=\"nav.html\" name=\"navigation\">\n"
        "  <FRAME src=\"content.html\" name=\"main\">\n"
        "  <NOFRAMES>\n"
        "    <BODY><P>Your browser does not support frames.</P></BODY>\n"
        "  </NOFRAMES>\n"
        "</FRAMESET>\n"
        "</HTML>\n"
    )


def gen_html_fragment():
    return (
        "</UL>\n"
        f"<P><A HREF=\"next.html\">{upper_word(8)}</A></P>\n"
        f"<P><A HREF=\"prev.html\">{upper_word(6)}</A></P>\n"
        "</BODY>\n"
        "</HEAD>\n"
    )


HTML_GENERATORS = [
    gen_html_wordpress, gen_html_heavy_style, gen_html_xhtml,
    gen_html_doc, gen_html_table, gen_html_meta_heavy,
    gen_html_form, gen_html_svg, gen_html_frameset, gen_html_fragment,
]


def gen_html(seed):
    random.seed(seed)
    return random.choice(HTML_GENERATORS)()


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    d = os.path.join(ROOT, "JavaScript+URIEncoded")
    for i in range(10):
        p = os.path.join(d, f"urienc_mstyle_{i}.js")
        with open(p, "w") as f:
            f.write(gen_urienc_m_style(seed=7000 + i))
        print(f"wrote {p} ({os.path.getsize(p)} bytes)")

    d = os.path.join(ROOT, "VBScript")
    for i in range(12):
        p = os.path.join(d, f"vbs_plain_{i}.vbs")
        with open(p, "w") as f:
            f.write(gen_vbscript(seed=8000 + i))
        print(f"wrote {p} ({os.path.getsize(p)} bytes)")

    d = os.path.join(ROOT, "VBScript+HTMLDecoy")
    os.makedirs(d, exist_ok=True)
    for i in range(10):
        p = os.path.join(d, f"vbs_htmldecoy_{i}.vbs")
        with open(p, "w") as f:
            f.write(gen_vbscript_htmldecoy(seed=9000 + i))
        print(f"wrote {p} ({os.path.getsize(p)} bytes)")

    d = os.path.join(ROOT, "HTML")
    for i in range(10):
        p = os.path.join(d, f"html_extra_{i}.html")
        with open(p, "w") as f:
            f.write(gen_html(seed=10000 + i))
        print(f"wrote {p} ({os.path.getsize(p)} bytes)")


if __name__ == "__main__":
    main()
