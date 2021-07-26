import datetime
import logging
from time import time
from functools import reduce

from urllib3 import Retry

from .client import RainbirdClient
from .data import (
    _DEFAULT_PAGE,
    StationStates,
    CommandSupport,
    DeviceInfo,
    WaterBudget,
)

# TODO move commands to separate file as they are not part of the SIP specification
from .sip_messages import commands


class Controller:
    def __init__(
        self,
        server,
        password,
        update_delay=20,
        retry_strategy=Retry(3, backoff_factor=20),
        logger=logging.getLogger(__name__),
    ):
        self.server = server
        self.logger = logger
        self.zones = StationStates()
        self.rain_sensor = None
        self.update_delay = update_delay
        self.zone_update_time = None
        self.sensor_update_time = None
        self.client = RainbirdClient(password, retry_strategy=retry_strategy)

    def get_model_and_version(self):
        r = self.command("ModelAndVersion")
        return DeviceInfo(
            r["modelID"], r["protocolRevisionMajor"], r["protocolRevisionMinor"]
        )

    def get_available_stations(self, page=_DEFAULT_PAGE):
        r = self.command("AvailableStations", page)
        return StationStates(r["setStations"], page=r["pageNumber"])

    def get_command_support(self, command):
        r = self.command("CommandSupport")
        return CommandSupport(r["support"], echo=r["commandEcho"])

    def get_serial_number(self):
        r = self.command("SerialNumber")
        return r["serialNumber"]

    def get_current_time(self):
        r = self.commmand("CurrentTime")
        return datetime.time(r["hour"], r["minute"], r["second"])

    def get_current_date(self):
        r = self.command("CurrentDate")
        return datetime.date(r["year"], r["month"], r["day"])

    def water_budget(self, budget):
        r = self.command("WaterBudget", budget)
        return WaterBudget(r["programCode"], r["seasonalAdjust"])

    def get_rain_sensor_state(self):
        if _check_delay(self.sensor_update_time, self.update_delay):
            self.logger.debug("Requesting current Rain Sensor State")
            r = self.command("CurrentRainSensorState")
            self.rain_sensor = bool(r["sensorState"])
            self.sensor_update_time = time()
        return self.rain_sensor

    def get_zone_state(self, zone, page=_DEFAULT_PAGE):
        if _check_delay(self.zone_update_time, self.update_delay):
            self._update_irrigation_state(page)
        return self.zones(zone)

    def set_program(self, program):
        return self.command("ManuallyRunProgram", program)

    def test_zone(self, zone):
        return self.command("TestStations", zone)

    def irrigate_zone(self, zone, minutes):
        self.command("ManuallyRunStation", zone, minutes)
        self._update_irrigation_state()
        return self.zones[zone]

    def stop_irrigation(self):
        self.command("StopIrrigation")
        self._update_irrigation_state()

    def get_rain_delay(self):
        r = self.command("RainDelayGet")
        return r["delaySetting"]

    def set_rain_delay(self, days):
        self.command("RainDelaySet", days)

    def advance_zone(self, param):
        self.command("AdvanceStation", param)

    def get_current_irrigation(self):
        r = self.command("CurrentIrrigationState")
        return bool(r["irrigationState"])

    def command(self, command, *args):
        sip_id = commands.get(command)
        if not sip_id:
            raise Exception(
                f"Unknown command (command). Existing commands: {commands.keys()}"
            )
        self.logger.debug(f"Requested sip id {sip_id}")
        r = self.client.post(f"http://{self.server}/stick", (sip_id,) + args)
        self.logger.debug(f"Response {r}")
        return r

    def _update_irrigation_state(self, page=_DEFAULT_PAGE):
        r = self.command("CurrentStationsActive", page)
        self.zones.update(r["activeStations"])


def _check_delay(update_time, update_delay):
    return update_time is None or time() > (update_time + update_delay)
