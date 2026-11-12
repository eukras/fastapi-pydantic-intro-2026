import asyncio
import time
from enum import Enum
from typing import Annotated

from airium import Airium
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from data import yield_csv_rows

# ---------------------------------------------------------------------------
# Talk outline:
#
# - Data + Jupyter overview
# - Simple FastAPI application: Homepage and /postcodes
# - Swagger-UI: /docs and models
# - Pydantic: Contracts for data in and out
# - Dependency Injection
# - Asynchronous functions
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

AUSTRALIAN_POSTCODES = list(yield_csv_rows("data/localities-au.csv"))


def lookup_postcode_id(id: int) -> dict | None:
    model = next(filter(lambda _: _["id"] == id, AUSTRALIAN_POSTCODES), None)
    if not model:
        raise HTTPException(404, f"Postcode ID {id} not found")
    return model


# ---------------------------------------------------------------------------
# Some simple HTML
# ---------------------------------------------------------------------------


app = FastAPI()

# Add CORS for Swagger-UI and Locust
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8081",  # Maps app
        "http://127.0.0.1:8089",  # Locust
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def get_index():

    # Examples:
    #
    # return "Hello World!"
    # return {"total": 5487}
    # return JSONResponse(status_code=418, content={"message": "I'm a teapot!"})
    # return RedirectResponse(url="https://melbpy.org", status_code=307)
    # return FileResponse(__file__)

    # HTML
    __ = Airium()
    with __.html():
        with __.head():
            __.title(_t="FastAPI Demo")
            __.link(
                rel="stylesheet",
                type="text/css",
                href="static/style.css",
            )
        with __.body(), __.div(klass="rounded-box"):
            __.h1(_t="FastAPI Demo")
            __.p(_t=f"{len(AUSTRALIAN_POSTCODES):,} localities")
            with __.p(), __.a(href="/docs"):
                __.button(_t="Docs")

    return HTMLResponse(content=str(__))


# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------


class StateEnum(str, Enum):
    act = "ACT"
    nsw = "NSW"
    nt = "NT"
    qld = "QLD"
    sa = "SA"
    tas = "TAS"
    vic = "VIC"
    wa = "WA"


class PostcodeModel(BaseModel):
    id: int = Field(ge=1)
    locality: str
    state: StateEnum
    postcode: int = Field(ge=1, le=9999)
    count: int
    long: float = Field(ge=0, le=360)
    lat: float = Field(ge=-90, le=90)
    # Form behaviour:
    model_config = {"extra": "forbid"}


class PostcodesContract(BaseModel):
    postcodes: list[PostcodeModel]


# @app.get("/postcodes", response_model=PostcodesContract)
@app.get("/postcodes")
def get_postcodes(skip: int = 0, limit: int = 100):
    """Get postcodes with pagination"""
    return {"postcodes": AUSTRALIAN_POSTCODES[skip : skip + limit]}


@app.get("/postcodes/{postcode}/localities", response_model=PostcodesContract)
def get_postcode_localities(postcode: str):
    """Get all localities for a postcode"""
    return {"postcodes": [_ for _ in AUSTRALIAN_POSTCODES if _["postcode"] == postcode]}


@app.patch("/postcodes/id/{id}", response_model=PostcodeModel)
def patch_postcode(id: int, postcode: PostcodeModel):
    """Update a postcode by ID, if it exists"""
    global AUSTRALIAN_POSTCODES
    AUSTRALIAN_POSTCODES = [
        postcode if item.get("id") == id else item for item in AUSTRALIAN_POSTCODES
    ]
    return postcode


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------


# How does it know to supply the Request object?


@app.get("/demo/request")
def demo_request(request: Request):
    """Return the user agent from the request object"""
    return JSONResponse(content={"User-Agent": request.headers["user-agent"]})


@app.get("/demo/headers")
def demo_headers(
    user_agent: Annotated[str | None, Header()] = None,
):
    """Return the user agent by dependency injection"""
    return JSONResponse(
        content={
            "User-Agent": user_agent,
        }
    )


class Paging:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


@app.get("/demo/paging")
def demo_paging(paging: Annotated[Paging, Depends(Paging)]):
    return {"skip": paging.skip, "limit": paging.limit}


# ---------------------------------------------------------------------------
# Applying dependency injection
# ---------------------------------------------------------------------------


@app.get("/postcodes/id/{id}")
def get_postcode_by_id(
    id: int,
    model: Annotated[PostcodeModel, Depends(lookup_postcode_id, use_cache=True)],
) -> PostcodeModel:
    """Return locality by id"""
    return model


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------


@app.get("/postcodes/slow/sync", response_model=PostcodesContract)
def get_postcodes_slow(skip: int = 0, limit: int = 100) -> dict:
    """Return localities list by postcode, but slowly"""
    time.sleep(1)
    return {"postcodes": AUSTRALIAN_POSTCODES[skip : skip + limit]}


@app.get("/postcodes/slow/async", response_model=PostcodesContract)
async def get_postcodes_async_slow(skip: int = 0, limit: int = 100) -> dict:
    """Return localities list by postcode, but slowly -- but also asynchronously"""
    await asyncio.sleep(1)
    return {"postcodes": AUSTRALIAN_POSTCODES[skip : skip + limit]}
