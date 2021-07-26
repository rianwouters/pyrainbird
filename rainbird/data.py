from time import time

_DEFAULT_PAGE = 0


class Pageable(object):
    def __init__(self, page=_DEFAULT_PAGE):
        self.page = page

    def __hash__(self):
        return hash(self.page)

    def __eq__(self, o):
        return isinstance(o, Pageable) and self.page == o.page

    def __str__(self):
        return "page: %d" % self.page


class Echo(object):
    def __init__(self, echo):
        self.echo = echo

    def __hash__(self):
        return hash(self.echo)

    def __eq__(self, o):
        return isinstance(o, Echo) and self.echo == o.echo

    def __str__(self):
        return "echo: %02X" % self.echo


class CommandSupport(Echo):
    def __init__(self, support, echo=0):
        super().__init__(echo)
        self.support = support

    def __eq__(self, o):
        return (
            super().__eq__(o)
            and isinstance(o, CommandSupport)
            and o.support == self.support
        )

    def __hash__(self):
        return hash((super().__hash__(), self.support))

    def __str__(self):
        return "command support: %02X, %s" % (
            self.support,
            super().__str__(),
        )


class DeviceInfo:
    def __init__(self, model, revMajor, revMinor):
        self.model = model
        self.major = revMajor
        self.minor = revMinor

    def __hash__(self):
        return hash((self.model, self.major, self.minor))

    def __eq__(self, o):
        return (
            isinstance(o, DeviceInfo)
            and self.model == o.model
            and self.major == o.major
            and self.minor == o.minor
        )

    def __str__(self):
        return "model: %04X, version: %d.%d" % (
            self.model,
            self.major,
            self.minor,
        )


class StationStates(Pageable):
    def __init__(self, stations=0, page=_DEFAULT_PAGE, updated=None):
        super().__init__(page)
        self.update(stations, updated)

    def update(self, stations, updated=time()):
        self.stations = stations
        self.updated = updated

    def __getitem__(self, n):
        return bool(self.stations & (1 << (4 * 8 - 1 - n)))

    def __hash__(self):
        return hash((super().__hash__(), self.stations))

    def __eq__(self, o):
        return (
            super().__eq__(o)
            and isinstance(o, StationStates)
            and self.stations == o.stations
        )

    def __str__(self):
        return "available stations: %X, %s" % (
            self.stations,
            super().__str__(),
        )


class WaterBudget:
    def __init__(self, program, adjust):
        self.program = program
        self.adjust = adjust

    def __hash__(self):
        return hash((self.program, self.adjust))

    def __eq__(self, o):
        return (
            isinstance(o, WaterBudget)
            and self.program == o.program
            and self.adjust == o.adjust
        )

    def __str__(self):
        return "water budget: program: %d, hi: %02X, lo: %02X" % (
            self.program,
            self.adjust,
        )
