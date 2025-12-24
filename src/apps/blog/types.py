from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class BlogPostMeta(BaseModel):
    post_id: str
    title: str
    author: str
    created_at: datetime
    status: Literal["draft", "published"]
