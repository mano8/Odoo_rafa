"""Pydantic models for the JSON receipt printing endpoint."""
from typing import Optional

from pydantic import BaseModel


class ReceiptLine(BaseModel):
    """One printable unit extracted from the rendered receipt DOM.

    Types:
      ``text`` — a single line of text (v, c, b, s).
      ``row``  — two-column row with left (l) and right (r) text (b, s).
      ``div``  — full-width divider rule using character dv (default "-").
    """

    t: str  # "text" | "row" | "div"
    v: Optional[str] = None  # text content  (text)
    l: Optional[str] = None  # left column   (row)
    r: Optional[str] = None  # right column  (row)
    c: Optional[str] = None  # "center" | "right"  (text; default "left")
    b: bool = False  # bold
    s: int = 1  # relative size multiplier (1=normal, 2=double)
    dv: Optional[str] = None  # divider character  (div; default "-")


class PrintReceiptJsonRequest(BaseModel):
    """Payload sent by pos_json_printer after scanning the rendered receipt DOM."""

    lines: list[ReceiptLine]
    char_size: int = 1  # global ESC/POS size (1=normal, 2=large)
    cut: bool = True
    open_cashdrawer: bool = False
