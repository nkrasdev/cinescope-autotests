from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    """Base model for API payloads with Python and wire-format aliases enabled."""

    model_config = ConfigDict(populate_by_name=True)
