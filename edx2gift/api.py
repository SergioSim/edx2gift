"""Edx2Gift API root."""

import os
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from edx2gift.cli import convert_edx_2_gift

app = FastAPI()
security = HTTPBasic()


def get_auth_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
) -> str:
    """Checks auth parameters validity."""
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = os.environ.get("EDX2GIFT_USERNAME").encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = os.environ.get("EDX2GIFT_PASSWORD").encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.post("/convert", response_class=PlainTextResponse)
async def convert(
    _: Annotated[str, Depends(get_auth_username)],
    content: Annotated[str, Form()],
) -> str:
    """Converts edX XML quiz string to Moodle GIFT format."""
    return "".join(convert_edx_2_gift(content))


app.mount("/", StaticFiles(directory="edx2gift/static", html=True), name="static")
