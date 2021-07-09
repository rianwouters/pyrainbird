from pyrainbird.resources import (
    requests,
    responses
)


def decode(data):
    if data[:2] in responses:
        cmd_template = responses[data[:2]]
        result = {"type": cmd_template["type"]}
        for k, v in cmd_template.items():
            if isinstance(v, dict) and "position" in v and "length" in v:
                position_ = v["position"]
                length_ = v["length"]
                result[k] = int(data[position_: position_ + length_], 16)
        return result
    else:
        return {"data": data}


def encode(command, *args):
    if command in requests:
        request = requests[command]
        cmd_code = request["command"]
    else:
        raise Exception(
            "Command %s not available. Existing commands: %s"
            % (command, requests)
        )
    if len(args) > request["length"] - 1:
        raise Exception(
            "Too much parameters. %d expected:\n%s"
            % (request["length"] - 1, request)
        )
    params = (cmd_code,) + tuple(map(lambda x: int(x), args))
    arg_placeholders = (("%%0%dX" % ((request["length"] - len(args)) * 2))
                        if len(args) > 0
                        else "") + ("%02X" * (len(args) - 1))
    return ("%s" + arg_placeholders) % (params)
