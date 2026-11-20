# AI Ticket Assignment Agent

A Python backend project that uses an AI agent and a ticket-management API to process unassigned support tickets stored in a MySQL database.

The project consists of **two services**:

1. **Ticket API:** Provides endpoints to retrieve and update tickets in MySQL.
2. **AI Agent:** Uses **Ollama** as its large language model (LLM) to review daily unassigned tickets and assign them to **Steve** through the Ticket API.

Each service has its own Dockerfile. **Docker Compose** runs the two containers on a shared network so they can communicate by service name.

## How it works

1. A daily run of the AI agent starts. The scheduling mechanism is configured separately.
2. The AI agent requests unassigned tickets from the Ticket API.
3. The Ticket API reads ticket data from MySQL and returns the matching tickets.
4. The AI agent uses Ollama as part of its ticket-processing workflow and requests assignment of the unassigned tickets to **Steve**.
5. The Ticket API updates the tickets in MySQL.
6. The AI agent returns a summary showing:
   - The number of tickets found unassigned.
   - The number of tickets successfully updated.

**Note:** The update count should include only confirmed successful updates. Tickets that fail to update should not be counted as updated.

## Architecture

```text
              Daily trigger / manual run
                         |
                         v
                 +----------------+
                 | AI Agent       |
                 | Python + Ollama|
                 +----------------+
                    |          |
          HTTP API  |          | LLM request
                    v          v
             +-------------+  +----------------+
             | Ticket API  |  | Ollama         |
             | Python      |  | LLM service    |
             +-------------+  +----------------+
                    |
                    | Database connection
                    v
               +---------+
               | MySQL   |
               | Tickets |
               +---------+

       Ticket API and AI Agent run as two Docker
       containers on the same Compose network.
```

Ollama and MySQL must be available to the containers. They can run on the Docker host, on another reachable server, or as separately configured services. **The provided two-container setup does not automatically create MySQL or Ollama containers.**

## Technology stack

- **Python** for both backend services.
- **REST API** for retrieving and updating ticket information.
- **MySQL** for ticket storage.
- **Ollama** for LLM inference in the AI agent.
- **Docker** for building separate images.
- **Docker Compose** for running the two containers and connecting them through a shared network.

## Project structure

The repository contains two Python applications, two Dockerfiles, and a Compose configuration. A possible layout is shown below; adjust the names to match the actual repository.

```text
.
├── ticket-api/                  # Python API and MySQL access
│   ├── ...
│   └── Dockerfile              # Ticket API image
├── ai-agent/                    # Python agent and Ollama integration
│   ├── ...
│   └── Dockerfile              # AI Agent image
├── docker-compose.yml          # Two containers and shared network
└── README.md
```

## Prerequisites

- Docker Engine or Docker Desktop with Docker Compose support.
- A running MySQL instance containing the ticket data.
- A running Ollama instance with the model required by the AI agent downloaded and available.
- Network access from the containers to MySQL and Ollama.

## Configuration

Configure the applications with the settings their code expects. Typical configuration includes:

| Setting | Purpose |
| --- | --- |
| MySQL host, port, database, username, and password | Allow the Ticket API to access the ticket database. |
| Ticket API base URL | Allow the AI agent to call the Ticket API. |
| Ollama base URL | Allow the AI agent to reach the Ollama server. |
| Ollama model name | Select the installed model used by the AI agent. |
| Assigned employee | Target employee for unassigned tickets: **Steve**. |

**Important:** These are configuration *categories*, not verified environment-variable names. Use the exact names defined in the Python source code and Compose file. Keep database credentials in environment variables or a local secrets file, and do not commit them to Git.

### Container networking

Within a Docker Compose network, containers connect using the **Compose service name**, not `localhost`.

For example, **if** the API service is named `ticket-api` and listens on port `4046` inside its container, its URL from the AI agent could be:

```text
http://ticket-api:4046
```

The service name and port above are examples; use the actual values in `docker-compose.yml`.

**Ollama on the Docker host:** A container usually cannot reach the host's Ollama server using `localhost`. Configure a reachable host address (for example, `host.docker.internal` where supported), make sure Ollama listens on an appropriate interface, and secure access to that interface. The same networking consideration applies to a host-installed MySQL instance.

## Build and run with Docker Compose

From the repository directory containing `docker-compose.yml`, run:

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f
```

Stop the two containers:

```bash
docker compose down
```

These commands assume the Compose file defines both application services and their shared network.

## Daily ticket assignment

The intended daily workflow is:

```text
Start daily processing
        |
        v
Fetch unassigned tickets from Ticket API
        |
        v
Count unassigned tickets
        |
        v
Process tickets using AI Agent + Ollama
        |
        v
Request assignment to Steve via Ticket API
        |
        v
Count successful ticket updates
        |
        v
Return processing summary
```

### Example result

The following is an **illustrative** response format, not a guaranteed current API schema:

```json
{
  "unassigned_tickets": 12,
  "updated_tickets": 12,
  "assigned_to": "Steve"
}
```

If some updates fail, `updated_tickets` should reflect only successful assignments.

## Scheduling

The workflow is intended to run daily, but **Docker Compose alone does not schedule daily execution**. To automate it, configure a scheduler such as cron, a task scheduler, or a scheduled application job to invoke the agent's supported entry point. The precise command or endpoint depends on the AI agent implementation.

## Operational considerations

- Make ticket assignments **idempotent** where possible so repeated runs do not reassign tickets unnecessarily.
- Verify each update succeeded before incrementing the `updated_tickets` count.
- Log API failures, model errors, and database connectivity problems.
- Restrict database access and protect API endpoints appropriately.
- Avoid placing database passwords or other secrets in source code or committed Compose files.
- Ensure `Steve` matches the employee identifier expected by the ticket system (for example, a user ID if the database stores IDs rather than names).

## Project scope

This repository covers the two Python application containers and their integration. MySQL setup, Ollama hosting, deployment-specific configuration, and daily scheduling depend on the environment and are not assumed to be included in the two-container Compose configuration.
