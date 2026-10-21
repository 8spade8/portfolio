# 🛍️ Merch Reservation Shop

> A zero-payment merchandise shop for a student organisation. Members browse and reserve with no account; admins manage stock and reservations in a separate portal. Runs entirely on free tiers.

![React](https://img.shields.io/badge/React_18-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite_5-646CFF?style=flat-square&logo=vite&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL_RLS-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)

| | |
|---|---|
| **Role** | Sole developer: UI, database design, security model, deployment |
| **Cost to run** | Free tiers only |
| **Source** | 🔒 Private (organisation branding and the reservation rules) |

---

## Product

| Public shop | Admin portal |
|---|---|
| Catalogue by category with a single spotlight item, product carousel and **live stock** | Email and password login, restricted to users on an allow-list table |
| Reservation form with validation for variants and quantities. **No payment is taken.** | Item management: create, edit, stock, visibility, spotlight |
| Items update live via realtime subscriptions | Reservation management: filter and move through `pending → collected / cancelled` |

## Architecture

```mermaid
flowchart TB
    subgraph Browser
        PUB["Public shop<br/>entry page 1"]
        ADM["Admin portal<br/>entry page 2<br/>lazy-loaded panels"]
    end

    subgraph Supabase
        AUTH["Auth"]
        RT["Realtime"]
        subgraph DB["PostgreSQL"]
            IT[("items")]
            RS[("reservations")]
            AU[("admin_users")]
            RPC["Reservation function<br/>SECURITY DEFINER"]
        end
    end

    PUB -- "read active items" --> IT
    PUB -- "reserve" --> RPC
    RPC -- "atomic stock check + decrement" --> IT
    RPC -- "insert" --> RS
    IT -. changes .-> RT -. live stock .-> PUB
    ADM --> AUTH
    ADM -- "RLS: admins only" --> IT
    ADM -- "RLS: admins only" --> RS
    AU -. "who is an admin" .-> DB
```

## Design decisions

- **Two entry points, not one app.** Public and admin are separate Vite pages, so visitors never download admin code. Admin panels are lazy-loaded and vendor libraries are split into long-lived cache chunks.
- **Stock can't be oversold.** Reservations go through a database function that performs the check and decrement as **one atomic conditional update**, then inserts the reservation. Two people cannot claim the last unit. There is **no public insert policy** on reservations, so that function is the only way in.
- **Security lives in the database.** Row-Level Security lets the public read active items only. Writes, and all reads of reservations, are admin-only. The anonymous key shipped to the browser carries no privileges beyond what those policies allow.
- **Backward-compatible RPC versions.** The client tries the newest reservation function and falls back to older versions, so a front-end deploy can't break an older database.
- **Idempotent, guarded SQL.** The setup script is safe to re-run, migrates old data (category normalisation, variant backfill) and aborts if anything needs manual review.
- **One spotlight, enforced by the database.** A partial unique index plus a trigger guarantee at most one spotlight item, so the UI can never drift from the data.
- **Hosting-portable.** Config for Vercel (rewrites, caching, security headers) and for Apache.

## What I'd highlight in an interview

1. **Authorization as data**: RLS policies plus a `SECURITY DEFINER` function instead of a custom API server.
2. Concurrency correctness without locks in app code.
3. Shipping a real product on a zero budget.
