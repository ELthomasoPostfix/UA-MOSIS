#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e ErrorA -sSrgv ./harmonic-oscillator/HarmonicOscillator.drawio -d ./harmonic-oscillator

from pyCBD.Core import *
from pyCBD.lib.std import *


class CBDA(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['xA'])

        # Create the Blocks
        self.addBlock(IntegratorBlock("int1"))
        self.addBlock(IntegratorBlock("int2"))
        self.addBlock(NegatorBlock("neg"))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))
        self.addBlock(ConstantBlock("oneCt", value=(1)))

        # Create the Connections
        self.addConnection("zeroCt", "int1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("oneCt", "int2", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("int2", "int1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("int1", "neg", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("int1", "xA", output_port_name='OUT1')
        self.addConnection("neg", "int2", output_port_name='OUT1', input_port_name='IN1')


class CBDB(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['xB'])

        # Create the Blocks
        self.addBlock(NegatorBlock("neg"))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))
        self.addBlock(ConstantBlock("oneCt", value=(1)))
        self.addBlock(DerivatorBlock("der1"))
        self.addBlock(DerivatorBlock("der2"))

        # Create the Connections
        self.addConnection("zeroCt", "der2", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("oneCt", "der1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("neg", "der1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("neg", "xB", output_port_name='OUT1')
        self.addConnection("der1", "der2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("der2", "neg", output_port_name='OUT1', input_port_name='IN1')


class sint(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['sinT'])

        # Create the Blocks
        self.addBlock(GenericBlock("sin", block_operator=("sin")))
        self.addBlock(TimeBlock("clock"))

        # Create the Connections
        self.addConnection("clock", "sin", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sin", "sinT", output_port_name='OUT1')


class ErrorA(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['xt', 'sinT', 'et'])

        # Create the Blocks
        self.addBlock(IntegratorBlock("int"))
        self.addBlock(sint("sint"))
        self.addBlock(CBDA("cbda"))
        self.addBlock(AbsBlock("abs"))
        self.addBlock(NegatorBlock("neg"))
        self.addBlock(AdderBlock("add", numberOfInputs=(2)))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))

        # Create the Connections
        self.addConnection("int", "et", output_port_name='OUT1')
        self.addConnection("abs", "int", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("cbda", "neg", output_port_name='xA', input_port_name='IN1')
        self.addConnection("cbda", "xt", output_port_name='xA')
        self.addConnection("sint", "add", output_port_name='sinT', input_port_name='IN1')
        self.addConnection("sint", "sinT", output_port_name='sinT')
        self.addConnection("add", "abs", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("neg", "add", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("zeroCt", "int", output_port_name='OUT1', input_port_name='IC')


class ErrorB(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['xt', 'sinT', 'et'])

        # Create the Blocks
        self.addBlock(IntegratorBlock("int"))
        self.addBlock(sint("sint"))
        self.addBlock(CBDB("cbdb"))
        self.addBlock(AbsBlock("abs"))
        self.addBlock(NegatorBlock("neg"))
        self.addBlock(AdderBlock("add", numberOfInputs=(2)))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))

        # Create the Connections
        self.addConnection("int", "et", output_port_name='OUT1')
        self.addConnection("abs", "int", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("cbdb", "neg", output_port_name='xB', input_port_name='IN1')
        self.addConnection("cbdb", "xt", output_port_name='xB')
        self.addConnection("sint", "add", output_port_name='sinT', input_port_name='IN1')
        self.addConnection("sint", "sinT", output_port_name='sinT')
        self.addConnection("add", "abs", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("neg", "add", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("zeroCt", "int", output_port_name='OUT1', input_port_name='IC')


