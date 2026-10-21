# Data Models (Pydantic) Validaton

from pydantic import BaseModel, field_validator
# field validator Vs seriliser?

# For fetching pincode
class PinRequest(BaseModel):
    pincode: str

    # Validating pincode format (6 digits in India)
    @field_validator("pincode")
    # `@classmmethod`->Alternative Constructor (factory method)
    @classmethod
    def pin_check(cls, value):
        # Length check for pincode
        if len(value) != 6 or not value.isdigit():
            raise ValueError ("Pincode is not 6 digit in length -> Invalid")
        return value

# Response Format validation
class PinResponse(BaseModel):
    pincode: str
    city: str
    state: str
    district: str

# Response Models for bulk fetching



    # Think: What all needs to be validated when involving Bulk Request
class BulkRequest(BaseModel):
    pincodes: list[str]

    @field_validator("pincodes")
    @classmethod
    def validate_pincodes(cls, values):
        if len(values) == 0:
            raise ValueError("At least one pincode is required")
        if len(values) > 20:
            raise ValueError("Maximum 20 pincodes allowed per request")

        for code in values:
            if len(code) != 6 or not code.isdigit():
                raise ValueError("Each Pincode must be exactly 6 digit")
        return values

# Red?
# class BulkRequest(BaseModel):
    # pincodes: list[str]
    # @field_validator("pincodes")
    # @classmethod
    # def mass_request(cls, vlaues):
    #     if len() == 0:
    #         raise ValueError("Pin must contain atleast 1 digit ☢️")
    #     if len(values) > 10:
    #         return ValueError("Can return max 10 Values per Request")

    #     for pin in values:
    #         if len(pin) != 6 or not values.isdigit():
    #             raise ValueError("PinCode Invalid!")
    #     return values

# POST based
class BulkResponse(BaseModel):
    # Think what needed in Response!
    status: int = 200 #Defaults to 200 OK
    # found: bool
    found: int
    not_found: int
    results: list[PinResponse]
    missing: list[str]