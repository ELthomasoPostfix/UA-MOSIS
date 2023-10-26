from scanner import Scanner, CharacterStream


class Requirement6Scanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.current_stacks = []

        # define accepting states
        self.accepting_states = ["ERR"]

        self.prev_state = None
        self.next_state = None

    def __str__(self):
        return str(self.value) + "E" + str(self.exp)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            return "S1"

        elif state == "S1":
            if input == "P":
                self.prev_state = "S1"
                self.next_state = {
                    "PS ON \d\n": "S2",
                }
                return "P"
            else:
                return "S1"

        elif state == "S2":
            if input == "P":
                self.prev_state = "S2"
                self.next_state = {
                    "PS OFF \d\n": "S1",
                    "PS ON \d\n": "ERR",
                }
                return "P"
            else:
                return "S2"

        elif state == "ERR":
            return "ERR"

        elif state == "P":
            return "PS" if input == "S" else self.prev_state

        elif state == "PS":
            return "PS " if input == " " else self.prev_state

        elif state == "PS ":
            return "PS O" if input == "O" else self.prev_state

        elif state == "PS O":
            if input == "N":
                return "PS ON"
            elif input == "F":
                if "PS OFF \d\n" in self.next_state:
                    return "PS OF"
            return self.prev_state

        elif state == "PS ON":
            return "PS ON " if input == " " else self.prev_state

        elif state == "PS ON ":
            return "PS ON \d" if input.isdigit() else self.prev_state

        elif state == "PS ON \d":
            if input.isdigit():
                return "PS ON \d"
            elif input == "\n":
                return self.next_state["PS ON \d\n"]
            else:
                return self.prev_state

        elif state == "PS OF":
            return "PS OFF" if input == "F" else self.prev_state

        elif state == "PS OFF":
            return "PS OFF " if input == " " else self.prev_state

        elif state == "PS OFF ":
            return "PS OFF \d" if input.isdigit() else self.prev_state

        elif state == "PS OFF \d":
            if input.isdigit():
                return "PS OFF \d"
            elif input == "\n":
                return self.next_state["PS OFF \d\n"]
            else:
                return self.prev_state

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
        test_trace(f"traces/{trace}")

