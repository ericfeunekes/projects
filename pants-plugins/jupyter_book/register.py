from typing import Iterable

from jupyter_book import goals
from jupyter_book.target_types import JBTarget
from pants.engine.target import Target


def target_types() -> Iterable[type[Target]]:
    return [JBTarget]


def rules():
    return [*goals.rules()]
