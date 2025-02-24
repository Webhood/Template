# mypy: disable-error-code=valid-type
# pylint: disable=no-member, unused-wildcard-import

import time
import logging

# Import utilities
from runtypes import *
from guardify import *

# Import webhood utilities
from webhood.router import WebSocket, router
from webhood.database import wait_for_redis_sync, broadcast_async, receive_async, redict
from webhood.constants import LOG_LEVEL, LOG_FORMAT, LOG_DATEFORMAT

# Setup logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATEFORMAT)

# Global database
DATABASE = redict("click")


def startup() -> None:
    # Wait for redis to ping back before operating on database
    wait_for_redis_sync()

    # Initialize click value
    DATABASE.setdefaults(count=0)


def shutdown() -> None:
    # Clear the database
    DATABASE.clear()


def worker() -> None:
    # Loop until the database is empty
    while DATABASE:
        # Log the amount of clicks
        logging.info("There were %d clicks so far", DATABASE.count)

        # Wait for 10 seconds
        time.sleep(10)


@router.get("/api/clicks")
async def fetch_clicks() -> int:
    # Return the count from the database
    return DATABASE.count


@router.post("/api/clicks")
async def click_request() -> str:
    # Increment ping count
    DATABASE.count += 1

    # Log the user click
    logging.info("User clicked - count is now %d", DATABASE.count)

    # Return the ping count
    return f"Click count is {DATABASE.count}"


@router.post("/api/relay")
async def relay_request(message: str, sender: Optional[Email] = None) -> None:
    # Append to message
    if sender:
        message += f" ({sender})"

    # Publish to channel
    await broadcast_async(text=message)


@router.socket("/socket/relay")
async def relay_socket(websocket: WebSocket) -> None:
    # Accept the websocket
    await websocket.accept()

    # Subscribe to the global relay
    async for event in receive_async():
        # Send the message
        await websocket.send_text(event.text)
