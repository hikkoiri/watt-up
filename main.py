from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import PlainTextResponse
import httpx
import uvicorn


router = APIRouter(prefix='/api/v1', tags=['api_v1'])

@router.get("/energyconsumption/{upstream}", response_class=PlainTextResponse)
async def get_energy_metrics(upstream: str):
    """Retrieve scrapable energy metrics of the specified Shelly device ."""
    client_response = await get_shelly_data(upstream)
    return reformat(client_response)

async def get_shelly_data(upstream: str):
    async with httpx.AsyncClient() as client:
        try:
            external_response = await client.get(f"http://{upstream}/rpc/Switch.GetStatus?id=0")
            external_response.raise_for_status() 
            return external_response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch external data: {e}")

def reformat(json: any):
    return f"""active_power {json["apower"]}
voltage {json["voltage"]}
current {json["current"]}
temperature {json["temperature"]["tC"]}
"""

app = FastAPI(
    title="Watt-up API",
    description="A a small and convenient converter which transforms energy consumption metrics of a Shelly device to scrapable Prometheus metrics.",
    version="1.0.0"
)
app.include_router(router)


def main() -> None:
    uvicorn.run("main:app", host="0.0.0.0")


if __name__ == "__main__":
    main()