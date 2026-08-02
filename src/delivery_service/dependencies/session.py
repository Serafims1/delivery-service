from typing import Annotated
from uuid import uuid4

from fastapi import Depends, Request


def get_session(request: Request) -> str:
    session_id = request.session.get("session_id")

    if session_id is None:
        session_id = str(uuid4())
        request.session["session_id"] = session_id

    return session_id


SessionDep = Annotated[str, Depends(get_session)]
