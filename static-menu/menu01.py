"""Main File for static-menu"""


"""Read only menu API to fetch latest menu without DB calls"""

# from pydoc import doc -> WHAT
#  Query, HTTPException ?


from fastapi import FastAPI, Query, HTTPException
from fastapi import Request
import uvicorn
from data_file import menu_items
from data_models import MenuList, MenuResponse


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


@app.get("/menu", response_model=MenuResponse) # Depencency Injections
# It means response_model will validate the reponse using memeber data of MenuResponse
# Vlaidate Response with MenuResponse before JSON serialisation


# ❗️
# Menu with path param-Query
def get_menu(
    category: str | None = Query(
        default=None,
        description="Filter by Indian, Continental, Chinese"
    )
):
    if category:
        separation = [
            item for item in menu_items
            if item["category"] == category
        ]
        if not separation:
            raise HTTPException(status_code=404, detail=f"No items in Category:{category}")
        return MenuResponse(count=len(separation), items = separation)

    return MenuResponse(count=len(menu_items), items=menu_items)

# Item id in path will fetch it
@app.get("/menu/{item_id}", response_model=MenuList)
def get_item(item_id: int):
    for item in menu_items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Menu item with id {item_id} not found")



if __name__ == "__main__":
    uvicorn.run("menu01:app",host="127.0.0.1", port= 8080, reload= True)
