from pyrainbird.resources import COMMANDS


def decode(data):
    if data[:2] in COMMANDS["responses"]:
        cmd_template = COMMANDS["responses"][data[:2]]
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
    request_command = "%sRequest" % command
    command_set = COMMANDS["requests"][request_command]
    if request_command in COMMANDS["requests"]:
        cmd_code = command_set["command"]
    else:
        raise Exception(
            "Command %s not available. Existing commands: %s"
            % (request_command, COMMANDS["requests"])
        )
    if len(args) > command_set["length"] - 1:
        raise Exception(
            "Too much parameters. %d expected:\n%s"
            % (command_set["length"] - 1, command_set)
        )
    params = (cmd_code,) + tuple(map(lambda x: int(x), args))
    arg_placeholders = (("%%0%dX" % ((command_set["length"] - len(args)) * 2))
                        if len(args) > 0
                        else "") + ("%02X" * (len(args) - 1))
    return ("%s" + arg_placeholders) % (params)
