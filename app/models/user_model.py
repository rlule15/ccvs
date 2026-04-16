# TODO Implement user models with Pydantic
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)


class UserCreate(UserBase):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8)


class UserResponse(UserBase):
    # Allows pydantic to read data using dot notation
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    team: str
