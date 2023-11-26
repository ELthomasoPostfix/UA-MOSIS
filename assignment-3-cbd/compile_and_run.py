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
		),
		Variable(
			type='Real',
			initial='calculated',
			variability='continuous',
			causality='output',
			name="u",
			mapping=[('plant', 'ego_car.u')]
		),
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
        Connection('pid', 'PID.OUT', 'plant', 'u'),
        Connection('plant', 'e', 'pid', 'PID.IN')
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


err = ([r[0] for r in result], [r[1] for r in result])
x_lead = ([r[0] for r in result], [r[2] for r in result])
x_tgt = ([r[0] for r in result], [r[3] for r in result])
u = ([r[0] for r in result], [r[4] for r in result])


plt.plot(x_lead[0], x_lead[1], label="x_lead")
plt.plot(x_tgt[0], x_tgt[1], label="x_tgt")
plt.plot(err[0], err[1], label="err")
plt.show()

# plt.plot(err[0], err[1], label="err")
# plt.plot(u[0], u[1], label="u")
# plt.legend()
# plt.show()

# Plot with two y-axes
fig, ax1 = plt.subplots()
ax1.plot(err[0], err[1], label="x_err", alpha=0.5)

ax2 = ax1.twinx()
ax2.plot(u[0], u[1], label="u", color="orange", linestyle="dotted")

# Combine two legends
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2)
plt.show()

