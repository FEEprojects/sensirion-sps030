"""
    Database of sensirion error codes
    Philip Basford
    19/02/2019
"""
CODE_NO_ERROR = 0x00
CODE_WRONG_LENGTH = 0x01
CODE_UNKNOWN_CMD = 0x02
CODE_NO_ACCESS = 0x03
CODE_ILLEGAL_CMD = 0x04
CODE_ILLEGAL_ARG = 0x28
CODE_CMD_NOT_ALLOWED = 0x43

CODES = {
    CODE_NO_ERROR : "OK",
    CODE_WRONG_LENGTH : "Wrong data length for command",
    CODE_UNKNOWN_CMD : "Unknown command",
    CODE_NO_ACCESS : "No Access right for command",
    CODE_ILLEGAL_CMD : "Illegal command parameter or parameter out of allowed range",
    CODE_ILLEGAL_ARG : "Internal function argument out of range",
    CODE_CMD_NOT_ALLOWED : "Command not allowed in current state"
}

def lookup_code(code):
    """
        Lookup the error code to get it's definition
    """
    return CODES.get(code, "Unknown Error 0x%02x" % code)
