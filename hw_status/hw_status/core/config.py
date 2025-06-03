
from os import getenv
import secrets
from urllib.parse import quote_plus
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
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
    model_validator
)
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from hw_status.tools.paths import find_dotenv
from hw_status.schemas.shared import ValidationConstants
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


class VaultProvider(SecretProvider):
    """Fetch secrets from HashiCorp Vault (production/staging only)."""

    def __init__(self, addr: str, token: str):
        try:
            import hvac
        except ImportError as e:
            raise RuntimeError(
                "hvac library is required for Vault integration"
            ) from e

        self._client = hvac.Client(url=addr, token=token)

    def get(self, key: str) -> Optional[str]:
        """Retrieve a secret at path `secret/data/app` and key `key`.
        TODO: adjust path/policy as needed for your Vault setup.
        """
        result = self._client.secrets.kv.v2.read_secret_version(
            path="app"
        )
        return result.get("data", {}).get("data", {}).get(key)


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
    4. Vault (prod/staging)
    """
    sources = [init_settings, file_secret_settings, env_settings]
    env = getenv("ENVIRONMENT", "").lower()
    secret_provider = getenv("SECRET_PROVIDER", "").lower()
    if env in {"production", "staging"} \
            and secret_provider == "vault":
        # Use Vault for production/staging environments
        vault_addr = getenv("VAULT_ADDR")
        vault_token = getenv("VAULT_TOKEN")
        token_file = "/run/secrets/vault_token"
        if not vault_token and Path(token_file).is_file():
            vault_token = vault_token = Path(
                token_file
            ).read_text(encoding="utf-8").strip()
        if vault_addr and vault_token:
            provider = VaultProvider(vault_addr, vault_token)

            def _vault_source(settings: BaseSettings) -> Dict[str, Any]:
                # Determine secrets to fetch based on current settings
                secrets_to_fetch = REQUIRE_UPDATE_FIELDS.copy()
                fetched: Dict[str, Any] = {}
                for key in secrets_to_fetch:
                    val = provider.get(key)
                    if val is not None:
                        fetched[key] = val
                return fetched

            sources.append(_vault_source)
    return tuple(sources)


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
    API_PREFIX: str = Field(..., pattern=ValidationConstants.URL_PATH_STR_REGEX.pattern)
    SET_OPEN_API: bool = True
    SET_DOCS: bool = True
    SET_REDOC: bool = True
    PROJECT_NAME: str = Field(..., pattern=ValidationConstants.KEY_REGEX.pattern)
    STACK_NAME: str = Field(..., pattern=ValidationConstants.SLUG_REGEX.pattern)
    STATIC_BASE_PATH: str = Field(..., pattern=ValidationConstants.FILE_PATH_REGEX.pattern)
    TEMPLATES_BASE_PATH: str = Field(..., pattern=ValidationConstants.FILE_PATH_REGEX.pattern)

    
    # -------------------
    # Security / Tokens
    # -------------------
    # Security keys & tokens
    SECRET_KEY: SecretStr

    BACKEND_HOST: HttpUrl
    SENTRY_DSN: HttpUrl | None = None
    PRINTER_KEY: str = Field(..., pattern=ValidationConstants.KEY_REGEX.pattern)

    LOG_LEVEL: str = "Warning"

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
            if isinstance(raw_val, str) and raw_val.strip().lower() == insecure_default:
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