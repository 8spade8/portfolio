# 🗄️ IT Jobs Data Warehouse

> A multi-source **star-schema data warehouse** for analysing the IT job market: heterogeneous salary and job-opportunity datasets from different countries are cleaned, conformed and loaded through SSIS ETL packages into dimension and fact tables ready for BI.

![SSIS](https://img.shields.io/badge/SSIS-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)
![ETL](https://img.shields.io/badge/ETL-star_schema-6366F1?style=flat-square)
![Visual Studio](https://img.shields.io/badge/Visual_Studio-5C2D91?style=flat-square&logo=visualstudio&logoColor=white)

| | |
|---|---|
| **Context** | Data warehousing coursework |
| **Role** | Designed the schema and built the ETL packages |

---

## Model

```mermaid
erDiagram
    FACT_JOBS }o--|| DIM_DATE : "when"
    FACT_JOBS }o--|| DIM_COUNTRY : "where"
    FACT_JOBS }o--|| DIM_POSTE : "role"
    FACT_JOBS }o--|| DIM_DEVISE : "currency"
    FACT_JOBS }o--|| DIM_COMPETENCES : "skill"
    FACT_JOBS {
        decimal salary
        string job_title
        string region
    }
```

## ETL flow

```mermaid
flowchart LR
    S1["Job opportunities CSV"] --> STG
    S2["Salary data: Tunisia CSV"] --> STG
    S3["Salary data: USA CSV"] --> STG
    S4["Mobile-market data: India CSV"] --> STG
    S5["Tunisia 2023-24 CSV"] --> STG
    STG["Connection managers<br/>flat-file sources"] --> CL["Cleaning and conforming<br/>types · currencies · titles · countries"]
    CL --> D1["Dimension packages<br/>date · country · role · currency · skills"]
    D1 --> FT["Fact package<br/>lookups to surrogate keys"]
    FT --> DW[("Warehouse")]
    DW --> BI["Analysis and BI"]
```

## Highlights

- **One package per dimension plus a fact package**, sequenced by a control-flow package with SQL tasks and precedence constraints, so each step can be run and debugged alone.
- **Conformed dimensions** let salary data in different currencies and different countries be compared in the same model.
- **Reproducible**: connection managers and project parameters isolate environment details.
- **Cleaning at the boundary**: five unlike sources are normalised before they ever reach a dimension.

## Skills shown

Dimensional modelling · SSIS control flow and data flow · lookup-based fact loading · data conforming across sources.
