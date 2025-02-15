import traceback

from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Query,
    status,
    Response,
    Request,
    Cookie,
    Depends,
)

from congress_fastapi.models.stats import (
    NivoCalendarResponse,
    NivoFunnelResponse,
)

from congress_fastapi.handlers.stats import (
    handle_get_legislation_calendar,
    handle_get_legislation_funnel,
)


router = APIRouter(tags=["Stats"])

@router.get("/stats/legislation_calendar")
async def legislation_calendar(request: Request) -> NivoCalendarResponse:
    try:
        data = await handle_get_legislation_calendar()
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    if data is not None:
        return NivoCalendarResponse(**data)

@router.get("/stats/legislation_funnel")
async def legislation_funnel(request: Request) -> NivoFunnelResponse:
    try:
        data = await handle_get_legislation_funnel()
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    if data is not None:
        return NivoFunnelResponse(**data)