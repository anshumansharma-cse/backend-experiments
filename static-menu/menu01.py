"""Main File for static-menu"""


"""Read only menu API to fetch latest menu without DB calls"""

# from pydoc import doc -> WHAT

from fastapi import FastAPI
from fastapi import Request
import uvicorn

app = FastAPI(
    title="Read-Only-Menu",
    description=(
        "Fetch Menu"
    ),
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/")
def read_root():
    """Root"""
    return{
        "Purpose": "Building Read Only Menu",
        "Instructions": "go to /menu for menu "
    }

@app.get("/menu")
def get_menu():
    """Menu"""
    return{
        "Category1": "Indian",
        "Category2": "Continental",
        "Category3": "Asian"
    }

# Tags:

# Indian Food
@app.get("/menu/cat1/Indian/food", tags=["India"])
def India_food():
    """Indian Food"""
    return{
        "Veg": ["Paneer", "Poha", "Aaloo"],
        "Non-Veg": ["Chicken", "Fish"]
    }

# Indian Drinks
@app.get("/menu/cat1/Indian/drinks", tags=["India"])
def India_drinks():
    return{
        "Drinks": ["Chai", "tea", "Doodh"]
    }


# Continental Food
@app.get("/menu/cat2/Continental/food", tags=["Continental"])
def Cont_food():
    return{
        "Veg": ["Bread", "Soyabean", "Apple"],
        "Non-Veg": ["Chicken", "Fish"]
    }

# Continental Drinks
@app.get("/menu/cat2/Continental/drinks", tags=["Continental"])
def Cont_drinks():
    return{
        "Drinks": ["ice-tea", "lemon-tea"]
    }


# Asian Food
@app.get("/menu/cat3/Asian/food", tags=["Asia"])
def Asia_food():
    return{
        "Veg": ["Chilly-Gravy", "Chilly-noodles"],
        "Non-Veg": ["Chilli-Chicken", "Fish"]
    }

# Asian Drinks
@app.get("/menu/cat3/Asian/drinks", tags=["India"])
def Asia_drinks():
    return{
        "Non-Veg": ["Beer", "Mojito"]
    }

if __name__ == "__main__":
    uvicorn.run("menu01:app",host="127.0.0.1", port= 8080, reload= True)
