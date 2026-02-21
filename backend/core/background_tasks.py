"""
Background Tasks — Entry points called from FastAPI lifespan.

Starts the signal pipeline as an asyncio background task.
"""

import asyncio
import logging

logger = logging.getLogger("background_tasks")


def start_signal_pipeline():
    """
    Create the background signal pipeline task.
    Call this from the FastAPI lifespan after DB init.
    """
    from core.signal_pipeline import run_signal_pipeline

    task = asyncio.create_task(run_signal_pipeline())
    logger.info("📡 Background signal pipeline task created")
    return task
