import pytest


@pytest.fixture
def input_data(request):
    with open(request.param) as fd:
        yield fd


@pytest.fixture
def expected_data(request):
    with open(request.param) as fd:
        yield fd
