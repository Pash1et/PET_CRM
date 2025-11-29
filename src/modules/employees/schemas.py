import uuid

from pydantic import BaseModel, EmailStr


class BaseEmployee(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class CreateEmployee(BaseEmployee):
    password: str


class UpdateEmployee(BaseEmployee):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class ReadEmployee(BaseEmployee):
    id: uuid.UUID


class LoginEmployee(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
