# Pydantic Data Models

from pydantic import BaseModel

# Class used for validation of menu items
class MenuList(BaseModel):
    id: int
    name: str
    category: str
    type: str
    source: str
    available: bool


# Class Used for Response Validation
class MenuResponse(BaseModel):
    # status: int = 200
    # None in status 👀
    status: int | None = 200
    count: int
    items: list[MenuList]