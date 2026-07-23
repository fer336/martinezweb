from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/trabajos"

    admin_username: str = "admin"
    admin_password_hash: str = ""

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    cors_origins: list[str] = ["http://localhost:5173"]

    # MinIO / cualquier storage S3-compatible
    s3_endpoint_url: str = ""
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_public_base_url: str = ""

    github_token: str = ""
    github_repo: str = "fer336/martinezweb"
    github_workflow_file: str = "deploy.yml"
    github_ref: str = "main"


settings = Settings()
