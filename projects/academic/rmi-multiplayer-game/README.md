# 🎮 RMI Multiplayer Tic-Tac-Toe

> A distributed, two-player Tic-Tac-Toe on **Java RMI**. A server publishes a session factory in an RMI registry, clients queue to join, the server **matchmakes pairs of players** into a shared session, and every move is pushed back to both clients through callbacks.

![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![RMI](https://img.shields.io/badge/Java_RMI-5382A1?style=flat-square)
![Distributed](https://img.shields.io/badge/distributed_systems-6366F1?style=flat-square)

| | |
|---|---|
| **Context** | Distributed systems and applications coursework |
| **Focus** | Remote objects, registry lookup, matchmaking, client callbacks, security policy |

---

## Architecture

```mermaid
classDiagram
    class SessionFactory {
        <<remote>>
        +joinGame(ClientCallback) Session
    }
    class Session {
        <<remote>>
        +playMove(player, x, y)
    }
    class ClientCallback {
        <<remote>>
        +updateBoard(board, isMyTurn)
        +gameOver(message)
    }
    SessionFactory ..> Session : returns once two players are matched
    Session ..> ClientCallback : pushes board updates to both players
    Client ..|> ClientCallback
    Client --> SessionFactory : lookup in registry
    Client --> Session : playMove
```

```mermaid
sequenceDiagram
    participant A as Client A
    participant B as Client B
    participant R as RMI registry
    participant S as Server
    S->>R: bind "Factory"
    A->>R: lookup "Factory"
    A->>S: joinGame(callbackA)
    Note over S: one player waiting
    B->>R: lookup "Factory"
    B->>S: joinGame(callbackB)
    Note over S: two waiting, create session
    S-->>A: updateBoard(board, isMyTurn)
    S-->>B: updateBoard(board, isMyTurn)
    A->>S: playMove(name, x, y)
    S-->>A: updateBoard(...)
    S-->>B: updateBoard(...)
    S-->>A: gameOver(message)
    S-->>B: gameOver(message)
```

## Highlights

- **Interfaces as contracts.** Every remote type is a `Remote` interface, and implementations are kept separate.
- **Factory plus registry.** Clients only need the registry address and the factory name.
- **Server-side matchmaking.** A synchronized join queue pairs players safely under concurrent connections.
- **Bidirectional communication.** Each client exports its own callback object, so the server pushes state instead of clients polling, and each side is told whether it's their turn.
- **Registry bootstrap** that creates the registry if missing or reuses a running one.
- **Security manager and policy file** configured as RMI requires.
