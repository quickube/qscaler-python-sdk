from typing import Optional

from pydantic import BaseModel


class NameSpacedName(BaseModel):
    name: str
    namespace: str

