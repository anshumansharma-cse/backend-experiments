# FastAPI code for seller-pin

from fastapi import FastAPI
import uvicorn
from data import pin_data

from exceptions import (
    PinNotFoundError,
    pin_not_found_handler,
    InvalidPinError,
    invalid_pin_handler
)

from models import PinRequest,PinResponse,BulkRequest,BulkResponse


app = FastAPI(
    title="Seller Pincode Dashboard",
    version="0.0.2",
    description=(
        "This will fetch the pincodes form a loical data file & flag custom errors"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Register Custom Excpetion Handler->
# errors?
app.add_exception_handler(PinNotFoundError, pin_not_found_handler)
app.add_exception_handler(InvalidPinError, invalid_pin_handler)


@app.get("/")
def root():
    """Pin Lookup API"""
    return{"Purouse": "Finding API"}

@app.get("/pincode/{pin}", response_model=PinResponse)
# Dont Forget responsemodel
def fetch_pin(pin: str):
    """Pin Path Param"""
    if len(pin) != 6 or not pin.isdigit(): #Valid Pincode check
        raise InvalidPinError(pin, "is invalid")

    if pin not in pin_data:
        raise PinNotFoundError(pin)
    return pin_data[pin]

# Post -> parsing data in JSON Body
# Browser- navigating directly to a URL normally triggers GET, not POST (Use HTTP webrequest (API) client)

@app.post("/bulk", response_model=BulkResponse)
def bulk_pin(request: BulkRequest):
    """Allows User to Query Multiple Pincodes at Once"""
    results = []
    missing = []

    for pin in request.pincodes:
        if pin in  pin_data:
            results.append(pin_data[pin])
        else:
            missing.append(pin)

    return BulkResponse(
        found=len(results),
        not_found=len(missing),
        results=results,
        missing=missing
    )

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1", port = 8080, reload=True)


