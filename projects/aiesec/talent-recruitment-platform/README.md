# 🎯 Talent Recruitment Platform

> A single authenticated flow that replaces scattered forms, chat threads and spreadsheets in a student organisation's recruitment: candidates sign up, apply, book an interview and receive a decision, while recruiters run the whole pipeline from one dashboard.

![Next.js](https://img.shields.io/badge/Next.js_App_Router-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Google APIs](https://img.shields.io/badge/Google_APIs-4285F4?style=flat-square&logo=google&logoColor=white)

| | |
|---|---|
| **Role** | Developer |
| **Backend** | No custom server: the front end talks to Supabase directly, secured by Row-Level Security |
| **Hosting** | Free tiers (Vercel + Supabase) |
| **Source** | 🔒 Private (candidate data model and selection process) |

---

## The product

| Candidate side | Recruiter side |
|---|---|
| Sign-up, email confirmation, password reset, profile completion with avatar upload | Dashboard with candidate list, search, filters and export |
| Application form with file upload | **Kanban pipeline** across recruitment stages |
| Self-service **interview booking** through a tokenised link | Recruitment **waves**, interview slots and a live interview-day board |
| A dashboard that changes with the candidate's stage | Attendance flags and internal notes |
| Decision delivered by email | **Decisions** queue with admin-triggered emails |

## Architecture

```mermaid
flowchart LR
    C(("Candidate")) --> APP
    R(("Recruiter")) --> APP
    subgraph APP["Next.js App Router on Vercel"]
        PAGES["Server and client pages"]
        API["Route handlers<br/>email · interview sheets"]
        MW["Auth callbacks<br/>role-gated admin routes"]
    end
    PAGES -- "supabase-js + RLS" --> SB
    MW --> SB
    API --> SB
    subgraph SB["Supabase"]
        AUTH["Auth"]
        PG[("Postgres<br/>RLS, triggers")]
        ST["Storage<br/>file uploads"]
    end
    API -- "SMTP" --> MAIL["Decision and booking emails"]
    API -- "Google Sheets API" --> GS["Interview sheets"]
```

### Candidate lifecycle

```mermaid
stateDiagram-v2
    [*] --> not_applied
    not_applied --> interview_ready : candidate submits application
    interview_ready --> interview_booked : booking (recruiter-controlled)
    interview_booked --> accepted : decision
    interview_booked --> rejected : decision
    accepted --> [*]
    rejected --> [*]
```

## Engineering highlights

- **Authorization in the database.** Row-Level Security and triggers enforce who can change what. A candidate may move *only* from "not applied" to "interview ready" on their own row (enforced by a narrowly scoped trigger exception); every other stage change is recruiter-only.
- **No custom API layer.** The browser uses `supabase-js` directly, so there's no extra server to secure or host. Route handlers exist only for side effects that need server secrets (email, Google APIs).
- **Admin-triggered communication.** Decision emails are an explicit action from a queue, not an automatic side effect, preventing accidental mass mailing.
- **Operational glue.** An interview can open a Google Sheet and sync its results back; interview-day boards auto-refresh for the people running the day.
- **Role-gated route groups** keep admin-only areas (waves, slots, decisions) separate from general recruiter pages.

## What I'd highlight in an interview

1. A **state machine enforced at the data layer**, not just in UI code.
2. Replacing five tools with one flow while staying on a zero-cost stack.
