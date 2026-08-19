from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base for every request/response model: snake_case in Python, camelCase on the wire."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ErrorResponse(CamelModel):
    """The single error shape every failing endpoint returns."""

    message: str
