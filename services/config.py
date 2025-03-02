from pathlib import Path

from pydantic_settings import BaseSettings


class PathSettings(BaseSettings):
    base_dir: Path = Path(__file__).parent
    submissions_dir: Path = Path("_submissions")
    logs_dir: Path = Path("_logs")


class Settings(BaseSettings):
    def setup(self):
        return self

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # File limits
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set[str] = {".zip", ".py"}

    # Sub-configurations
    paths: PathSettings = PathSettings()


settings = Settings().setup()
