# README

A 20 minute talk demonstrating `FastAPI` and `Pydantic`.

A modern API should be:

- Self-documenting -- `Swagger`/`SwaggerUI`
- Contract-based -- `Pydantic`
- Fast -- async/caching
- Observability/Instrumentation Metrics -- `OpenTelemetry`/`Prometheus`/`Grafana`
- Deployable: ENV vars, container lifecycles

In this little intro, we'll look at the first three points.

## Contents

<!--toc:start-->

- [README](#readme)
  - [Contents](#contents)
  - [Basics](#basics)
  - [Data](#data)
    - [Polars / Plotly / Jupyter](#polars-plotly-jupyter)
  - [FastAPI](#fastapi)
    - [Dependency Injection](#dependency-injection)
    - [Contracts / Pydantic](#contracts-pydantic)
    - [Swagger / Swagger-UI](#swagger-swagger-ui)
    - [AI app](#ai-app)
    - [Async / Locust](#async-locust)

<!--toc:end-->

## Basics

```bash
uv venv .venv
source .venv/bin/activate
uv pip install fastapi[all]
```

## Data

Source: <https://github.com/joelkoen/postcodes-au/tree/main>

```bash
v localities-au.csv  # <-- My editor is always mapped to `v`.
```

### Polars / Plotly / Jupyter

Quick sanity check on the data...

```bash
uv pip install polars plotly jupyter
uv run --with jupyter jupyter lab
```

Note: If you look at the VIC population, you'll see this is old data.

## FastAPI

```bash
v main.py  # <-- look at @app.get('/postcodes')
uvicorn main:app --reload
```

- <http://127.0.0.1:8000/>

See responses in @app.get('/')

- <http://127.0.0.1:8000/postcodes?skip=5800&limit=100>
- <http://127.0.0.1:8000/postcodes/0823/localities>

### Dependency Injection

(Retrieve the right ID or first postcode; see other examples in main.py)

### Contracts / Pydantic

(Compare GET /postcodes with response_model=PostcodesModelList)

(Show types and models in Refspy)

### Swagger / Swagger-UI

- <http://127.0.0.1:8000/docs>
- <http://127.0.0.1:8000/openapi.json>

- How to verify input?

(Compare POST /postcodes/0823/edit with PostcodesModel)

### AI app

```bash
cd ../map-app/
```

(generated from the openapi.json in about 2 mins)

- <http://127.0.0.1:8081/> # <-- Must be 127.0.0.1 not localhost

### Async / Locust

```bash
uv add locust
v locustfile.py
locust --tag=data
locust --tag=sync
locust --tag=async
```

- <http://127.0.0.1:8089> # <-- Locust
