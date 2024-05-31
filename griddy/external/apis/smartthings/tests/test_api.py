import pytest
from django.conf import settings
from external.apis.smartthings.api import Api
from external.apis.smartthings.capabilities import (
    FLOW_TEMPERATURE_CAPABILITY,
    FlowTemperatureCapability,
    OnOffCapability,
)
from external.apis.smartthings.exceptions import SmartthingsApiException


@pytest.fixture()
def smartthings_api():
    return Api(
        base_url="https://api.smartthings.com/v1/", token=settings.TEST_SMARTTHINGS_API_TOKEN
    )


@pytest.mark.vcr()
@pytest.mark.block_network()
def test_devices(smartthings_api):
    response = smartthings_api.devices()

    items = response["items"]
    assert len(items) == 2
    assert items[0]["deviceId"] == settings.TEST_SMARTTHINGS_DEVICE_ID


@pytest.mark.vcr()
@pytest.mark.block_network()
def test_device_status(smartthings_api):
    response = smartthings_api.device_status(device_id=settings.TEST_SMARTTHINGS_DEVICE_ID)

    assert response["components"]["main"]["switch"]["switch"]["value"] == "off"
    assert response["components"]["INDOOR"]["switch"]["switch"]["value"] == "on"


@pytest.mark.vcr()
@pytest.mark.block_network()
def test_capability(smartthings_api):
    response = smartthings_api.capability(name=FLOW_TEMPERATURE_CAPABILITY)

    assert response["id"] == FLOW_TEMPERATURE_CAPABILITY
    assert response["commands"]["setCoolingSetpoint"]["name"] == "setCoolingSetpoint"


@pytest.mark.vcr()
@pytest.mark.block_network()
def test_command(smartthings_api):
    command = FlowTemperatureCapability.set_flow_temperature(temperature=50, module="INDOOR")

    response = smartthings_api.command(settings.TEST_SMARTTHINGS_DEVICE_ID, command)

    results = response["results"][0]
    assert results["id"] == settings.TEST_SMARTTHINGS_COMMAND_ID
    assert results["status"] == "COMPLETED"


@pytest.mark.vcr()
@pytest.mark.block_network()
def test_process_response_bad_request(smartthings_api):
    smartthings_api.token = "bad_token"

    with pytest.raises(SmartthingsApiException):
        smartthings_api.devices()


@pytest.mark.vcr()
@pytest.mark.block_network()
def test_on_command(smartthings_api):
    command = OnOffCapability.turn_on(module="INDOOR")

    response = smartthings_api.command(settings.TEST_SMARTTHINGS_DEVICE_ID, command)

    results = response["results"][0]
    assert results["id"] == settings.TEST_SMARTTHINGS_COMMAND_ID
    assert results["status"] == "COMPLETED"


@pytest.mark.vcr()
@pytest.mark.block_network()
def test_off_command(smartthings_api):
    command = OnOffCapability.turn_off(module="INDOOR")

    response = smartthings_api.command(settings.TEST_SMARTTHINGS_DEVICE_ID, command)

    results = response["results"][0]
    assert results["id"] == settings.TEST_SMARTTHINGS_COMMAND_ID
    assert results["status"] == "COMPLETED"
