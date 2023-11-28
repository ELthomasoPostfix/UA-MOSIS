#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e BWDEulerCalc -sSrgv ./integration-methods/IntegrationMethods.drawio -d ./integration-methods

from pyCBD.Core import *
from pyCBD.lib.std import *


class BWDEulerInt(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1', 'IC'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(ConstantBlock("zeroCt", value=(0)))
        self.addBlock(DeltaTBlock("deltaT"))
        self.addBlock(DelayBlock("delay1"))
        self.addBlock(ProductBlock("prod", numberOfInputs=(2)))
        self.addBlock(DelayBlock("delay2"))
        self.addBlock(AdderBlock("sum", numberOfInputs=(2)))

        # Create the Connections
        self.addConnection("IN1", "delay1", input_port_name='IN1')
        self.addConnection("IC", "delay2", input_port_name='IC')
        self.addConnection("zeroCt", "delay1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("prod", "sum", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("delay2", "sum", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum", "delay2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum", "OUT1", output_port_name='OUT1')
        self.addConnection("delay1", "prod", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("deltaT", "prod", output_port_name='OUT1', input_port_name='IN1')


class FWDEulerInt(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1', 'IC'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(ConstantBlock("zeroCt", value=(0)))
        self.addBlock(DeltaTBlock("deltaT"))
        self.addBlock(DelayBlock("delay1"))
        self.addBlock(ProductBlock("prod", numberOfInputs=(2)))
        self.addBlock(DelayBlock("delay2"))
        self.addBlock(AdderBlock("sum", numberOfInputs=(2)))

        # Create the Connections
        self.addConnection("IN1", "prod", input_port_name='IN1')
        self.addConnection("IC", "delay2", input_port_name='IC')
        self.addConnection("prod", "sum", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("delay2", "sum", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum", "delay2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum", "OUT1", output_port_name='OUT1')
        self.addConnection("deltaT", "delay1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("zeroCt", "delay1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("delay1", "prod", output_port_name='OUT1', input_port_name='IN2')


class TrapezoidIntSimple(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1', 'IC'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(ConstantBlock("zeroCt", value=(0)))
        self.addBlock(DeltaTBlock("deltaT"))
        self.addBlock(DelayBlock("delay1"))
        self.addBlock(ProductBlock("prod2", numberOfInputs=(2)))
        self.addBlock(DelayBlock("delay2"))
        self.addBlock(AdderBlock("sum2", numberOfInputs=(2)))
        self.addBlock(AdderBlock("sum1", numberOfInputs=(2)))
        self.addBlock(ProductBlock("prod1", numberOfInputs=(2)))
        self.addBlock(ConstantBlock("twoCt", value=(2)))
        self.addBlock(InverterBlock("inv"))

        # Create the Connections
        self.addConnection("IN1", "delay1", input_port_name='IN1')
        self.addConnection("IN1", "sum1", input_port_name='IN2')
        self.addConnection("IC", "delay2", input_port_name='IC')
        self.addConnection("delay2", "sum2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum2", "delay2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum2", "OUT1", output_port_name='OUT1')
        self.addConnection("zeroCt", "delay1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("delay1", "sum1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("twoCt", "inv", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum1", "prod1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("inv", "prod1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("deltaT", "prod2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("prod1", "prod2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("prod2", "sum2", output_port_name='OUT1', input_port_name='IN1')


class AnalyticFunc(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['t'], output_ports=['gt'])

        # Create the Blocks
        self.addBlock(ConstantBlock("oneCt", value=(1)))
        self.addBlock(NegatorBlock("neg"))
        self.addBlock(AdderBlock("sum2", numberOfInputs=(2)))
        self.addBlock(AdderBlock("sum1", numberOfInputs=(2)))
        self.addBlock(PowerBlock("power"))
        self.addBlock(ProductBlock("prod1", numberOfInputs=(2)))
        self.addBlock(ConstantBlock("twoCt", value=(2)))
        self.addBlock(InverterBlock("inv"))

        # Create the Connections
        self.addConnection("oneCt", "neg", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("oneCt", "sum1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("neg", "sum2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("t", "sum1", input_port_name='IN1')
        self.addConnection("t", "sum2", input_port_name='IN2')
        self.addConnection("sum2", "prod1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("prod1", "gt", output_port_name='OUT1')
        self.addConnection("sum1", "power", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("twoCt", "power", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("power", "inv", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("inv", "prod1", output_port_name='OUT1', input_port_name='IN1')


class AnalyticIntCalc(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['I'])

        # Create the Blocks
        self.addBlock(ConstantBlock("twoCt", value=(2)))
        self.addBlock(AdderBlock("sum1", numberOfInputs=(2)))
        self.addBlock(ConstantBlock("oneCt", value=(1)))
        self.addBlock(AdderBlock("sum2", numberOfInputs=(2)))
        self.addBlock(GenericBlock("log", block_operator=("log")))
        self.addBlock(InverterBlock("inv"))
        self.addBlock(ProductBlock("prod", numberOfInputs=(2)))
        self.addBlock(AdderBlock("sum3", numberOfInputs=(2)))
        self.addBlock(TimeBlock("clock"))
        self.addBlock(NegatorBlock("2JxUFJoTUBjuM0Cz1H6F-208"))

        # Create the Connections
        self.addConnection("sum1", "log", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum1", "inv", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("inv", "prod", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("twoCt", "prod", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("twoCt", "2JxUFJoTUBjuM0Cz1H6F-208", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("prod", "sum2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("log", "sum2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum3", "I", output_port_name='OUT1')
        self.addConnection("clock", "sum1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("oneCt", "sum1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum2", "sum3", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("2JxUFJoTUBjuM0Cz1H6F-208", "sum3", output_port_name='OUT1', input_port_name='IN1')


class FWDEulerIntCalc(CBD):
    def __init__(self, block_name, IC=(0)):
        super().__init__(block_name, input_ports=[], output_ports=['I'])

        # Create the Blocks
        self.addBlock(FWDEulerInt("fwdeulter"))
        self.addBlock(AnalyticFunc("gt"))
        self.addBlock(TimeBlock("time"))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))

        # Create the Connections
        self.addConnection("gt", "fwdeulter", output_port_name='gt', input_port_name='IN1')
        self.addConnection("zeroCt", "fwdeulter", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("fwdeulter", "I", output_port_name='OUT1')
        self.addConnection("time", "gt", output_port_name='OUT1', input_port_name='t')


class TrapezoidIntCalc(CBD):
    def __init__(self, block_name, IC=(0)):
        super().__init__(block_name, input_ports=[], output_ports=['I'])

        # Create the Blocks
        self.addBlock(AnalyticFunc("gt"))
        self.addBlock(TimeBlock("time"))
        self.addBlock(TrapezoidInt("trapezoid"))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))

        # Create the Connections
        self.addConnection("gt", "trapezoid", output_port_name='gt', input_port_name='IN1')
        self.addConnection("zeroCt", "trapezoid", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("trapezoid", "I", output_port_name='OUT1')
        self.addConnection("time", "gt", output_port_name='OUT1', input_port_name='t')


class BWDEulerIntCalc(CBD):
    def __init__(self, block_name, IC=(0)):
        super().__init__(block_name, input_ports=[], output_ports=['I'])

        # Create the Blocks
        self.addBlock(AnalyticFunc("gt"))
        self.addBlock(TimeBlock("time"))
        self.addBlock(BWDEulerInt("bwdeuler"))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))

        # Create the Connections
        self.addConnection("zeroCt", "bwdeuler", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("gt", "bwdeuler", output_port_name='gt', input_port_name='IN1')
        self.addConnection("bwdeuler", "I", output_port_name='OUT1')
        self.addConnection("time", "gt", output_port_name='OUT1', input_port_name='t')


class FWDEulerTest(CBD):
    def __init__(self, block_name, IC=(0)):
        super().__init__(block_name, input_ports=[], output_ports=['I'])

        # Create the Blocks
        self.addBlock(FWDEulerInt("fwdeulter"))
        self.addBlock(AnalyticFunc("gt"))
        self.addBlock(TimeBlock("time"))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))
        self.addBlock(DelayBlock("2JxUFJoTUBjuM0Cz1H6F-303"))
        self.addBlock(AdderBlock("2JxUFJoTUBjuM0Cz1H6F-308", numberOfInputs=(2)))

        # Create the Connections
        self.addConnection("gt", "fwdeulter", output_port_name='gt', input_port_name='IN1')
        self.addConnection("zeroCt", "fwdeulter", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("zeroCt", "2JxUFJoTUBjuM0Cz1H6F-303", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("time", "gt", output_port_name='OUT1', input_port_name='t')
        self.addConnection("2JxUFJoTUBjuM0Cz1H6F-308", "I", output_port_name='OUT1')
        self.addConnection("2JxUFJoTUBjuM0Cz1H6F-308", "2JxUFJoTUBjuM0Cz1H6F-303", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("fwdeulter", "2JxUFJoTUBjuM0Cz1H6F-308", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("2JxUFJoTUBjuM0Cz1H6F-303", "2JxUFJoTUBjuM0Cz1H6F-308", output_port_name='OUT1', input_port_name='IN2')


class AnalyticFuncCalc(CBD):
    def __init__(self, block_name, IC=(0)):
        super().__init__(block_name, input_ports=[], output_ports=['y'])

        # Create the Blocks
        self.addBlock(TimeBlock("time"))
        self.addBlock(AnalyticFunc("gt"))

        # Create the Connections
        self.addConnection("time", "gt", output_port_name='OUT1', input_port_name='t')
        self.addConnection("gt", "y", output_port_name='gt')


class TrapezoidInt(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1', 'IC'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(AdderBlock("sum2", numberOfInputs=(2)))
        self.addBlock(DelayBlock("delay2"))
        self.addBlock(AdderBlock("sum3", numberOfInputs=(2)))
        self.addBlock(ProductBlock("prod2", numberOfInputs=(2)))
        self.addBlock(ProductBlock("prod1", numberOfInputs=(2)))
        self.addBlock(DeltaTBlock("deltaT"))
        self.addBlock(ProductBlock("prod3", numberOfInputs=(2)))
        self.addBlock(InverterBlock("inv"))
        self.addBlock(ConstantBlock("twoCt", value=(2)))
        self.addBlock(ConstantBlock("zeroCt", value=(0)))
        self.addBlock(ProductBlock("prod4", numberOfInputs=(2)))
        self.addBlock(NegatorBlock("neg"))
        self.addBlock(AdderBlock("sum1", numberOfInputs=(2)))
        self.addBlock(DelayBlock("delay1"))

        # Create the Connections
        self.addConnection("IN1", "prod4", input_port_name='IN1')
        self.addConnection("IN1", "sum1", input_port_name='IN2')
        self.addConnection("IN1", "delay1", input_port_name='IN1')
        self.addConnection("IC", "sum3", input_port_name='IN2')
        self.addConnection("sum2", "delay2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum2", "OUT1", output_port_name='OUT1')
        self.addConnection("sum3", "delay2", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("prod4", "neg", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("twoCt", "inv", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("zeroCt", "delay1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("delay1", "sum1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("delay2", "sum2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("prod2", "sum2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("prod3", "prod4", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("neg", "sum3", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum1", "prod1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("prod1", "prod2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("inv", "prod3", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("inv", "prod1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("deltaT", "prod2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("deltaT", "prod3", output_port_name='OUT1', input_port_name='IN1')


