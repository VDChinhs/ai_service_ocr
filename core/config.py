from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import BaseModel


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("AI Services API", env="PROJECT_NAME")
    PROJECT_DESCRIPTION: str = Field("AI Services API", env="PROJECT_DESCRIPTION")
    VERSION: str = Field("1.0.0", env="VERSION")

    FILE_MODEL_TITLE_BLOCK_ID: str = Field("17eWk3kOlcZVEF4ieLWA-QL27-Gi0rie3", env="FILE_MODEL_TITLE_BLOCK_ID")
    FILE_MODEL_COORDINATES_ID: str = Field("1Sw2Z3xKq_vadJfbtwQwr0_yfdxET3_7C", env="FILE_MODEL_COORDINATES_ID")

    RABBITMQ_URL: str = Field("", env="RABBITMQ_URL")
    TRITON_SERVER_URL: str = Field("http://10.0.10.62:8010", env="TRITON_SERVER_URL")


class ResourcePathConfig(BaseModel):
    PATH_MODEL_TITLE_BLOCK: str = "./models/title_block.pt"
    PATH_MODEL_COORDINATES: str = "./models/coordinates.pt"


resources = ResourcePathConfig()
settings = Settings()