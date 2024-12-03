from app.core.constants.app import (
    DEFAULT_APP_ENV,
    DEFAULT_APP_NAME,
    DEFAULT_APP_VERSION,
)
from typing import Any, Dict, Optional, Union, List
from pydantic import PostgresDsn, validator, AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = DEFAULT_APP_NAME
    app_env: str = DEFAULT_APP_ENV
    app_desc: str = ""

    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str
    database_uri: Optional[PostgresDsn] = None

    celery_broker_url: str
    celery_result_backend: str

    jwt_secret: str
    jwt_algorithm: str

    mailgun_key: str
    mailgun_url: str
    mailgun_domain: str
    mailgun_from: str

    risetai_url: str
    risetai_token: str

    app_version: str = DEFAULT_APP_VERSION

    allowed_origins: list[AnyUrl] = []

    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                return [i.strip() for i in v[1:-1].split(",")]
            else:
                return [v]
        elif isinstance(v, list):
            return [i.strip() for i in v]
        raise ValueError(v)

    @validator("database_uri", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_server"),
            port=int(values.get("postgres_port")),
            path=f"{values.get('postgres_db') or ''}",
        )

    class Config:
        case_sensitive = False
        env_file = ".env"


settings = Settings()
