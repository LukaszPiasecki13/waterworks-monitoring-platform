"""Base schemas and pagination utilities."""

from typing import TypeVar

from pydantic import BaseModel, ConfigDict, field_serializer

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(str_strip_whitespace=False)

    @field_serializer("*", mode="plain", when_used="json")
    def serialize_floats(self, value: object) -> object:
        """Round all float values to 2 decimal places for JSON."""
        if isinstance(value, float) and not isinstance(value, bool):
            return round(value, 2)
        return value
