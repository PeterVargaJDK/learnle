import click

import uvicorn
import yaml
from click import ClickException
from fastapi import FastAPI
from pydantic import Field

from pydantic_settings import BaseSettings

from learnle.api import create_fast_api


class ApiSettings(BaseSettings):
    port: int = Field(alias='API_PORT', default=8000)


def setup_app() -> tuple[FastAPI, ApiSettings]:
    settings = ApiSettings()
    fast_api = create_fast_api()
    return fast_api, settings


@click.group()
def main():
    pass


@main.command()
def serve():
    fast_api, settings = setup_app()
    uvicorn.run(fast_api, port=settings.port)


@main.command()
def generate_openapi():
    fast_api, _ = setup_app()
    openapi_schema = fast_api.openapi()
    with open('openapi.yaml', 'w+') as f:
        f.write(yaml.dump(openapi_schema))


@main.command()
def check_openapi():
    fast_api, _ = setup_app()
    openapi_schema = fast_api.openapi()
    with open('openapi.yaml', 'r') as f:
        openapi_schema_in_repo = yaml.safe_load(f)
    if openapi_schema != openapi_schema_in_repo:
        # click.echo('openapi.yaml is not up-to-date')
        raise ClickException('openapi.yaml is not up-to-date')


if __name__ == '__main__':
    main()
