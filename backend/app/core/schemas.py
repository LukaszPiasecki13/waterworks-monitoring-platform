"""Base schemas and pagination utilities."""

from typing import TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(str_strip_whitespace=False)
