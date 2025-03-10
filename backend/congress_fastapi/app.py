import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from congress_fastapi.routes.members import router as members_router
from congress_fastapi.routes.legislation import router as legislation_router
from congress_fastapi.routes.legislation_version import (
    router as legislation_version_router,
)
from congress_fastapi.routes.search import router as search_router
from congress_fastapi.routes.user import router as user_router
from congress_fastapi.routes.stats import router as stats_router
from congress_fastapi.routes.uscode import router as uscode_router
from congress_fastapi.utils.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


origins = [
    "http://localhost:3000",
    "https://congress.dev",
]
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins (or ["*"] for all origins)
    allow_credentials=True,  # Allow cookies to be sent with requests
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    try:
        # Process the request
        return await call_next(request)
    except Exception as e:
        # Log the exception to the console
        print(f"Exception occurred: {e}")
        traceback.print_exc()

        # Re-raise the exception to let FastAPI handle it
        raise e


app.include_router(members_router)
app.include_router(legislation_router)
app.include_router(legislation_version_router)
app.include_router(search_router)
app.include_router(user_router)
app.include_router(stats_router)
app.include_router(uscode_router)
print("Loaded")
