# 🎓 Student Management API

> A small, cleanly layered **Spring Boot REST service** for registering and listing students, with OpenAPI documentation and a service-layer test.

![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![Swagger](https://img.shields.io/badge/OpenAPI-85EA2D?style=flat-square&logo=swagger&logoColor=black)
![Maven](https://img.shields.io/badge/Maven-C71A36?style=flat-square&logo=apachemaven&logoColor=white)

| | |
|---|---|
| **Context** | Enterprise Java / Spring coursework |
| **Focus** | Layered architecture, dependency injection, API documentation, testing |

---

## Architecture

```mermaid
flowchart LR
    CL(("HTTP client")) --> CT["Controller<br/>REST endpoints · OpenAPI annotations"]
    CT --> SV["Service interface<br/>+ implementation"]
    SV --> RP["Repository<br/>Spring Data"]
    RP --> DB[("MySQL")]
    EN["Entity"] -.- RP
```

| Layer | Responsibility |
|---|---|
| **Controller** | Exposes `register` and `list` endpoints, documented with OpenAPI annotations and CORS enabled |
| **Service** | A business interface and an implementation, so the controller depends on an abstraction |
| **Repository** | Spring Data JPA repository over MySQL |
| **Entity** | The student model |
| **Tests** | A service-implementation test |

## Highlights

- **Constructor injection** through Lombok, with no field injection.
- **Interface-driven services** keep layers swappable and testable.
- **Self-documenting API** via springdoc OpenAPI / Swagger UI.
