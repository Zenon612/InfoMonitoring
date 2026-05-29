from __future__ import annotations

from pydantic import BaseModel


class MonitorRunResponseSchema(BaseModel):
    release_id: str
    markdown_path: str
    geo_code: str
    raw_inforeasons_saved: int

