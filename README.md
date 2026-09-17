# Student Attendance Management System (SAMS)

![Status](https://img.shields.io/badge/status-requirements%20%26%20test%20planning%20complete-yellow)
![Course](https://img.shields.io/badge/course-UE24CS341A-blue)
![Team](https://img.shields.io/badge/team-Team%203-lightgrey)

A web-based **Student Attendance Management System (SAMS)**, built as a Software Engineering mini-project for **UE24CS341A** at PES University. Replaces manual attendance registers with a centralized digital platform for recording, tracking, and reporting attendance.

---

## Table of Contents
- [Overview](#overview)
- [Objectives](#objectives)
- [Features](#features)
- [User Roles](#user-roles)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Testing Strategy](#testing-strategy)
- [Security](#security)
- [Non-Functional Requirements](#non-functional-requirements)
- [Repository Structure](#repository-structure)
- [Project Status](#project-status)
- [Open Design Questions](#open-design-questions)
- [Team](#team)
- [License](#license)

---

## Overview
Role-based platform for three actors:
- **Students** – view attendance %, history, low-attendance alerts
- **Faculty** – mark/modify attendance, generate reports
- **Admins** – manage users, subjects, classes, thresholds, reports

Built via a phased SE process: requirements → test planning → design → implementation → validation.

---

## Objectives
Digitize attendance tracking, eliminate manual errors, enforce role-based access, prevent duplicate records, auto-calculate percentages, and maintain secure, auditable records with low-attendance alerts.

---

## Features

**Authentication** — Role-based login (Admin/Faculty/Student); unauthorized access blocked.

**Student Management** — Add/update/search student records; students view their own history.

**Faculty & Subjects** — Manage faculty, create/assign subjects, show assignments on faculty dashboard.

**Attendance** — Select class/subject, mark Present/Absent, store with ID/subject/date/status, block duplicates, allow authorized edits.

**Monitoring** — Calculate percentages, view history, flag low attendance against a configurable threshold.

**Reports** — Student-, subject-, and class-wise; downloadable and printable.

---

## User Roles

| Role | Responsibilities |
|---|---|
| **Student** | View attendance %, history, alerts |
| **Faculty** | Mark/modify attendance, generate reports |
| **Admin** | Manage users, subjects, classes, access, thresholds, reports |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JS, Bootstrap |
| Backend | Python 3, Django |
| Database | MySQL 8.0 |
| VCS | Git & GitHub |
| Testing | Django TestCase / pytest-django |
| CI | GitHub Actions *(planned)* |

---

## Architecture

```text
Users (Student/Faculty/Admin)
        │
Web Browser (HTML/CSS/JS/Bootstrap)
        │
Django Backend (Auth · Business Logic · Attendance · Reports)
        │
MySQL 8.0 (Students · Faculty · Subjects · Attendance)
```

---

## Documentation

| Document | Contents | 
|---|---|
| **SRS v1.0** | 20 functional, 7 non-functional, 5 security requirements + use cases + RTM | 
| **Test Plan v1.0** | Strategy, environment, schedule, traceability | 

Covers 7 use cases: Mark Attendance, Select Class/Subject, View Attendance %, Manage User Access, Log Admin Action, Generate Reports, View History.

---

## Testing Strategy

- **Unit** — percentage calc, student/auth logic
- **Integration** — Student → Attendance → Calculation → Report
- **System (E2E)** — Login → Select Class/Subject → Mark → Save → Calculate → Generate

Plus functional, security, regression, and limited performance testing.

---

## Security
Auth-gated access, role-based control, hashed passwords, student data isolation, protection against unauthorized edits, audit logging.

---

## Non-Functional Requirements

| Attribute | Requirement |
|---|---|
| Performance | Response within target time |
| Reliability | Backup/recovery, availability |
| Usability | Simple, user-friendly UI |
| Security | Protect attendance/user data |
| Maintainability | Extensible without major rework |
| Scalability | Multiple concurrent users |

---

## Repository Structure

```text
SAMS/
├── README.md
├── SRS/Team3_SRS.pdf
├── Test-Plan/SAMS_Test_Plan_Team3.pdf
├── src/            # Django project
├── tests/
├── docs/diagrams, docs/reports
└── requirements.txt
```

---

## Project Status

**Stage: Requirements & Test Planning Complete → Design/Implementation Next**

✅ SRS · Test Plan · RTM · Use cases · Requirements (functional/non-functional/security) · Test strategy

⬜ System/DB design · Django setup · Frontend/backend build · Auth · Attendance module · Reports · Security implementation · Unit/Integration/System testing · Final validation

---

## Open Design Questions
Multiple sessions of same subject/day · student deactivation vs. deletion · failed admin actions in audit log · report-generation performance measurement · default attendance history ordering.

---

## Team

**Team 3 — PES University**

| Name | SRN |
|---|---|
| Anmol Vyas | PES2UG24CS072 |
| Anupam Rajesh Tiwari | PES2UG24CS073 |
| Anupriya | PES2UG24CS074 |
| Anusha G | PES2UG24CS075 |

---

## License
Academic coursework project (UE24CS341A, PES University) — no license assigned yet.
