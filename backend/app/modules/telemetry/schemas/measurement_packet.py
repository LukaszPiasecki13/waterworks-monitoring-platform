"""Telemetry packet request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field, model_validator

from app.core.schemas import BaseSchema
from app.modules.core_data.schemas.point_types import ErrorCode


class MeasurementPoint(BaseSchema):
    point_id: str = Field(min_length=1, max_length=128)
    type: str = Field(min_length=1, max_length=64)
    unit: str = Field(min_length=1, max_length=32)
    quality: str = Field(min_length=1, max_length=32)

    avg: float | None = None
    min: float | None = None
    max: float | None = None
    value: float | int | bool | None = None

    @model_validator(mode="after")
    def validate_measurement_shape(self) -> MeasurementPoint:
        has_aggregate = (
            self.avg is not None or self.min is not None or self.max is not None
        )
        has_value = self.value is not None

        if not has_aggregate and not has_value:
            raise ValueError(
                "Point must contain either value or at least one aggregate: avg/min/max"
            )

        return self


class MeasurementWindow(BaseSchema):
    window_start: datetime
    window_seconds: int = Field(gt=0, le=3600)
    points: list[MeasurementPoint] = Field(min_length=0)


class ErrorEntry(BaseSchema):
    code: ErrorCode
    point_id: str | None = Field(None, min_length=1, max_length=128)
    severity: Literal["info", "warning", "critical"]
    message: str | None = Field(None, max_length=512)


class MeasurementPacketRequest(BaseSchema):
    model_config = ConfigDict(extra="forbid")

    v: int = Field(ge=2, le=2)
    device_id: str = Field(min_length=1, max_length=128)
    seq: int = Field(ge=0)
    sent_at: datetime
    windows: list[MeasurementWindow] = Field(min_length=1)
    errors: list[ErrorEntry] = Field(default_factory=list)


class TelemetryIngestResponse(BaseSchema):
    status: Literal["accepted", "duplicate"]
    device_id: str
    seq: int
