NAME = "CONSTANT_TOKEN_NAME"
VALUE = "CONSTANT_TOKEN_VALUE"

IF_STMT = "STRUCTURE_IF"
FOR_STMT = "STRUCTURE_FOR"
WHILE_STMT = "STRUCTURE_WHILE"
FUNCTION_STMT = "STRUCTURE_FUNCTION"
LAMBDA_STMT = "STRUCTURE_LAMBDA"
SWITCH_STMT = "STRUCTURE_SWITCH"
NO_STMT = "STRUCTURE_NONE"
STRING_STMT = "STRUCTURE_STRING"
INTEGER = "STRUCTURE_INTEGER"
CHARACTER = "STRUCTURE_CHARACTER"
LAMBDA_STMT = "LAMBDA_STMT"
LAMBDA_MAP = "LAMBDA_MAP"
LIST_STMT = "LIST_STMT"
VARIABLE_GET = "VARIABLE_GET"
VARIABLE_SET = "VARIABLE_SET"
FUNCTION_REFERENCE = "FUNCTION_REFERENCE"

VARIABLES = [VARIABLE_GET, VARIABLE_SET]

STRING_CONTENTS = "string_contents"
INTEGER_CONTENTS = "integer_contents"
IF_ON_TRUE = "if_on_true"
IF_ON_FALSE = "if_on_false"
FOR_VARIABLE = "for_variable"
FOR_BODY = "for_body"
WHILE_CONDITION = "while_condition"
WHILE_BODY = "while_body"
FUNCTION_NAME = "function_name"
FUNCTION_BODY = "function_body"
LAMBDA_BODY = "lambda_body"
LIST_ITEM = "list_item"
LIST_ITEMS = "list_items"
VARIABLE_NAME = "variable_name"

ONE = "one"
TWO = "two"

ONE_CHARS = "kv․∆ø"

CONSTANT_CHAR = "k"
VECTORISATION_CHAR = "v"
SINGLE_SCC_CHAR = "ı"

DECIMAL = "º"


OPENING = {
    IF_STMT: "[",
    FOR_STMT: "(",
    WHILE_STMT: "{",
    FUNCTION_STMT: "@",
    LAMBDA_STMT: "λ",
    SWITCH_STMT: "§",
    STRING_STMT: "`",
    LAMBDA_STMT: "λ",
    LAMBDA_MAP: "ƛ",
    LIST_STMT: "⟨",
    FUNCTION_REFERENCE: "°"
}

CLOSING = {
    IF_STMT: "]",
    FOR_STMT: ")",
    WHILE_STMT: "}",
    FUNCTION_STMT: ";",
    LAMBDA_STMT: ";",
    SWITCH_STMT: ";",
    STRING_STMT: "`",
    LAMBDA_STMT: ";",
    LAMBDA_MAP: ";",
    LIST_STMT: "⟩",
    FUNCTION_REFERENCE: ";"

}

DEFAULT_KEYS = {
    IF_STMT: IF_ON_TRUE,
    FOR_STMT: FOR_BODY,
    WHILE_STMT: WHILE_BODY,
    STRING_STMT: STRING_CONTENTS,
    INTEGER: INTEGER_CONTENTS,
    FUNCTION_STMT: FUNCTION_NAME,
    LAMBDA_STMT: LAMBDA_BODY,
    LAMBDA_MAP: LAMBDA_BODY,
    LIST_STMT: LIST_ITEM,
    FUNCTION_REFERENCE: FUNCTION_NAME
}

class Token:
    def __init__(self, name: str, value: object):
        self.name = name
        self.value = value

    def __getitem__(self, key: int):
        if key in (0, NAME):
            return self.name

        elif key in (1, VALUE):
            return self.value

        else:
            raise IndexError("Token value not in the range of 0/1")


def Tokenise(source: str) -> [Token]:
    tokens = []
    structure = NO_STMT
    structure_data = {}
    default_key = ""
    escaped = comment = False
    active_key = ""
    scc_mode, scc = False, ""
    nest_level = 0
    vectorisation = False



    for char in source:
        # print(char, structure, structure_data, nest_level, tokens, escaped)

        if comment:
            if char == "\n":
                comment = False
            continue
        if escaped:
            if structure != NO_STMT:
                structure_data[active_key] += "\\" + char
            else:
                tokens.append(Token(CHARACTER, char))

            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue




        elif structure == STRING_STMT:
            if char == CLOSING[STRING_STMT]:
                nest_level -= 1
                this_token = Token(structure, structure_data)
                tokens.append(this_token)
                structure_data = {}
                structure = NO_STMT
            else:
                if char == "\\":
                    escaped = True
                else:
                    structure_data[active_key] += char

            continue

        elif structure == INTEGER:
            if char in "0123456789º":
                structure_data[INTEGER_CONTENTS] += char
                continue
            else:
                value = structure_data[active_key]
                end = value.find("º", value.find("º") + 1)

                if end > -1:
                    value = value[:value.find("º", value.find("º"))]

                if value.isnumeric():
                    this_token = Token(INTEGER, int(value))

                else:
                    this_token = Token(INTEGER, float(value.replace("º", ".")))
                tokens.append(this_token)
                structure_data = {}
                structure = NO_STMT

        elif structure in VARIABLES:
            import string
            if char in string.ascii_letters + "_":
                structure_data[active_key] += char
                continue
            else:
                this_token = Token(structure, structure_data)
                tokens.append(this_token)
                structure_data = {}
                structure = NO_STMT


        elif scc_mode:
            scc += char
            if len(scc) == 2:
                scc_mode = False
                this_token = Token(SINGLE_SCC_CHAR, scc)
                tokens.append(this_token)
                scc = ""
                structure = NO_STMT
            continue


        elif structure in ONE_CHARS:
            this_token = Token(structure, char)
            tokens.append(this_token)
            structure = NO_STMT
            continue

        if char in OPENING.values():
            if nest_level > 0:
                if char != CLOSING[STRING_STMT]:
                    nest_level += 1
                structure_data[active_key] += char
                continue

            elif char == OPENING[IF_STMT]:
                structure = IF_STMT
                active_key = IF_ON_TRUE

            elif char == OPENING[WHILE_STMT]:
                structure = WHILE_STMT
                active_key = WHILE_CONDITION

            elif char == OPENING[FOR_STMT]:
                structure = FOR_STMT
                active_key = FOR_VARIABLE


            elif char == OPENING[STRING_STMT]:
                structure = STRING_STMT
                active_key = STRING_CONTENTS

            elif char == OPENING[FUNCTION_STMT]:
                structure = FUNCTION_STMT
                active_key = FUNCTION_NAME

            elif char == OPENING[LAMBDA_STMT]:
                structure = LAMBDA_STMT
                active_key = LAMBDA_BODY

            elif char == OPENING[LAMBDA_MAP]:
                structure = LAMBDA_MAP
                active_key = LAMBDA_BODY

            elif char == OPENING[LIST_STMT]:
                structure = LIST_STMT
                active_key = LIST_ITEM
                structure_data[LIST_ITEMS] = []

            elif char == OPENING[FUNCTION_REFERENCE]:
                structure = FUNCTION_REFERENCE
                active_key = FUNCTION_NAME

            else:
                raise NotImplementedError("That structure isn't implemented yet")

            structure_data[active_key] = ""
            nest_level += 1
            default_key = DEFAULT_KEYS[structure]


        elif char in CLOSING.values():
            nest_level -= 1
            if nest_level > 0:
                structure_data[active_key] += char
            else:

                additional_token = None

                if structure == LAMBDA_MAP:
                    additional_token = Token(NO_STMT, "M")
                    structure = LAMBDA_STMT

                elif structure == LIST_STMT:
                    structure_data[LIST_ITEMS].append(structure_data[LIST_ITEM])
                    del structure_data[LIST_ITEM]

                else:
                    if default_key not in structure_data:
                        structure_data[default_key] = structure_data[active_key]
                        del structure_data[active_key]

                this_token = Token(structure, structure_data)
                tokens.append(this_token)
                structure_data = {}
                structure = NO_STMT

                if additional_token:
                    tokens.append(additional_token)


        elif char == "|" and nest_level == 1:
            # Oh, the magical pipe which makes Vyxal and Keg unique
            if structure == IF_STMT:
                active_key = IF_ON_FALSE

            elif structure == WHILE_STMT:
                active_key = WHILE_BODY

            elif structure == FOR_STMT:
                active_key = FOR_BODY

            elif structure == FUNCTION_STMT:
                active_key = FUNCTION_BODY

            elif structure == LIST_STMT:
                structure_data[LIST_ITEMS].append(structure_data[active_key])

            structure_data[active_key] = ""


        elif structure != NO_STMT:
            structure_data[active_key] += char


        elif char in "0123456789º":
            structure = INTEGER
            structure_data[INTEGER_CONTENTS] = char
            active_key = INTEGER_CONTENTS
            default_key = DEFAULT_KEYS[INTEGER]

        elif char == "£":
            structure = VARIABLE_SET
            structure_data[VARIABLE_NAME] = ""
            active_key = VARIABLE_NAME
            default_key = VARIABLE_NAME

        elif char == "¥":
            structure = VARIABLE_GET
            structure_data[VARIABLE_NAME] = ""
            active_key = VARIABLE_NAME
            default_key = VARIABLE_NAME


        elif char == VECTORISATION_CHAR:
            vectorisation = True
            continue


        elif char in ONE_CHARS:
            char_mode = ONE
            structure = char

        elif char == SINGLE_SCC_CHAR:
            scc_mode = True

        elif char == "#":
            comment = True
            continue

        else:
            if vectorisation:
                tokens += Tokenise("ƛ" + char + ";")
                vectorisation = False
            else:
                this_token = Token(NO_STMT, char)
                tokens.append(this_token)



    if structure != NO_STMT:
        # print(structure_data, default_key, active_key)
        additional_token = None

        if structure == LAMBDA_MAP:
            additional_token = Token(NO_STMT, "M")
            structure = LAMBDA_STMT

        elif structure == LIST_STMT:
            structure_data[LIST_ITEMS].append(structure_data[LIST_ITEM])
            del structure_data[LIST_ITEM]

        elif structure == INTEGER:
            value = structure_data[default_key]
            end = value.find("º", value.find("º") + 1)

            if end > -1:
                value = value[:end]

            if value.isnumeric():
                structure_data = int(value)

            else:
                structure_data = float(value.replace("º", "."))

        else:
            if default_key not in structure_data:
                structure_data[default_key] = structure_data[active_key]
                del structure_data[active_key]

        this_token = Token(structure, structure_data)
        tokens.append(this_token)
        structure_data = {}
        structure = NO_STMT

        if additional_token:
            tokens.append(additional_token)
    return tokens


if __name__ == "__main__":
    tests = [r"`\\`"]
    for test in tests:
        print([(n[0], n[1]) for n in Tokenise(test)])
