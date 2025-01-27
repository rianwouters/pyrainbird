import unittest

from parameterized import parameterized

from rainbird.rainbird import encode, decode


def encode_name_func(testcase_func, param_num, param):
    return f'{testcase_func.__name__}_{param_num}_{parameterized.to_safe_name(param.args[1])}'

def decode_name_func(testcase_func, param_num, param):
    return f'{testcase_func.__name__}_{param_num}_{parameterized.to_safe_name(param.args[0]["type"])}'
    
class TestSequence(unittest.TestCase):
    @parameterized.expand(
        [
            ["02", "ModelAndVersion"],
            ["030C", "AvailableStations", 12],
            ["040B", "CommandSupport", 11],
            ["05", "SerialNumber"],
            ["10", "CurrentTime"],
            ["12", "CurrentDate"],
            ["300D", "WaterBudget", 13],
            ["3E", "CurrentRainSensorState"],
            ["3F10", "CurrentStationsActive", 16],
            ["3811", "ManuallyRunProgram", 17],
            ["39000612", "ManuallyRunStation", 6, 18],
            ["3A17", "TestStations", 23],
            ["40", "StopIrrigation"],
            ["36", "RainDelayGet"],
            ["37000F", "RainDelaySet", 15],
            ["4208", "AdvanceStation", 8],
            ["48", "CurrentIrrigationState"],
        ],
        name_func=encode_name_func,
    )
    def test_encode(self, expected, command, *vargs):
        self.assertEqual(expected, encode(command, *vargs))

    @parameterized.expand(
        [
            [
                {
                    "type": "NotAcknowledge",
                    "commandEcho": 2,
                    "NAKCode": 3,
                },
                "000203",
            ],
            [{"type": "Acknowledge", "commandEcho": 6}, "0106"],
            [
                {
                    "type": "ModelAndVersion",
                    "modelID": 6,
                    "protocolRevisionMajor": 9,
                    "protocolRevisionMinor": 12,
                },
                "820006090C",
            ],
            [
                {
                    "type": "AvailableStations",
                    "pageNumber": 15,
                    "setStations": 16,
                },
                "830F0010",
            ],
            [
                {
                    "type": "CommandSupport",
                    "commandEcho": 0x82,
                    "support": 1,
                },
                "848201",
            ],
            [
                {"type": "SerialNumber", "serialNumber": 0x8963},
                "850000000000008963",
            ],
            [
                {
                    "type": "CurrentTime",
                    "hour": 12,
                    "minute": 54,
                    "second": 35,
                },
                "900C3623",
            ],
            [
                {
                    "type": "CurrentDate",
                    "day": 18,
                    "month": 11,
                    "year": 2018,
                },
                "9212B7E2",
            ],
            [
                {
                    "type": "WaterBudget",
                    "programCode": 3,
                    "seasonalAdjust": 0x83,
                },
                "B0030083",
            ],
            [
                {"type": "CurrentRainSensorState", "sensorState": 1},
                "BE01",
            ],
            [
                {
                    "type": "CurrentStationsActive",
                    "pageNumber": 1,
                    "activeStations": 0b00010000000000000000000000000000,
                },
                "BF0110000000",
            ],
            [
                {"type": "RainDelaySetting", "delaySetting": 3},
                "B60003",
            ],
            [
                {
                    "type": "CurrentIrrigationState",
                    "irrigationState": 1,
                },
                "C801",
            ],
        ],
        name_func=decode_name_func,
    )
    def test_decode(self, expected, data):
        self.assertEqual(expected, decode(data))
