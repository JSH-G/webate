from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    options: str
    secret_key: str
    algorithms: str
    access_token_expire: int
    service_name: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    random_number: str
    account_sid: str
    auth_token:  str
    fromm: str

    class Config:
        env_file = ".env"

        
settings = Settings()