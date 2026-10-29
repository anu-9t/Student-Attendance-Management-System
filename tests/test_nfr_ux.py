"""TC-UX-01 (SAM-NF-003): the interface is simple to use for every role.

Owner: Anupam. Automated checks for what makes the pages usable without training:
- every page has its own title and works on a phone-sized screen (viewport tag);
- every form field has a visible label (or an aria-label for the Present/Absent radios);
- each role's main tasks are one click from their dashboard;
- there's always a way home (the SAMS link) and a way to log out;
- error messages say what went wrong in plain words.
"""
from html.parser import HTMLParser

import pytest
from django.core.management import call_command

from accounts.models import User
from subjects.models import SubjectAssignment

pytestmark = pytest.mark.django_db


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.title, self._in_title = "", False
        self.links, self.labels_for, self.fields, self.meta = set(), set(), [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "a" and a.get("href"):
            self.links.add(a["href"])
        elif tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        elif tag == "meta":
            self.meta.append(a)
        elif tag in ("input", "select", "textarea") and a.get("type") not in ("hidden", "submit", "button"):
            self.fields.append(a)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data

    def unlabelled_fields(self):
        return [f for f in self.fields if f.get("id") not in self.labels_for and not f.get("aria-label")
                and not f.get("placeholder")]


def get(client, username, url):
    client.force_login(User.objects.get(username=username))
    response = client.get(url)
    assert response.status_code == 200, url
    return Page(response.content.decode())


def pages_for(username):
    a = SubjectAssignment.objects.filter(faculty__user__username="faculty1").first()
    return {
        "admin": ["/dashboard/admin/", "/students/", "/students/add/", "/faculty/", "/subjects/", "/reports/",
                  "/audit/", "/notifications/threshold/"],
        "faculty1": ["/dashboard/faculty/", "/attendance/select/", f"/attendance/mark/{a.class_group_id}/{a.subject_id}/",
                     f"/attendance/modify/{a.class_group_id}/{a.subject_id}/", "/reports/"],
        "student1": ["/dashboard/student/", "/percentage/", "/history/"],
    }[username]


@pytest.fixture
def seeded():
    call_command("seed_data", verbosity=0)


@pytest.mark.parametrize("username", ["admin", "faculty1", "student1"])
def test_tc_ux_01a_every_page_has_a_title_and_fits_a_phone(client, seeded, username):
    titles = set()
    for url in pages_for(username):
        page = get(client, username, url)
        assert page.title.strip().endswith("| SAMS"), url
        assert any(m.get("name") == "viewport" for m in page.meta), url
        titles.add(page.title.strip())
    assert len(titles) == len(pages_for(username)), "two pages share a title"


@pytest.mark.parametrize("username", ["admin", "faculty1", "student1"])
def test_tc_ux_01b_every_form_field_is_labelled(client, seeded, username):
    for url in pages_for(username):
        missing = get(client, username, url).unlabelled_fields()
        assert not missing, f"{url}: {missing}"


@pytest.mark.parametrize(
    "username,dashboard,tasks",
    [
        ("admin", "/dashboard/admin/", ["/students/", "/faculty/", "/reports/", "/audit/"]),
        ("faculty1", "/dashboard/faculty/", ["/attendance/select/", "/reports/"]),
        ("student1", "/dashboard/student/", ["/percentage/", "/history/"]),
    ],
)
def test_tc_ux_01c_main_tasks_are_one_click_from_the_dashboard(client, seeded, username, dashboard, tasks):
    links = get(client, username, dashboard).links
    for task in tasks:
        assert task in links, f"{task} isn't linked from {dashboard}"


@pytest.mark.parametrize("username", ["admin", "faculty1", "student1"])
def test_tc_ux_01d_always_a_way_home_and_out(client, seeded, username):
    client.force_login(User.objects.get(username=username))
    for url in pages_for(username):
        response = client.get(url)
        assert b'href="/"' in response.content, url
        assert b'action="/logout/"' in response.content, url


def test_tc_ux_01e_error_messages_are_plain(client, seeded):
    response = client.post("/login/", {"username": "student1", "password": "wrong"})
    assert b"Wrong username or password" in response.content
    client.force_login(User.objects.get(username="student1"))
    assert b"You don't have access to this page" in client.get("/students/").content
