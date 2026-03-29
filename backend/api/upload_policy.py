"""HTTP-adjacent upload rules. Presentation layer only."""

from typing import AbstractSet, Final, FrozenSet

from fastapi import UploadFile

ALLOWED_CONTENT_TYPES: Final[FrozenSet[str]] = frozenset(
    {
        "text/csv",
        "text/plain",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    }
)

ALLOWED_EXTENSIONS: Final[AbstractSet[str]] = frozenset({".csv", ".xlsx", ".xls"})

UPLOAD_REJECT_DETAIL: Final[str] = (
    "Unsupported file type. Use CSV or Excel (.csv, .xlsx, .xls)."
)


def is_allowed_tabular_upload(file: UploadFile) -> bool:
    raw_ct = (file.content_type or "").split(";")[0].strip().lower()
    if raw_ct in ALLOWED_CONTENT_TYPES:
        return True
    name = (file.filename or "").lower()
    return any(name.endswith(ext) for ext in ALLOWED_EXTENSIONS)
