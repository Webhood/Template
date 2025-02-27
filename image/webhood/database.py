import os
import time
import json
import typing
import logging
import asyncio
import contextlib

# Import munch utility
import munch

# Import redis utilities
import redis
import redis.asyncio

# Import rednest utilities
from rednest import List, Dictionary

# Patch the dictionary copy type
# pylint: disable-next=protected-access
Dictionary._COPY_TYPE = munch.Munch

# Default channel
CHANNEL = "global"

# Fetch database URL from environment
REDIS_URL = os.environ["REDIS"]

# Default database connections
REDIS_SYNC = redis.Redis.from_url(REDIS_URL, decode_responses=True)
REDIS_ASYNC = redis.asyncio.Redis.from_url(REDIS_URL, decode_responses=True)


def relist(name: str) -> List:
    return List(REDIS_SYNC, name)


def redict(name: str) -> Dictionary:
    return Dictionary(REDIS_SYNC, name)


# Database connectivity utilities


def wait_for_redis_sync() -> None:
    # Initialize ping response
    ping_response = None

    # Loop until the redis instance can be pinged
    while not ping_response:
        # Ignore busy loading errors
        with contextlib.suppress(redis.BusyLoadingError, redis.ConnectionError):
            # Ping the instance
            ping_response = REDIS_SYNC.ping()

            # Database accepts connections
            return

        # Log the database state
        logging.info("Waiting for database to respond")

        # Sleep a second
        time.sleep(1)


async def wait_for_redis_async() -> None:
    # Initialize ping response
    ping_response = None

    # Loop until the redis instance can be pinged
    while not ping_response:
        # Ignore busy loading errors
        with contextlib.suppress(redis.BusyLoadingError, redis.ConnectionError):
            # Ping the instance
            ping_response = await REDIS_ASYNC.ping()

            # Database accepts connections
            return

        # Log the database state
        logging.info("Waiting for database to respond")

        # Sleep a second
        await asyncio.sleep(1)


# Publish / subscribe utilities


def broadcast_sync(channel: str = CHANNEL, connection: redis.Redis = REDIS_SYNC, **parameters: typing.Any) -> None:
    # Publish to channel
    connection.publish(channel, json.dumps(parameters))


async def broadcast_async(channel: str = CHANNEL, connection: redis.Redis = REDIS_ASYNC, **parameters: typing.Any) -> None:
    # Publish to channel
    await connection.publish(channel, json.dumps(parameters))


def receive_sync(channel: str = CHANNEL, connection: redis.Redis = REDIS_SYNC, count: int = 0) -> typing.Iterator[munch.Munch]:
    # Count messages
    received = 0

    # Create Pub / Sub subscriber
    with connection.pubsub() as subscriber:
        # Subscribe to channel
        subscriber.subscribe(channel)

        # Loop until count is reached
        while (received < count) or (count == 0):
            # Receive message from channel
            message = subscriber.get_message(ignore_subscribe_messages=True, timeout=1)

            # Skip sending if None
            if message is None:
                continue

            # Fetch the message data
            data = message.get("data")

            # Only parse if data is valid
            if not data:
                continue

            # Parse the message
            yield munch.Munch(json.loads(data))

            # Bump the receive count
            received += 1


async def receive_async(channel: str = CHANNEL, connection: redis.Redis = REDIS_ASYNC, count: int = 0) -> typing.AsyncIterator[munch.Munch]:
    # Count messages
    received = 0

    # Create Pub / Sub subscriber
    async with connection.pubsub() as subscriber:
        # Subscribe to channel
        await subscriber.subscribe(channel)

        # Loop until count is reached
        while (received < count) or (count == 0):
            # Receive message from channel
            message = await subscriber.get_message(ignore_subscribe_messages=True, timeout=1)

            # Skip sending if None
            if message is None:
                continue

            # Fetch the message data
            data = message.get("data")

            # Only parse if data is valid
            if not data:
                continue

            # Parse the message
            yield munch.Munch(json.loads(data))

            # Bump the receive count
            received += 1


# Add explicit exports
__all__ = ["CHANNEL", "REDIS_URL", "REDIS_ASYNC", "relist", "redict", "wait_for_redis_sync", "wait_for_redis_async", "broadcast_sync", "broadcast_async", "receive_sync", "receive_async"]
