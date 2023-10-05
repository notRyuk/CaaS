from CaaS import app, connect
from CaaS.config import PORT
import asyncio
import uvicorn


loop = asyncio.get_event_loop()

@app.on_event("startup")
async def db_connect():
    await connect()

async def main():
    # await connect()
    uvicorn.run(
        "CaaS.__main__:app",
        host="127.0.0.1",
        port=PORT,
        reload=True
    )

if __name__ == "__main__":
    loop.run_until_complete(main())