import uuid

from pydantic import BaseModel, EmailStr


class BaseEmployee(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class CreateEmployee(BaseEmployee):
    password: str


class UpdateEmployee(BaseEmployee):
    pass


class ReadEmployee(BaseEmployee):
    id: uuid.UUID
