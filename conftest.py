from can import Bus
import pytest


@pytest.fixture(scope="session")
def bus_binar(can_binar_name):
    return Bus(can_binar_name, "socketcan", 500000)

@pytest.fixture(scope="session")
def can_binar_name(request: pytest.FixtureRequest):
    return request.config.getoption("--can_binar")

def pytest_addoption(parser):
    parser.addoption(
        "--can_binar",
        action="store",
        default="can0",
        help="can интерфейс для цапов и ацп",
    )