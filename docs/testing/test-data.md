# Test data (STP Section 6)

Every test run starts from the same data, so results can be compared between machines and
between runs. Owner: Anusha G (Test Engineer).

## 1. Sample data: `python manage.py seed_data`

| What | Values |
|---|---|
| Logins (password `Sams@12345`) | `admin`; `faculty1`, `faculty2`; `student1` ... `student8` |
| Classes | CSE-5A, CSE-5B (4 students each) |
| Subjects | UE24CS341A Software Engineering, UE24CS342A Computer Networks, UE24CS343A DBMS |
| Who teaches what | faculty1: UE24CS341A to CSE-5A and CSE-5B; faculty2: UE24CS342A to CSE-5A, UE24CS343A to CSE-5B |
| Time slots | Period 1 to Period 6 (one hour each) |
| Threshold | 75% |

`student1` to `student4` are PES2UG24CS091 to PES2UG24CS094 in CSE-5A.

## 2. Term data for the use-case tests: `tests/testdata.py`

Ten teaching days (1 to 14 Oct 2026) of UE24CS341A (Period 1, marked by faculty1) and
UE24CS342A (Period 3, marked by faculty2) for CSE-5A:

| SRN | UE24CS341A | UE24CS342A | Why |
|---|---|---|---|
| PES2UG24CS091 | 10/10 = 100.0% | 10/10 = 100.0% | never absent |
| PES2UG24CS092 | 5/10 = 50.0% | 8/10 = 80.0% | low in one subject only |
| PES2UG24CS093 | 7/10 = 70.0% | 7/10 = 70.0% | just under 75% in both |
| PES2UG24CS094 | 8/10 = 80.0% | 6/10 = 60.0% | above in one, below in the other |

## 3. Load data for the non-functional tests: `python manage.py seed_load`

6 classes (LOAD-1 to LOAD-6) of 60 students and 60 teaching days for all three subjects:
about 65,000 attendance rows, the same on every machine (fixed random seed, roughly 80% present).
`python manage.py seed_load --clear` removes it again.
