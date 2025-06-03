
from os import getenv
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    List,
    Literal,
    Optional,
    Tuple
)

from pydantic import (
    Field,
    HttpUrl,
    SecretStr,
    ValidationError,
    model_validator,
    computed_field,
    field_validator
)
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from hw_proxy.tools.paths import find_dotenv
from hw_proxy.schemas.shared import ValidationConstants
# pylint: disable=invalid-name, import-outside-toplevel


# --------------------------------------
# Pluggable Secret Providers
# --------------------------------------
class SecretProvider:
    """Abstract base for retrieving secrets from various backends."""

    def get(self, key: str) -> Optional[str]:
        """Retrieve the secret value for `key`, or None if not found."""
        raise NotImplementedError


class EnvProvider(SecretProvider):
    """Fetch secrets from OS environment variables."""

    def get(self, key: str) -> Optional[str]:
        return getenv(key)


def settings_customise_sources(
    init_settings,
    env_settings,
    file_secret_settings
) -> Tuple[Any, ...]:
    """
    Source priority:
    1. Init kwargs
    2. .env file
    3. Environment variables
    """
    sources = [init_settings, file_secret_settings, env_settings]
    return tuple(sources)


def parse_cors(value: str) -> List[str]:
    """
    Convert a comma-separated string into a list of CORS origins,
    ensuring that each origin is valid (using a simplified host pattern).

    Each origin is stripped of extra whitespace and trailing slashes.
    """
    # Note: Here, you may reuse the HTTP_HOST_REGEX from ValidationConstants.
    host_pattern = ValidationConstants.HTTP_HOST_REGEX
    origins = []
    for origin in value.split(","):
        origin = origin.strip().rstrip("/")
        if not origin:
            continue
        if not host_pattern.match(origin):
            raise ValueError(
                f"Invalid host in BACKEND_CORS_ORIGINS: '{origin}'"
            )
        origins.append(origin)
    if not origins:
        raise ValueError(
            "BACKEND_CORS_ORIGINS must contain at least one valid origin"
        )
    return origins


# --------------------------------------
# Settings Model
# --------------------------------------
REQUIRE_UPDATE_FIELDS = [
    "SECRET_KEY"
]
REQUIRED_FIELDS = [
    "DOMAIN", "API_PREFIX", "PROJECT_NAME", "STACK_NAME",
    "STATIC_BASE_PATH", "TEMPLATES_BASE_PATH",
    "PRINTER_KEY"
]


class Settings(BaseSettings):
    """Settings for the auth_user_service: adds only new fields."""
    # Directory where .env is located; subclasses override if needed
    ENV_FILE_DIR: ClassVar[Path] = Path(__file__).resolve().parent

    # fields lists for validation
    required_fields: ClassVar[List[str]] = [
        "DOMAIN", "ENVIRONMENT", "API_PREFIX", "PROJECT_NAME", "STACK_NAME",
        "STATIC_BASE_PATH", "TEMPLATES_BASE_PATH"
    ]
    secret_fields: ClassVar[List[str]] = [
        "SECRET_KEY"
    ]
    passwords: ClassVar[List[str]] = []
    secret_keys: ClassVar[List[str]] = [
        "SECRET_KEY"
    ]

    # Pydantic v2 config must be a plain class attribute (no annotation)
    model_config = SettingsConfigDict(
        env_file=find_dotenv(ENV_FILE_DIR),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="forbid",
        settings_customise_sources=settings_customise_sources,
    )

    # -------------------
    # Core Settings
    # -------------------
    # Basic settings
    DOMAIN: str = Field(..., pattern=ValidationConstants.HOST_REGEX.pattern)
    ENVIRONMENT: Literal["local", "development", "staging", "production"]
    API_PREFIX: str = Field(
        ...,
        pattern=ValidationConstants.URL_PATH_STR_REGEX.pattern
    )
    SET_OPEN_API: bool = True
    SET_DOCS: bool = True
    SET_REDOC: bool = True
    PROJECT_NAME: str = Field(
        ...,
        pattern=ValidationConstants.KEY_REGEX.pattern
    )
    STACK_NAME: str = Field(
        ...,
        pattern=ValidationConstants.SLUG_REGEX.pattern
    )
    STATIC_BASE_PATH: str = Field(
        ...,
        pattern=ValidationConstants.FILE_PATH_REGEX.pattern
    )
    TEMPLATES_BASE_PATH: str = Field(
        ...,
        pattern=ValidationConstants.FILE_PATH_REGEX.pattern
    )

    # -------------------
    # Security / Tokens
    # -------------------
    # Security keys & tokens
    SECRET_KEY: SecretStr

    BACKEND_HOST: HttpUrl
    FRONTEND_HOST: HttpUrl
    SENTRY_DSN: HttpUrl | None = None
    PRINTER_KEY: str = Field(
        ...,
        pattern=ValidationConstants.KEY_REGEX.pattern
    )

    LOG_LEVEL: str = "Warning"
    # BACKEND_CORS_ORIGINS should be provided
    # as a comma-separated string in the env file.
    BACKEND_CORS_ORIGINS: str

    @classmethod
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def validate_cors_origins(cls, v: str) -> List[str]:
        """
        Validate the BACKEND_CORS_ORIGINS environment variable.
        If it's a string, parse it into a list of valid origins.
        """
        if not isinstance(v, str):
            raise ValidationError(
                "BACKEND_CORS_ORIGINS must be a comma-separated string."
            )
        return isinstance(parse_cors(v), list)

    @computed_field
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """
        Combine validated BACKEND_CORS_ORIGINS (as a list)
        with FRONTEND_HOST (host only, without scheme).
        FRONTEND_HOST is stripped of its scheme and trailing slash.
        """
        frontend = self.FRONTEND_HOST
        origins = parse_cors(self.BACKEND_CORS_ORIGINS)
        if frontend not in origins:
            origins.append(frontend)
        return origins

    @model_validator(mode="after")
    def validate_sensitive_fields(self) -> "Settings":
        """
        Post-initialization validation for sensitive and required fields.
        """
        for name in self.secret_fields:
            secret = getattr(self, name)
            is_secret = isinstance(secret, SecretStr)
            if name in self.passwords\
                    and is_secret:
                raw = secret.get_secret_value().strip()
                if not ValidationConstants.PASSWORD_REGEX.match(raw):
                    raise ValueError(
                        f"{name} must be a strong password: "
                        "8+ chars, upper, lower, digit, special char."
                    )
            if name in self.secret_keys\
                    and is_secret:
                raw = secret.get_secret_value().strip()
                if not ValidationConstants.SECRET_KEY_REGEX.match(raw):
                    raise ValueError(
                        f"{name} must be a valid secret key."
                    )
        return self

    @classmethod
    @model_validator(mode="after")
    def enforce_secure_and_required_values(cls, values: dict) -> dict:
        """
        Ensure all required string fields are non-empty after stripping.
        """
        insecure_default = "changethis"
        # List of fields that must be non-empty.
        for field_item in cls.required_fields:
            val = values.get(field_item)
            if not val or (isinstance(val, str) and not val.strip()):
                raise ValidationError(
                    f"The environment variable '{field_item}' "
                    "must be provided and not be empty."
                )
        # Enforce that secret values are changed.
        for field_item in cls.secret_fields:
            val = values[field_item]
            if hasattr(val, "get_secret_value"):
                raw_val = val.get_secret_value()
            else:
                raw_val = val
            if isinstance(raw_val, str)\
                    and raw_val.strip().lower() == insecure_default:
                raise ValidationError(
                    "Insecure value for '{field_item}' "
                    f"(found '{insecure_default}'). "
                    f"Please set a strong, unique value for {field_item}."
                )
        return values


try:
    settings = Settings()
except Exception as e:
    # Raise with a clear error message if validation fails.
    raise RuntimeError(
        f"Configuration validation error:\n {str(e)}") from e

if __name__ == "__main__":
    # For debugging, print out public settings without exposing secrets.
    public_settings = settings.model_dump()
    for field in settings.secret_fields:
        public_settings.pop(field, None)
    print(public_settings)
