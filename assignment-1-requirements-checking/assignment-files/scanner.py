#
# scanner.py
#
# Based on code for COMP 304B Assignment 3
# Updated to Python 3 in 2021
#

# trace FSA dynamics (True | False)
__trace__ = False


# __trace__ = True

class CharacterStream:
    """
    A stream of characters helper class.
    """

    def __init__(self, string):
        self.string = string
        self.last_ptr = -1
        self.cur_ptr = -1

    def __repr__(self):
        return self.string

    def __str__(self):
        return self.string

    def peek(self):
        if self.cur_ptr + 1 < len(self.string):
            return self.string[self.cur_ptr + 1]
        return None

    def consume(self):
        self.cur_ptr += 1

    def commit(self):
        self.last_ptr = self.cur_ptr

    def rollback(self):
        self.cur_ptr = self.last_ptr


class Scanner:
    """
    A simple Finite State Automaton simulator.
    Used for scanning an input stream.
    """

    def __init__(self, stream):
        self.set_stream(stream)
        self.current_state = None
        self.accepting_states = []

    def set_stream(self, stream):
        self.stream = stream

    def scan(self):
        self.current_state = self.transition(self.current_state, None)

        if __trace__:
            print("\ndefault transition --> " + self.current_state)

        while True:
            # look ahead at the next character in the input stream
            next_char = self.stream.peek()

            # stop if this is the end of the input stream
            if next_char is None: break

            if __trace__:
                if self.current_state is not None:
                    print("transition", self.current_state, "-|", next_char if next_char != '\n' else "\\n", end=' ')

            # perform transition and its action to the appropriate new state
            next_state = self.transition(self.current_state, next_char)

            if __trace__:
                if next_state is None:
                    print("")
                else:
                    print("|->", next_state)

            # stop if a transition was not possible
            if next_state is None:
                break
            else:
                self.current_state = next_state
                # perform the new state's entry action (if any)
                self.entry(self.current_state, next_char)

            # now, actually consume the next character in the input stream
            next_char = self.stream.consume()

        if __trace__:
            print("")

        # now check whether to accept consumed characters
        success = self.current_state in self.accepting_states
        if success:
            self.stream.commit()
        else:
            self.stream.rollback()
        return success


## An example scanner, see http://msdl.cs.mcgill.ca/people/hv/teaching/SoftwareDesign/COMP304B2003/assignments/assignment3/solution/
class NumberScanner(Scanner):
    def __init__(self, stream):
        # superclass constructor
        super().__init__(stream)

        self.value = 0
        self.exp = 0
        self.scale = 1

        # define accepting states
        self.accepting_states = ["S2", "S4", "S7"]

    def __str__(self):
        return str(self.value) + "E" + str(self.exp)

    def transition(self, state, input):
        """
        Encodes transitions and actions
        """
        if state is None:
            # action
            # initialize variables
            self.value = 0
            self.exp = 0
            # new state
            return "S1"

        elif state == "S1":
            if input == '.':
                # action
                self.scale = 0.1
                # new state
                return "S3"
            elif '0' <= input <= '9':
                # action
                self.value = ord(input.lower()) - ord('0')
                # new state
                return "S2"
            else:
                return None

        elif state == "S2":
            if input == '.':
                # action
                self.scale = 0.1
                # new state
                return "S4"
            elif '0' <= input <= '9':
                # action
                self.value = self.value * 10 + ord(input.lower()) - ord('0')
                # new state
                return "S2"
            elif input.lower() == 'e':
                # action
                self.exp = 1
                # new state
                return "S5"
            else:
                return None

        elif state == "S3":
            if '0' <= input <= '9':
                # action
                self.value += self.scale * (ord(input.lower()) - ord('0'))
                self.scale /= 10
                # new state
                return "S4"
            else:
                return None

        elif state == "S4":
            if '0' <= input <= '9':
                # action
                self.value += self.scale * (ord(input.lower()) - ord('0'))
                self.scale /= 10
                # new state
                return "S4"
            elif input.lower() == 'e':
                # action
                self.exp = 1
                # new state
                return "S5"
            else:
                return None

        elif state == "S5":
            if input == '+':
                # new state
                return "S6"
            elif input == '-':
                # action
                self.exp = -1
                # new state
                return "S6"
            elif '0' <= input <= '9':
                # action
                self.exp *= ord(input.lower()) - ord('0')
                # new state
                return "S7"
            else:
                return None

        elif state == "S6":
            if '0' <= input <= '9':
                # action
                self.exp *= ord(input.lower()) - ord('0')
                # new state
                return "S7"
            else:
                return None

        elif state == "S7":
            if '0' <= input <= '9':
                # action
                self.exp = self.exp * 10 + ord(input.lower()) - ord('0')
                # new state
                return "S7"
            else:
                return None

        else:
            return None

    def entry(self, state, input):
        pass


if __name__ == "__main__":
    stream = CharacterStream("123e-4")
    scanner = NumberScanner(stream)
    success = scanner.scan()
    if success:
        print("Stream has been accepted. Number: %se%s" % (str(scanner.value), str(scanner.exp)))
    else:
        print("Stream not accepted")
