"""Main File for static-menu"""


"""Read only menu API to fetch latest menu without DB calls"""

# from pydoc import doc -> WHAT
#  Query, HTTPException ?

from fastapi import FastAPI, Query, HTTPException
import uvicorn
from data_file import menu_items
from data_models import MenuList, MenuResponse
# from fastapi import Request


app = FastAPI(
    title="Read-Only-Menu",
    description=(
        "Read Only Menu"
    ),
    version="0.0.2",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/")
def read_root():
    """Root"""
    return{
        "Purpose": "Building Read Only Menu",
        "Instructions": "yet to update"
    }


# Depencency Injections, response_model=MoenuResponse->
# @app.get("/menu", response_model=MenuResponse)
# It means response_model will validate the reponse using memeber data of MenuResponse
# Vlaidate Response with MenuResponse before JSON serialisation


# ❗️
# Menu with path param-Query
@app.get("/menu", response_model=MenuResponse)
def get_menu(
    # Add All Query (param) filters required
    category: str | None = Query(default=None),
    name: str | None = Query(default=None, min_length=1), #min_length=1 accounts for /menu?name= returning 422
    item_type: str | None = Query(default=None, alias="type"), #alias here means external url will refer to 'type'
    source: str | None = Query(default=None),
    available: bool | None = Query(default=None),
    id: int | None = Query(default=None)
):
    results = menu_items

    if category:
        results = [
            item for item in results
            if item["category"].lower() == category.lower()
        ]

    if name:
        results = [
            item for item in results
            if item["name"].lower() == name.lower()
        ]

    if item_type is not None:
        results = [
            item for item in results
            if item["type"].lower() == item_type.lower()
        ]

    if source:
        results = [
            item for item in results
            if item["source"].lower() == source.lower()
        ]

    if available is not None:
        results = [
            item for item in results
            if item["available"] == available
        ]

    if id:
        results = [
            item for item in results
            if item["id"] == id
        ]

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No matching menu items found"
        )

    return MenuResponse(
        count=len(results),
        items=results

    )
# Item id in path will fetch it
@app.get("/menu/{item_id}", response_model=MenuList)
def item_id(item_id: int):
    for item in menu_items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Menu item with id {item_id} not found")

# Search by name
@app.get("/menu/name/{item_name}", response_model=MenuList)
def item_name(item_name: str):
    for item in menu_items:
        if item["name"].lower() == item_name.lower():
            return item
    raise HTTPException(
        status_code=404,
        detail=f"Menu item with name {item_name} not found"
    )


# Search by type
@app.get("/menu/type/{item_type}", response_model=list[MenuList])
def item_type(item_type: str):
    results = [
        item for item in menu_items
        if item["type"].lower() == item_type.lower()
    ]
    if not results:
        raise HTTPException(status_code=404, detail=f"No items of {item_type} found")
    return results


# Search by source
@app.get("/menu/source/{item_src}", response_model=list[MenuList])
def item_src(item_src: str):
    results = [
        item for item in menu_items
        if item["source"].lower() == item_src.lower()
    ]
    if not results:
        raise HTTPException(status_code=404, detail=f"No items from {item_src} source found")
    return results


# Search by availability
@app.get("/menu/availability/{item_available}", response_model=list[MenuList])
def item_available(item_available: bool):
    results = [
        item for item in menu_items
        if item["available"] == item_available
    ]
    if not results:
        raise HTTPException(status_code=404, detail="No items found for this availability")
    return results



if __name__ == "__main__":
    uvicorn.run("menu01:app",host="127.0.0.1", port= 8080, reload= True)


