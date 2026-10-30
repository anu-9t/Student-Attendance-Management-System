"""System validation run (STP Section 5, system level): black-box tests against a running SAMS server.

It drives the application over HTTP the way a browser does (log in, fill forms, follow redirects) and
checks what each role sees. Nothing is imported from the application.

Run it against a server that has fresh sample data (python manage.py seed_data), for example:

    DB_ENGINE=sqlite python manage.py migrate && DB_ENGINE=sqlite python manage.py seed_data
    openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj /CN=localhost -keyout key.pem -out cert.pem
    DB_ENGINE=sqlite DJANGO_DEBUG=0 DJANGO_SECRET_KEY=<any long value> DJANGO_ALLOWED_HOSTS=127.0.0.1 \\
        DJANGO_CSRF_TRUSTED_ORIGINS=https://127.0.0.1:8443 \\
        gunicorn sams.wsgi --bind 127.0.0.1:8443 --workers 2 --certfile cert.pem --keyfile key.pem
    python tools/system_validation.py --base-url https://127.0.0.1:8443 --insecure --out results.json

Against the Docker stack: --base-url https://localhost --insecure (the local certificate is self-signed).
It changes data (adds a student, marks attendance), so use a fresh database each time.
"""

import argparse
import datetime as dt
import html
import http.client
import json
import re
import ssl
import statistics
import sys
import threading
import time
import urllib.parse
from html.parser import HTMLParser

PASSWORD = "Sams@12345"  # the seed_data development password


class FormParser(HTMLParser):
    """Collects the forms on a page: action, method and the fields with their default values."""

    def __init__(self):
        super().__init__()
        self.forms, self._form, self._selecting = [], None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self._form = {"action": a.get("action", ""), "method": a.get("method", "get").lower(), "fields": {}}
            self.forms.append(self._form)
        elif self._form is not None and tag in ("input", "select", "option", "textarea"):
            getattr(self, f"_{tag}")(a)

    def _input(self, a):
        kind, name = a.get("type", "text"), a.get("name")
        if not name or kind in ("submit", "button"):
            return
        if kind not in ("radio", "checkbox"):
            self._form["fields"][name] = a.get("value", "")
        elif "checked" in a:
            self._form["fields"].setdefault(name, a.get("value", "on"))

    def _select(self, a):
        if a.get("name"):
            self._selecting = a["name"]
            self._form["fields"].setdefault(self._selecting, "")

    def _option(self, a):
        name = self._selecting
        if name and a.get("value") and ("selected" in a or not self._form["fields"][name]):
            self._form["fields"][name] = a["value"]

    def _textarea(self, a):
        if a.get("name"):
            self._form["fields"][a["name"]] = ""

    def handle_endtag(self, tag):
        if tag == "form":
            self._form = None
        elif tag == "select":
            self._selecting = None


class Browser:
    """A minimal browser: cookies, redirects, CSRF from the page's forms."""

    def __init__(self, base, insecure=False):
        u = urllib.parse.urlsplit(base)
        self.https, self.host = u.scheme == "https", u.netloc
        self.ctx = ssl.create_default_context()
        if insecure:
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE
        self.cookies, self.last, self.set_cookie_log = {}, None, []

    def _conn(self):
        if self.https:
            return http.client.HTTPSConnection(self.host, timeout=30, context=self.ctx)
        return http.client.HTTPConnection(self.host, timeout=30)

    def request(self, method, path, data=None, follow=True, referer=None):
        body, headers = None, {"Cookie": "; ".join(f"{k}={v}" for k, v in self.cookies.items())}
        scheme = "https" if self.https else "http"
        headers["Referer"] = referer or f"{scheme}://{self.host}{path}"
        if data is not None:
            body = urllib.parse.urlencode(data, doseq=True)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            if "csrftoken" in self.cookies:
                headers["X-CSRFToken"] = self.cookies["csrftoken"]
        start = time.perf_counter()
        conn = self._conn()
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        elapsed = time.perf_counter() - start
        for header, value in resp.getheaders():
            if header.lower() == "set-cookie":
                self.set_cookie_log.append(value)
                name, _, rest = value.partition("=")
                val = rest.split(";", 1)[0]
                if val in ('""', "") or "Max-Age=0" in value:
                    self.cookies.pop(name, None)
                else:
                    self.cookies[name] = val
        page = Page(path, resp.status, dict((k.lower(), v) for k, v in resp.getheaders()), raw, elapsed)
        page.set_cookies = [v for k, v in resp.getheaders() if k.lower() == "set-cookie"]
        conn.close()
        if follow and resp.status in (301, 302, 303) and "location" in page.headers:
            loc = urllib.parse.urlsplit(page.headers["location"])
            nxt = loc.path + (f"?{loc.query}" if loc.query else "")
            follow_page = self.request("GET", nxt, follow=True)
            follow_page.redirected_from = page
            follow_page.elapsed += elapsed
            self.last = follow_page
            return follow_page
        self.last = page
        return page

    def get(self, path, follow=True):
        return self.request("GET", path, follow=follow)

    def submit(self, page, form_index=None, match=None, **overrides):
        """Fill a form found on `page` (the first whose action contains `match`) and submit it."""
        forms = page.forms()
        if match is not None:
            forms = [f for f in forms if match in (f["action"] or page.path)]
        form = forms[form_index or 0] if form_index is None else page.forms()[form_index]
        fields = dict(form["fields"])
        for key, value in overrides.items():
            if value is None:
                fields.pop(key, None)
            else:
                fields[key] = value
        action = form["action"] or page.path
        if form["method"] == "post":
            return self.request("POST", action, data=fields, referer=self._abs(page.path))
        return self.get(action.split("?")[0] + "?" + urllib.parse.urlencode(fields, doseq=True))

    def _abs(self, path):
        return f"{'https' if self.https else 'http'}://{self.host}{path}"

    def login(self, username, password=PASSWORD):
        page = self.get("/login/")
        return self.submit(page, match="login", username=username, password=password)


class Page:
    def __init__(self, path, status, headers, raw, elapsed):
        self.path, self.status, self.headers, self.raw, self.elapsed = path, status, headers, raw, elapsed
        self.redirected_from = None
        self.text = raw.decode("utf-8", "replace") if "text" in headers.get("content-type", "") else ""

    def forms(self):
        p = FormParser()
        p.feed(self.text)
        return p.forms

    def has(self, *needles):
        return all(n in self.text for n in needles)

    def title(self):
        m = re.search(r"<title>(.*?)</title>", self.text, re.S)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

    def links(self, pattern):
        return re.findall(r'href="(' + pattern + r')"', self.text)

    def message(self):
        m = re.search(r'class="alert[^"]*"[^>]*>(.*?)</div>', self.text, re.S)
        return html.unescape(re.sub(r"<[^>]+>|\s+", " ", m.group(1)).strip()) if m else ""


RESULTS = []


def case(cid, module, uc, reqs, description, preconditions, steps, data, expected):
    """Decorator: registers a test case with the columns of the course's test case template."""

    def wrap(fn):
        RESULTS.append(
            {"id": cid, "module": module, "use_case": uc, "requirements": reqs, "description": description,
             "preconditions": preconditions, "steps": steps, "data": data, "expected": expected, "fn": fn}
        )
        return fn

    return wrap


class Ctx:
    """State shared between test cases (things created by earlier cases)."""


def run(base, insecure):
    ctx = Ctx()
    ctx.base, ctx.insecure = base, insecure
    ctx.new = lambda: Browser(base, insecure)
    ctx.today = dt.date.today()
    for tc in RESULTS:
        try:
            ok, actual = tc["fn"](ctx)
        except Exception as exc:  # a crash in one case is recorded as a failure, the run goes on
            ok, actual = False, f"Error while running: {exc!r}"
        tc["actual"], tc["result"] = actual, "Pass" if ok else "Fail"
        print(f"{tc['id']:7} {tc['result']:4}  {tc['description']}")
    return RESULTS


# ---- UC-04 / authentication and access ---------------------------------------------------------


@case("ST-01", "Login (accounts)", "UC-04", "SAM-F-001, SAM-F-003", "Valid login takes each role to its own dashboard",
      "Server running with seed_data", "1. Open /login/\n2. Enter username and password\n3. Submit",
      "admin / faculty1 / student1, password Sams@12345",
      "Admin, Faculty and Student dashboards respectively")
def st01(ctx):
    seen = []
    for user, title in (("admin", "Administrator Dashboard"), ("faculty1", "Faculty Dashboard"),
                        ("student1", "Student Dashboard")):
        b = ctx.new()
        page = b.login(user)
        seen.append((user, page.path, title in page.text))
    ok = all(found for _, _, found in seen)
    return ok, "; ".join(f"{u} landed on {p} ({'dashboard shown' if f else 'dashboard missing'})" for u, p, f in seen)


@case("ST-02", "Login (accounts)", "UC-04", "SAM-F-002", "Wrong password is refused with a message",
      "Server running", "1. Open /login/\n2. Enter a wrong password\n3. Submit",
      "student1 / WrongPass1", "Login page shown again with an error; no session")
def st02(ctx):
    b = ctx.new()
    page = b.login("student2", "WrongPass1")
    err = "Wrong username or password" in page.text
    ok = page.path.startswith("/login/") and err and "sessionid" not in b.cookies
    return ok, f"Stayed on {page.path}; error message {'shown' if err else 'missing'}; " \
               f"session cookie {'not set' if 'sessionid' not in b.cookies else 'set'}"


@case("ST-03", "Access control", "UC-04", "SAM-SEC-001", "Every page needs a login",
      "Not logged in", "1. Open each protected URL without logging in",
      "/dashboard/, /students/, /attendance/select/, /reports/, /audit/, /percentage/",
      "Each request is redirected to /login/")
def st03(ctx):
    b = ctx.new()
    out = []
    for path in ("/dashboard/", "/students/", "/attendance/select/", "/reports/", "/audit/", "/percentage/"):
        page = b.get(path, follow=False)
        out.append((path, page.status, page.headers.get("location", "")))
    ok = all(s == 302 and "/login/" in loc for _, s, loc in out)
    return ok, "; ".join(f"{p} -> {s} {loc.split('?')[0]}" for p, s, loc in out)


@case("ST-04", "Access control", "UC-04", "SAM-SEC-002", "Each role reaches only its own pages",
      "Logged in as student1, then as faculty1", "1. As a student, open admin and faculty pages\n"
      "2. As faculty, open admin pages", "/students/, /audit/, /attendance/select/, /subjects/",
      "403 Forbidden for every page outside the role")
def st04(ctx):
    out = []
    s = ctx.new()
    s.login("student1")
    for path in ("/students/", "/audit/", "/attendance/select/", "/subjects/"):
        out.append(("student", path, s.get(path, follow=False).status))
    f = ctx.new()
    f.login("faculty1")
    for path in ("/students/", "/audit/", "/subjects/"):
        out.append(("faculty", path, f.get(path, follow=False).status))
    ok = all(code == 403 for *_, code in out)
    return ok, "; ".join(f"{r} {p} -> {c}" for r, p, c in out)


@case("ST-05", "Login lockout", "UC-04", "SAM-SEC-003", "Account locks after 5 failed logins",
      "faculty2 not used in this run", "1. Submit 5 wrong passwords for faculty2\n2. Try the correct password",
      "faculty2 / Wrong1234 (x5), then Sams@12345",
      "6th attempt refused with HTTP 429 and a lockout message, even with the right password")
def st05(ctx):
    b = ctx.new()
    for _ in range(5):
        b.login("faculty2", "Wrong1234")
    page = b.login("faculty2")
    ok = page.status == 429 and "sessionid" not in b.cookies
    return ok, f"After 5 failures the correct password returned HTTP {page.status}" \
               f"{' with the lockout page' if 'locked' in page.text.lower() else ''}"


# ---- UC-04 / administration --------------------------------------------------------------------


@case("ST-06", "Student management", "UC-04", "SAM-F-004", "Admin adds a student, who can then log in",
      "Logged in as admin; class CSE-5A exists", "1. Students -> Add\n2. Fill the form\n3. Save\n"
      "4. Log in as the new student", "SRN PES2UG24CS200, name Test Student, test@example.com, CSE-5A, "
      "password Welcome@123", "Student listed; the new login reaches the student dashboard")
def st06(ctx):
    b = ctx.new()
    b.login("admin")
    page = b.get("/students/add/")
    page = b.submit(page, match="add", srn="pes2ug24cs200", name="Test Student", email="test@example.com",
                    password="Welcome@123")
    listed = b.get("/students/?q=PES2UG24CS200").has("PES2UG24CS200", "Test Student")
    s = ctx.new()
    dash = s.login("PES2UG24CS200", "Welcome@123")
    ok = listed and "Student Dashboard" in dash.text
    return ok, f"Saved ({page.message() or 'no message'}); listed: {listed}; new login reached " \
               f"{'the student dashboard' if 'Student Dashboard' in dash.text else dash.path}"


@case("ST-07", "Student management", "UC-04", "SAM-F-006", "Search students by SRN or name",
      "ST-06 done", "1. Students\n2. Search by part of the SRN, then by name", "q=CS200, q=test student",
      "Only matching students listed")
def st07(ctx):
    b = ctx.new()
    b.login("admin")
    by_srn = b.get("/students/?q=CS200")
    by_name = b.get("/students/?q=test+student")
    rows_srn = len(re.findall(r"PES2UG24CS\d{3}", by_srn.text))
    ok = by_srn.has("PES2UG24CS200") and "PES2UG24CS091" not in by_srn.text and by_name.has("PES2UG24CS200")
    return ok, f"q=CS200 listed {rows_srn} SRN(s) incl. PES2UG24CS200; q=test student found it: " \
               f"{by_name.has('PES2UG24CS200')}"


@case("ST-08", "Student management", "UC-04", "SAM-F-005", "Edit, then deactivate a student (never deleted)",
      "ST-06 done", "1. Edit the student's name\n2. Deactivate the student\n3. List, then list with 'show all'",
      "Name changed to Test Student Two", "Name updated; hidden from the active list; still shown under 'all'")
def st08(ctx):
    b = ctx.new()
    b.login("admin")
    listing = b.get("/students/?q=PES2UG24CS200")
    edit = listing.links(r"/students/\d+/edit/")[0]
    pk = edit.split("/")[2]
    b.submit(b.get(edit), match="edit", name="Test Student Two")
    renamed = b.get("/students/?q=PES2UG24CS200").has("Test Student Two")
    b.submit(b.get("/students/?q=PES2UG24CS200"), match=f"/students/{pk}/deactivate/")
    hidden = "Test Student Two" not in b.get("/students/?q=PES2UG24CS200").text
    kept = b.get("/students/?q=PES2UG24CS200&show=all").has("Test Student Two")
    ok = renamed and hidden and kept
    return ok, f"renamed: {renamed}; hidden from active list: {hidden}; still in 'all': {kept}"


@case("ST-09", "Faculty management", "UC-04", "SAM-F-007", "Admin adds a faculty member",
      "Logged in as admin", "1. Faculty -> Add\n2. Fill the form\n3. Save", "F900, Test Faculty, CSE",
      "Faculty member listed")
def st09(ctx):
    b = ctx.new()
    b.login("admin")
    page = b.get("/faculty/add/")
    fields = page.forms()[-1]["fields"]
    extra = {k: "testfac900" for k in fields if "user" in k}
    extra.update({k: "Welcome@123" for k in fields if "password" in k})
    page = b.submit(page, match="add", employee_id="F900", name="Test Faculty", department="CSE", **extra)
    ok = b.get("/faculty/").has("F900", "Test Faculty")
    return ok, f"{page.message() or 'saved'}; listed: {ok}"


@case("ST-10", "Subject management", "UC-04", "SAM-F-008", "Admin adds a subject and a time slot",
      "Logged in as admin", "1. Subjects -> Add, save\n2. Time slots -> Add, save",
      "UE24CS399A Test Subject sem 5; slot 'Test slot' 18:00-19:00", "Both listed")
def st10(ctx):
    b = ctx.new()
    b.login("admin")
    b.submit(b.get("/subjects/add/"), match="add", code="UE24CS399A", name="Test Subject", semester="5")
    b.submit(b.get("/subjects/time-slots/add/"), match="add", label="Test slot", start_time="18:00",
             end_time="19:00")
    subj = b.get("/subjects/").has("UE24CS399A")
    slot = b.get("/subjects/time-slots/").has("Test slot")
    return subj and slot, f"subject listed: {subj}; time slot listed: {slot}"


@case("ST-11", "Subject assignment", "UC-04", "SAM-F-009", "Admin assigns a subject and class to a faculty member",
      "ST-09 and ST-10 done", "1. Subject Assignments\n2. Pick faculty, subject, class\n3. Assign",
      "Test Faculty, UE24CS399A, CSE-5A", "Assignment listed")
def st11(ctx):
    b = ctx.new()
    b.login("admin")
    page = b.get("/subjects/assignments/")
    sel = {}
    for name, label in (("faculty", "Test Faculty"), ("subject", "UE24CS399A"), ("class_group", "CSE-5A")):
        m = re.search(r'<option value="(\d+)"[^>]*>[^<]*' + re.escape(label), page.text)
        sel[name] = m.group(1) if m else ""
    b.submit(page, match="assignments", **sel)
    after = b.get("/subjects/assignments/")
    ok = bool(re.search(r"Test Faculty.*?UE24CS399A|UE24CS399A.*?Test Faculty", after.text, re.S))
    return ok, f"assignment listed: {ok}"


# ---- UC-02 / UC-01 attendance ------------------------------------------------------------------


def _faculty_sheet(ctx):
    b = ctx.new()
    b.login("faculty1")
    select = b.get("/attendance/select/")
    marks = select.links(r"/attendance/mark/\d+/\d+/")
    return b, select, marks


@case("ST-12", "Select class (attendance)", "UC-02", "SAM-F-010", "Faculty sees only their assigned class/subject pairs",
      "Logged in as faculty1 (teaches UE24CS341A to CSE-5A and CSE-5B)", "1. Mark Attendance\n2. Read the list",
      "-", "Exactly the 2 assigned pairs; Computer Networks / DBMS not offered")
def st12(ctx):
    b, select, marks = _faculty_sheet(ctx)
    pairs = len(re.findall(r'name="class_id"', select.text)) or len(set(marks))
    ok = pairs == 2 and "UE24CS341A" in select.text and "UE24CS342A" not in select.text
    return ok, f"{pairs} class/subject pairs offered; other faculty's subjects shown: {'UE24CS342A' in select.text}"


def _open_sheet(ctx):
    b, select = ctx.new(), None
    b.login("faculty1")
    select = b.get("/attendance/select/")
    chosen = b.submit(select, match="select")  # the first pair: CSE-5A / UE24CS341A
    sheet = b.get(chosen.links(r"/attendance/mark/\d+/\d+/")[0])
    return b, sheet


@case("ST-13", "Mark attendance", "UC-01", "SAM-F-011, SAM-F-012", "Faculty marks a class for one slot",
      "Logged in as faculty1", "1. Select CSE-5A / UE24CS341A\n2. Pick today and slot 1\n"
      "3. Mark the first student Absent, others Present\n4. Save", "today's date, first slot",
      "Confirmation 'Saved attendance for N students, 1 slot'")
def st13(ctx):
    b, sheet = _open_sheet(ctx)
    ctx.sheet_path = sheet.path
    form = [f for f in sheet.forms() if f["method"] == "post" and "date" in f["fields"]][0]
    slot = re.search(r'name="slots" value="(\d+)"', sheet.text).group(1)
    statuses = sorted(k for k in form["fields"] if k.startswith("status_"))
    over = {statuses[0]: "ABSENT"}
    ctx.absent_field, ctx.slot = statuses[0], slot
    page = b.submit(sheet, form_index=sheet.forms().index(form), date=ctx.today.isoformat(), slots=slot, **over)
    msg = page.message()
    ok = "Saved attendance for" in msg
    return ok, msg or f"no confirmation (HTTP {page.status})"


@case("ST-14", "Mark attendance", "UC-01", "SAM-F-013", "The same class, date and slot can't be saved twice",
      "ST-13 done", "1. Open the same sheet\n2. Same date and slot\n3. Save", "today, first slot",
      "Refused with 'already saved'; nothing new stored")
def st14(ctx):
    b = ctx.new()
    b.login("faculty1")
    sheet = b.get(ctx.sheet_path)
    form = [f for f in sheet.forms() if f["method"] == "post" and "date" in f["fields"]][0]
    page = b.submit(sheet, form_index=sheet.forms().index(form), date=ctx.today.isoformat(), slots=ctx.slot)
    ok = "already saved" in page.text
    return ok, page.message() or "no message"


@case("ST-15", "Mark attendance", "UC-01", "SAM-F-012", "A future date is refused",
      "Logged in as faculty1", "1. Open the sheet\n2. Pick tomorrow\n3. Save", "tomorrow's date",
      "Refused: attendance can't be marked for a future date")
def st15(ctx):
    b = ctx.new()
    b.login("faculty1")
    sheet = b.get(ctx.sheet_path)
    form = [f for f in sheet.forms() if f["method"] == "post" and "date" in f["fields"]][0]
    tomorrow = (ctx.today + dt.timedelta(days=1)).isoformat()
    page = b.submit(sheet, form_index=sheet.forms().index(form), date=tomorrow, slots=ctx.slot)
    ok = "future date" in page.text
    return ok, page.message() or "no message"


@case("ST-16", "Mark attendance", "UC-02", "SAM-SEC-002, SAM-SEC-004",
      "Faculty can't open a class or subject they don't teach", "Logged in as faculty1",
      "1. Type the URL of faculty2's class/subject sheet", "/attendance/mark/<CSE-5A>/<UE24CS342A>/",
      "Refused (403 or 404); no sheet shown")
def st16(ctx):
    b = ctx.new()
    b.login("faculty1")
    cls, subj = ctx.sheet_path.strip("/").split("/")[2:4]
    other = b.get(f"/attendance/mark/{cls}/{int(subj) + 1}/", follow=False)
    ok = other.status in (403, 404)
    return ok, f"HTTP {other.status}"


@case("ST-17", "Modify attendance", "UC-01", "SAM-F-014", "A correction without a reason is refused",
      "ST-13 done", "1. Modify -> today, slot 1\n2. Change a status\n3. Save with an empty reason", "reason ''",
      "Refused: a reason is required; nothing changed")
def st17(ctx):
    b = ctx.new()
    b.login("faculty1")
    mod = ctx.sheet_path.replace("/mark/", "/modify/")
    page = b.get(f"{mod}?date={ctx.today.isoformat()}&slot={ctx.slot}")
    form = [f for f in page.forms() if f["method"] == "post" and "reason" in f["fields"]][0]
    status_field = sorted(k for k in form["fields"] if k.startswith("status_"))[0]
    ctx.modify_page, ctx.status_field = page.path + f"?date={ctx.today.isoformat()}&slot={ctx.slot}", status_field
    after = b.submit(page, form_index=page.forms().index(form), reason="", **{status_field: "PRESENT"})
    ok = "reason" in after.message().lower() and "Updated" not in after.text
    return ok, after.message() or "no message"


@case("ST-18", "Modify attendance", "UC-01, UC-05", "SAM-F-014, SAM-SEC-005",
      "A correction with a reason is saved and logged", "ST-13 done",
      "1. Modify -> today, slot 1\n2. Change the absent student to Present\n3. Reason given\n4. Save\n"
      "5. Admin opens the audit log", "reason 'Medical certificate shown'",
      "'Updated 1 record'; audit log has the change and the reason")
def st18(ctx):
    b = ctx.new()
    b.login("faculty1")
    page = b.get(ctx.modify_page)
    form = [f for f in page.forms() if f["method"] == "post" and "reason" in f["fields"]][0]
    after = b.submit(page, form_index=page.forms().index(form), reason="Medical certificate shown",
                     **{ctx.status_field: "PRESENT"})
    a = ctx.new()
    a.login("admin")
    logged = a.get("/audit/?q=Medical+certificate").has("Medical certificate shown")
    ok = "Updated 1 record" in after.text and logged
    return ok, f"{after.message()}; audit entry with reason: {logged}"


# ---- UC-03 / UC-07 student views ---------------------------------------------------------------


@case("ST-19", "Attendance percentage", "UC-03", "SAM-F-015", "Student sees their percentage per subject",
      "ST-13: student1 marked; faculty marks one more slot absent for student1", "1. Log in as student1\n"
      "2. Open My Attendance", "-", "Percentage shown per subject, matching the marked classes")
def st19(ctx):
    b, sheet = ctx.new(), None
    b.login("faculty1")
    sheet = b.get(ctx.sheet_path)
    form = [f for f in sheet.forms() if f["method"] == "post" and "date" in f["fields"]][0]
    slots = re.findall(r'name="slots" value="(\d+)"', sheet.text)
    ctx.slot2 = slots[1]
    b.submit(sheet, form_index=sheet.forms().index(form), date=ctx.today.isoformat(), slots=ctx.slot2,
             **{ctx.absent_field: "ABSENT"})
    s = ctx.new()
    s.login("student1")
    page = s.get("/percentage/")
    m = re.search(r"UE24CS341A.*?(\d+(?:\.\d+)?)\s*%", page.text, re.S)
    pct = m.group(1) if m else None
    ok = pct is not None and float(pct) == 50.0
    return ok, f"UE24CS341A shown as {pct}% (1 present of 2 classes)" if pct else "no percentage shown"


@case("ST-20", "Threshold and alerts", "UC-03", "SAM-F-017", "Admin sets the threshold; low students are warned",
      "ST-19 done (student1 at 50% in UE24CS341A)", "1. Admin -> Attendance threshold -> 60 -> Save\n"
      "2. student1 opens the dashboard\n3. faculty1 opens the dashboard", "threshold 60",
      "Saved; student1 sees a low-attendance warning; faculty1 sees student1 in the below-threshold list")
def st20(ctx):
    a = ctx.new()
    a.login("admin")
    saved = a.submit(a.get("/notifications/threshold/"), match="threshold", threshold="60")
    s = ctx.new()
    warn = "Low attendance" in s.login("student1").text
    f = ctx.new()
    fdash = f.login("faculty1")
    listed = bool(re.search(r"Sample Student 1</a> \(\d", fdash.text))
    ok = warn and listed
    return ok, f"{saved.message() or 'saved'}; student warning: {warn}; on faculty list: {listed}"


@case("ST-21", "Attendance history", "UC-07", "SAM-F-016", "Student sees their history, newest first",
      "ST-13 and ST-19 done", "1. Log in as student1\n2. Open My History", "-",
      "Each marked class listed with date, slot, subject and status")
def st21(ctx):
    s = ctx.new()
    s.login("student1")
    page = s.get("/history/")
    rows = len(re.findall(r"UE24CS341A", page.text))
    ok = rows >= 2 and ("Absent" in page.text or "ABSENT" in page.text)
    return ok, f"{rows} entries for UE24CS341A, statuses shown"


@case("ST-22", "Ownership", "UC-07", "SAM-SEC-004", "A student can't open another student's records",
      "Logged in as student1", "1. Type the URL of another student's history and report", "/history/student/2/, "
      "/reports/student/2/", "Refused (403 or 404)")
def st22(ctx):
    s = ctx.new()
    s.login("student1")
    out = [(p, s.get(p, follow=False).status) for p in ("/history/student/2/", "/reports/student/2/")]
    ok = all(code in (403, 404) for _, code in out)
    return ok, "; ".join(f"{p} -> HTTP {c}" for p, c in out)


# ---- UC-06 reports -----------------------------------------------------------------------------


@case("ST-23", "Reports", "UC-06", "SAM-F-019", "Subject-wise report for a date range",
      "ST-13 done; logged in as faculty1", "1. Reports -> subject report for CSE-5A / UE24CS341A\n"
      "2. Enter a date range covering today", "date_from = date_to = today",
      "Every student of the class with classes held, attended and %, low ones marked")
def st23(ctx):
    b = ctx.new()
    b.login("faculty1")
    idx = b.get("/reports/")
    link = idx.links(r"/reports/subject/\d+/\d+/")[0]
    ctx.subject_report = link
    d = ctx.today.isoformat()
    page = b.get(f"{link}?date_from={d}&date_to={d}")
    students = len(set(re.findall(r"PES2UG24CS\d{3}", page.text)))
    ok = page.status == 200 and students >= 4 and "%" in page.text
    return ok, f"HTTP {page.status}; {students} students listed with percentages"


@case("ST-24", "Reports", "UC-06", "SAM-F-018, SAM-F-019", "Student-wise and class-wise reports (admin)",
      "ST-13 done; logged in as admin", "1. Reports -> search a student -> open\n2. Reports -> class CSE-5A",
      "q=PES2UG24CS091", "Both reports open with the marked data")
def st24(ctx):
    b = ctx.new()
    b.login("admin")
    found = b.get("/reports/?q=PES2UG24CS091")
    stu = found.links(r"/reports/student/\d+/")
    cls = b.get("/reports/").links(r"/reports/class/\d+/")
    sp = b.get(stu[0]) if stu else None
    cp = b.get(cls[0]) if cls else None
    ok = bool(sp and sp.status == 200 and "UE24CS341A" in sp.text and cp and cp.status == 200)
    return ok, f"student report: HTTP {sp.status if sp else '-'}; class report: HTTP {cp.status if cp else '-'}"


@case("ST-25", "Report export", "UC-06", "SAM-F-020", "Download a report as CSV",
      "ST-23 done", "1. Open the subject report\n2. Download CSV", "format=csv",
      "A CSV file with a header row and one row per student")
def st25(ctx):
    b = ctx.new()
    b.login("faculty1")
    page = b.get(f"{ctx.subject_report}?format=csv")
    lines = [ln for ln in page.raw.decode("utf-8-sig", "replace").splitlines() if ln.strip()]
    ok = page.status == 200 and "csv" in page.headers.get("content-type", "") and len(lines) >= 5
    disp = page.headers.get("content-disposition", "")
    return ok, f"{page.headers.get('content-type')}; {disp}; {len(lines)} lines; header: {lines[0][:60] if lines else ''}"


@case("ST-26", "Report export", "UC-06", "SAM-F-020", "Download a report as PDF; print view",
      "ST-23 done", "1. Open the subject report\n2. Download PDF\n3. Check the print button and print styles",
      "format=pdf", "A valid PDF file; the page has a Print button and hides navigation when printed")
def st26(ctx):
    b = ctx.new()
    b.login("faculty1")
    pdf = b.get(f"{ctx.subject_report}?format=pdf")
    page = b.get(ctx.subject_report)
    printable = "window.print()" in page.text and "@media print" in page.text
    ok = pdf.status == 200 and pdf.raw[:5] == b"%PDF-" and printable
    return ok, f"{pdf.headers.get('content-type')}, {len(pdf.raw)} bytes, starts with %PDF-: " \
               f"{pdf.raw[:5] == b'%PDF-'}; print view: {printable}"


# ---- UC-05 audit -------------------------------------------------------------------------------


@case("ST-27", "Audit log", "UC-05", "SAM-SEC-005", "Admin actions, refusals and failed logins are logged",
      "Earlier cases done (ST-02, ST-04, ST-06)", "1. Admin -> Audit Log\n2. Filter by outcome",
      "outcome = SUCCESS, DENIED, FAILED", "Entries of all three kinds, with user and time")
def st27(ctx):
    b = ctx.new()
    b.login("admin")
    counts = {}
    for outcome in ("SUCCESS", "DENIED", "FAILED"):
        page = b.get(f"/audit/?outcome={outcome}")
        counts[outcome] = page.text.count("<tr") - 1
    ok = all(n > 0 for n in counts.values())
    return ok, ", ".join(f"{k}: {v} entries" for k, v in counts.items())


# ---- non-functional ----------------------------------------------------------------------------


@case("ST-28", "Performance", "-", "SAM-NF-001", "Main pages answer within 3 seconds",
      "Data from this run", "1. Open each main page as its role, timing each request", "16 pages, 3 roles",
      "Every page under 3 s")
def st28(ctx):
    times = []
    for user, paths in (("admin", ["/dashboard/", "/students/", "/faculty/", "/subjects/", "/subjects/assignments/",
                                   "/audit/", "/reports/", "/notifications/threshold/"]),
                        ("faculty1", ["/dashboard/", "/attendance/select/", ctx.sheet_path, ctx.subject_report,
                                      f"{ctx.subject_report}?format=pdf"]),
                        ("student1", ["/dashboard/", "/percentage/", "/history/"])):
        b = ctx.new()
        b.login(user)
        for p in paths:
            page = b.get(p)
            times.append((p, page.elapsed))
    slowest = max(times, key=lambda t: t[1])
    ok = slowest[1] < 3.0
    return ok, f"{len(times)} pages; slowest {slowest[0]} at {slowest[1] * 1000:.0f} ms; " \
               f"median {statistics.median(t for _, t in times) * 1000:.0f} ms"


@case("ST-29", "Availability", "-", "SAM-NF-002", "Health check reports the server and database",
      "Server running", "1. Open /health/ without logging in", "-", "HTTP 200 'ok' (503 if the database is down)")
def st29(ctx):
    page = ctx.new().get("/health/")
    ok = page.status == 200
    return ok, f"HTTP {page.status}: {page.raw[:40].decode('utf-8', 'replace')}"


@case("ST-30", "Data protection", "-", "SAM-NF-004", "Session cookie is protected; logout ends the session",
      "Production settings (DEBUG off)", "1. Log in, read the session cookie flags\n2. Log out\n"
      "3. Open the dashboard again", "student1",
      "Cookie Secure, HttpOnly and SameSite; after logout the dashboard redirects to /login/")
def st30(ctx):
    b = ctx.new()
    page = b.get("/login/")
    page = b.submit(page, match="login", username="student1", password=PASSWORD)
    cookie = next((c for c in b.set_cookie_log if c.startswith("sessionid=")), "")
    flags = {f: f.lower() in cookie.lower() for f in ("Secure", "HttpOnly", "SameSite")}
    dash = b.get("/dashboard/")
    logout_form = [f for f in dash.forms() if "logout" in f["action"]]
    if logout_form:
        b.submit(dash, form_index=dash.forms().index(logout_form[0]))
    else:
        b.get("/logout/")
    again = b.get("/dashboard/", follow=False)
    ok = all(flags.values()) and again.status == 302 and "/login/" in again.headers.get("location", "")
    return ok, f"session cookie flags {flags}; after logout /dashboard/ -> {again.status} " \
               f"{again.headers.get('location', '').split('?')[0]}"


@case("ST-31", "Usability", "-", "SAM-NF-003", "Every page has a title, a way home and a way out",
      "Logged in as each role", "1. Open each role's main pages\n2. Check page title, home link, Logout button",
      "admin, faculty1, student1", "All present on every page")
def st31(ctx):
    missing = []
    for user, paths in (("admin", ["/students/", "/reports/", "/audit/"]),
                        ("faculty1", ["/attendance/select/", ctx.subject_report]),
                        ("student1", ["/percentage/", "/history/"])):
        b = ctx.new()
        b.login(user)
        for p in paths:
            page = b.get(p)
            if not (page.title() and 'href="/"' in page.text and 'action="/logout/"' in page.text):
                missing.append(p)
    return not missing, "all pages have title, home and logout" if not missing else f"missing on {missing}"


@case("ST-32", "Load", "-", "SAM-NF-007", "20 users at once",
      "Server with 2 gunicorn workers", "1. 20 users log in and open 5 pages each, at the same time",
      "student1-8, faculty1, admin (repeated)", "No errors; 95% of pages under 3 s")
def st32(ctx):
    users = [f"student{i}" for i in range(1, 9)] * 2 + ["faculty1", "admin", "faculty1", "admin"]
    times, errors, lock = [], [], threading.Lock()

    def one(user):
        b = ctx.new()
        page = b.login(user)
        pages = ["/dashboard/", "/dashboard/", "/dashboard/", "/dashboard/"]
        pages += ["/percentage/"] if user.startswith("student") else ["/reports/"]
        for p in pages:
            page = b.get(p)
            with lock:
                times.append(page.elapsed)
                if page.status >= 400:
                    errors.append((user, p, page.status))

    threads = [threading.Thread(target=one, args=(u,)) for u in users]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = time.perf_counter() - start
    p95 = sorted(times)[int(len(times) * 0.95) - 1]
    ok = not errors and p95 < 3.0
    return ok, f"{len(users)} users, {len(times)} page views in {total:.1f} s; errors {len(errors)}; " \
               f"median {statistics.median(times) * 1000:.0f} ms, 95th percentile {p95 * 1000:.0f} ms"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--insecure", action="store_true", help="accept a self-signed certificate")
    ap.add_argument("--out", default="system-validation-results.json")
    args = ap.parse_args(argv)
    started = dt.datetime.now().astimezone()
    results = run(args.base_url.rstrip("/"), args.insecure)
    for r in results:
        r.pop("fn", None)
    summary = {"started": started.isoformat(timespec="seconds"), "base_url": args.base_url,
               "passed": sum(r["result"] == "Pass" for r in results), "total": len(results), "cases": results}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(f"{summary['passed']} of {summary['total']} passed; results in {args.out}")
    return 0 if summary["passed"] == summary["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
