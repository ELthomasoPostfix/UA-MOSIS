from scanner import Scanner, CharacterStream

transition_table = {
    "S1": {
        "D": [("S2", "_DS ON @\n"), ("ERR", "_DS OFF @\n")],
        "P": [("ERR", "_PS ON @\n"), ("ERR", "_PS OFF @\n")],
        "": [("S1", "")]
    },
    "S2": {
        "D": [("ERR", "_DS ON @\n"), ("S3", "_DS OFF @\n")],
        "P": [("ERR", "_PS ON @\n"), ("ERR", "_PS OFF @\n")],
        "": [("S2", "")]
    },
    "S3": {
        "D": [("S5", "_DS ON @\n"), ("ERR", "_DS OFF @\n")],
        "P": [("S4", "_PS ON @\n"), ("ERR", "_PS OFF @\n")],
        "": [("S3", "")]
    },
    "S4": {
        "D": [("S7", "_DS ON @\n"), ("ERR", "_DS OFF @\n")],
        "P": [("ERR", "_PS ON @\n"), ("S1", "_PS OFF @\n")],
        "": [("S4", "")]
    },
    "S5": {
        "D": [("ERR", "_DS ON @\n"), ("S3", "_DS OFF @\n")],
        "P": [("S7", "_PS ON @\n"), ("ERR", "_PS OFF @\n")],
        "": [("S5", "")]
    },
    "S6": {
        "D": [("S8", "_DS ON @\n"), ("ERR", "_DS OFF @\n")],
        "P": [("ERR", "_PS ON @\n"), ("S3", "_PS OFF @\n")],
        "": [("S6", "")]
    },
    "S7": {
        "D": [("ERR", "_DS ON @\n"), ("S6", "_DS OFF @\n")],
        "P": [("ERR", "_PS ON @\n"), ("S2", "_PS OFF @\n")],
        "": [("S7", "")]
    },
    "S8": {
        "D": [("ERR", "_DS ON @\n"), ("S6", "_DS OFF @\n")],
        "P": [("ERR", "_PS ON @\n"), ("S5", "_PS OFF @\n")],
        "": [("S8", "")]
    },
}


class Requirement6Scanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.current_stacks = []

        # define accepting states
        self.accepting_states = ["ERR"]

        self.prev_state = None
        self.sub_paths = []

    def __str__(self):
        return str(self.value) + "E" + str(self.exp)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            return "S1"

        elif state[0] == "S":
            state_table = transition_table[state]
            if input in state_table:
                self.prev_state = state
                self.sub_paths = state_table[input]
                return f"_{input}"
            elif "" in state_table:
                return state_table[""][0][0]
            else:
                return "ERR"

        elif state == "ERR":
            return state

        # Is currently in a substate
        elif state[0] == "_":
            # Resolve current substate depth
            current_depth = len(state)

            # Determine all possible remaining paths
            accepted_paths = []
            is_digit = False
            for path in self.sub_paths:
                # Get the character required to correctly transition
                required_char = path[1][current_depth]

                # "@" is a special encoding of \d+ to reduce code length
                if required_char == "@":
                    if input.isdigit():
                        is_digit = True
                        accepted_paths.append(path)
                        continue
                    else:
                        state += "@"
                        required_char = path[1][current_depth + 1]

                # Otherwise, check if the required character matches the input
                if required_char == input:
                    accepted_paths.append(path)

            # If there were no paths that matched, return to the previous state
            if len(accepted_paths) == 0:
                return self.prev_state

            # If there was a single path that matched, and substate is full matched, go to corresponding destination state
            elif len(accepted_paths) == 1 and state + input == accepted_paths[0][1]:
                return accepted_paths[0][0]

            # Otherwise, update the sub_paths and proceed to the next character
            else:
                self.sub_paths = accepted_paths
                if not is_digit:
                    state += input
                return state

        else:
            return None

    def entry(self, state, input):
        pass


def test_trace(trace):
    with open(trace, "r") as f:
        contents = f.read()
    stream = CharacterStream(contents)
    scanner = Requirement6Scanner(stream)
    success = scanner.scan()
    if success:
        print(f"{trace:26} -- Accepted")
    else:
        print(f"{trace:26} -- Not Accepted")

if __name__ == "__main__":
    import os

    for trace in os.listdir("traces"):
        # if trace == "trace5.txt":
        test_trace(f"traces/{trace}")

