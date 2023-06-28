import pydantic
from typing import Optional, Type


class CreateAdvertisement(pydantic.BaseModel):
    title: str
    description: str
    owner: str

class PatchAdvertisement(pydantic.BaseModel):
    title: Optional[str]
    description: Optional[str]
    owner: Optional[str]

VALIDATION_CLASS = Type[CreateAdvertisement] | Type[PatchAdvertisement]
