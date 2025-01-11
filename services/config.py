from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class DatabaseSettings(BaseSettings):
    url: str = "sqlite:///grader.db"
    echo: bool = False  # SQL query logging

class DockerSettings(BaseSettings):
    timeout: int = 300  # 5 minutes
    memory_limit: str = "512m"
    cpu_quota: int = 50000  # 50% of one CPU
    cpu_period: int = 100000

class PathSettings(BaseSettings):
    base_dir: Path = Field(default=Path(__file__).parent.parent)
    submissions_dir: Path = Field(default=None)
    courses_dir: Path = Field(default=None)
    logs_dir: Path = Field(default=None)

    @field_validator("submissions_dir", "courses_dir", "logs_dir", mode="before")
    @classmethod
    def set_default_dirs(cls, v: Optional[Path], info) -> Path:
        if v is None:
            base = cls.model_fields["base_dir"].default
            field_name = info.field_name
            return base / field_name.replace("_dir", "s")
        return Path(v)

    def ensure_dirs(self):
        """Ensure all directories exist"""
        self.submissions_dir.mkdir(parents=True, exist_ok=True)
        self.courses_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    # Service configuration
    env: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # File limits
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set[str] = {".zip", ".py"}
    
    # Sub-configurations
    db: DatabaseSettings = DatabaseSettings()
    docker: DockerSettings = DockerSettings()
    paths: PathSettings = PathSettings()

    model_config = {
        "env_file": ".env",
        "env_prefix": "GRADER_",
        "env_nested_delimiter": "__"
    }

    def setup(self, create_dirs: bool = True):
        """Perform initial setup"""
        if create_dirs and self.env != "test":
            self.paths.ensure_dirs()
        return self

# Create global settings instance but don't create directories yet
settings = Settings().setup(create_dirs=False) 