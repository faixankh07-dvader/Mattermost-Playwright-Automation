import os
import pytest
from dotenv import load_dotenv
from utils.api_client import MattermostAPI

load_dotenv()

@pytest.fixture(scope="session")
def api(base_url):
    return MattermostAPI(base_url, os.environ["MM_ADMIN_USER"], os.environ["MM_ADMIN_PASS"])

@pytest.fixture(scope="session")
def team(api):
    return api.get_team(os.environ["MM_TEAM"])