import datetime
import logging
import time
from functools import reduce

from urllib3 import Retry

from .client import RainbirdClient
from .data import (
    _DEFAULT_PAGE,
    AvailableStations,
    CommandSupport,
    ModelAndVersion,
    States,
    WaterBudget,
)

# TODO move commands to separate file as they are not part of the SIP specification
from .sip_messages import commands


class RainbirdController:
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
        self.zones = States()
        self.rain_sensor = None
        self.update_delay = update_delay
        self.zone_update_time = None
        self.sensor_update_time = None
        self.client = RainbirdClient(password, retry_strategy=retry_strategy)

    def get_model_and_version(self):
        r = self.command("ModelAndVersion")
        return ModelAndVersion(
            r["modelID"], r["protocolRevisionMajor"], r["protocolRevisionMinor"]
        )

    def get_available_stations(self, page=_DEFAULT_PAGE):
        mask = "%%0%dX" % responses["83"]["setStations"]["length"]
        return self._process_command(
            lambda resp: AvailableStations(
                mask % resp["setStations"], page=resp["pageNumber"]
            ),
            "AvailableStations",
            page,
        )

    def get_command_support(self, command):
        return self._process_command(
            lambda resp: CommandSupport(resp["support"], echo=resp["commandEcho"]),
            "CommandSupport",
            command,
        )

    def get_serial_number(self):
        return self._process_command(lambda resp: resp["serialNumber"], "SerialNumber")

    def get_current_time(self):
        return self._process_command(
            lambda resp: datetime.time(resp["hour"], resp["minute"], resp["second"]),
            "CurrentTime",
        )

    def get_current_date(self):
        return self._process_command(
            lambda resp: datetime.date(resp["year"], resp["month"], resp["day"]),
            "CurrentDate",
        )

    def water_budget(self, budget):
        return self._process_command(
            lambda resp: WaterBudget(resp["programCode"], resp["seasonalAdjust"]),
            "WaterBudget",
            budget,
        )

    def get_rain_sensor_state(self):
        if _check_delay(self.sensor_update_time, self.update_delay):
            self.logger.debug("Requesting current Rain Sensor State")
            response = self._process_command(
                lambda resp: bool(resp["sensorState"]),
                "CurrentRainSensorState",
            )
            if isinstance(response, bool):
                self.rain_sensor = response
                self.sensor_update_time = time.time()
            else:
                self.rain_sensor = None
        return self.rain_sensor

    def get_zone_state(self, zone, page=_DEFAULT_PAGE):
        if _check_delay(self.zone_update_time, self.update_delay):
            response = self._update_irrigation_state(page)
            if not isinstance(response, States):
                self.zones = States()
                return None
            else:
                self.zone_update_time = time.time()
        return self.zones.active(zone)

    def set_program(self, program):
        return self._process_command(lambda resp: True, "ManuallyRunProgram", program)

    def test_zone(self, zone):
        return self._process_command(lambda resp: True, "TestStations", zone)

    def irrigate_zone(self, zone, minutes):
        response = self._process_command(
            lambda resp: True, "ManuallyRunStation", zone, minutes
        )
        self._update_irrigation_state()
        return response == True and self.zones.active(zone)

    def stop_irrigation(self):
        r = self.command("StopIrrigation")
        self._update_irrigation_state()
        return not reduce((lambda x, y: x or y), self.zones.states)

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

        resp = self.client.post(f"http://{self.server}/stick", (sip_id,) + args)

        self.logger.debug(f"Response {resp}")

        return resp

    def _process_command(self, funct, cmd, *args):
        response = self.command(cmd, *args)
        return (
            funct(response)
            if response is not None
            and response["type"] == responses[requests[cmd]["response"]]["type"]
            else response
        )

    def _update_irrigation_state(self, page=_DEFAULT_PAGE):
        mask = "%%0%dX" % responses["BF"]["activeStations"]["length"]
        result = self._process_command(
            lambda resp: States((mask % resp["activeStations"])[:4]),
            "CurrentStationsActive",
            page,
        )
        if isinstance(result, States):
            self.zones = result
        return result


def _check_delay(update_time, update_delay):
    return update_time is None or time.time() > (update_time + update_delay)
