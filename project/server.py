import io
import logging
from contextlib import asynccontextmanager

import prisma
import project.make_turn_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, StreamingResponse
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="TicTacToe Game",
    lifespan=lifespan,
    description="""Two Players TicTacToe Game communicate through an API.""",
)


@app.post("/make-turn", response_model=project.make_turn_service.GameStateResponse)
async def api_post_make_turn(
    game_id: str, row: int, col: int
) -> project.make_turn_service.GameStateResponse | Response:
    """
    Processes a player's move in the Tic-Tac-Toe game and returns the current state of the game.
    """
    try:
        res = project.make_turn_service.make_turn(game_id, row, col)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
