from fmpy import simulate_fmu
from fmpy.fmucontainer import create_fmu_container, Connection, Configuration, Component, Variable
from fmpy.validation import validate_fmu
from fmpy.util import compile_platform_binary
from fmpy.model_description import DefaultExperiment

problems = validate_fmu("PID.fmu")
if not problems:
	compile_platform_binary("PID.fmu")
else:
	print("PROBLEMS ENCOUNTERED WITH PID FMU:")
	print(problems)
	exit()

configuration = Configuration(
    fmiVersion='2.0',
	defaultExperiment=DefaultExperiment(
	            startTime='0',
	            stopTime='70',
	            tolerance='1e-7',
	            stepSize='0.01'
	        ),
	parallelDoStep=False,
	variables = [
		Variable(
			type='Real',
			initial='calculated',
			variability='continuous',
			causality='output',
			name='x_err',
			mapping=[('plant', 'e')]
		),
		Variable(
			type='Real',
			initial='calculated',
			variability='continuous',
			causality='output',
			name='x_tgt',
			mapping=[('plant', 'forward_car.y')]
		),
		Variable(
			type='Real',
			initial='calculated',
			variability='continuous',
			causality='output',
			name='x_ego',
			mapping=[('plant', 'ego_car.y')]
		)
	],
	components=[
		Component(
            filename='Plant.fmu',
            name='plant'
        ),
        Component(
            filename='PID.fmu',
            name='pid'
        )
    ],
    connections=[
        Connection('pid', 'PID_OUT', 'plant', 'u'),
        Connection('plant', 'e', 'pid', 'PID_IN')
    ]
)

create_fmu_container(configuration, "Container.fmu")
problems = validate_fmu("Container.fmu")
if problems:
	print("PROBLEMS ENCOUNTERED WITH COMBINED FMU:")
	print(problems)
	exit()

result = simulate_fmu("Container.fmu",
                      # debug_logging=True,
                      # fmi_call_logger=print,
                      stop_time=70, output_interval=0.01)


import matplotlib.pyplot as plt

plt.plot([r[0] for r in result], [r[1] for r in result], label="x_err")
plt.plot([r[0] for r in result], [r[2] for r in result], label="x_tgt")
plt.plot([r[0] for r in result], [r[3] for r in result], label="x_ego")
plt.legend()
plt.show()

