from typing import Tuple

import uvicorn
from fastapi import FastAPI
from gamba.client.client import Client

app = FastAPI()
master = Client()


@app.get("/healthz")
def healthz():
    return master.is_alive()


@app.get("/readyz")
def readyz():
    return master.is_alive()


@app.post("/example")
async def dummy(request):
    data = prepare_data(request)
    results = await master.execute("queue1", data)
    return results


def prepare_data(request) -> Tuple[dict, str]:
    # IMPLEMENT ME
    return {}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
