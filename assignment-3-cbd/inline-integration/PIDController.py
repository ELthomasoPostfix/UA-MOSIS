#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e PIDController -sSrgv ../Diagrams/PIDController.drawio

from pyCBD.Core import *
from pyCBD.lib.std import *


class PID(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN'], output_ports=['OUT'])

        # Create the Blocks
        self.addBlock(ConstantBlock("Kp", value=(390)))
        self.addBlock(ConstantBlock("Kid", value=(20)))
        self.addBlock(IntegratorBlock("int"))
        self.addBlock(DerivatorBlock("der"))
        self.addBlock(AdderBlock("sum1", numberOfInputs=(2)))
        self.addBlock(AdderBlock("sum2", numberOfInputs=(2)))
        self.addBlock(ProductBlock("prod1", numberOfInputs=(2)))
        self.addBlock(ProductBlock("prod2", numberOfInputs=(2)))
        self.addBlock(ProductBlock("prod3", numberOfInputs=(2)))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))

        # Create the Connections
        self.addConnection("IN", "int", input_port_name='IN1')
        self.addConnection("IN", "der", input_port_name='IN1')
        self.addConnection("IN", "prod1", input_port_name='IN2')
        self.addConnection("Kp", "prod1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("zeroCt", "der", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("zeroCt", "int", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("int", "prod2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("der", "prod3", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("Kid", "prod2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("Kid", "prod3", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("prod1", "sum1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("prod2", "sum1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("prod3", "sum2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum1", "sum2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum2", "OUT", output_port_name='OUT1')


