# File for Exceptions

# Define Classes for Custom Errors

from fastapi.responses import JSONResponse
from fastapi import Request


class PinNotFoundError(Exception):
    def __init__(self, pincode: str):
        self.pincode = pincode

class InvalidPinError(Exception):
    def __init__(self, pincode: str, reason: str = "Invalid Format"):
        self.pincode = pincode
        self.reason = reason


#  Custom Handler

async def pin_not_found_handler(request: Request, exc: PinNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "pin_not_found",
            "message": f"No location for pin {exc.pincode}",
            "pin": exc.pincode,
        },
    )

async def invalid_pin_handler(request: Request, exc: InvalidPinError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_pin",
            "message": f"Pincode '{exc.pincode}' is invalid, because {exc.reason}",
            "pin": exc.pincode
        }
    )