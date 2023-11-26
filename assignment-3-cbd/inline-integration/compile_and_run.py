from fmpy import simulate_fmu
from fmpy.fmucontainer import create_fmu_container, Connection, Configuration, Component, Variable
from fmpy.validation import validate_fmu
from fmpy.util import compile_platform_binary
from fmpy.model_description import DefaultExperiment

import matplotlib.pyplot as plt


FMU_DIR = "fmu-outputs/"


def combineFMU():
	problems = validate_fmu(f"{FMU_DIR}PID.fmu")
	if not problems:
		compile_platform_binary(f"{FMU_DIR}PID.fmu")
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
				filename=f'{FMU_DIR}Plant.fmu',
				name='plant'
			),
			Component(
				filename=f'{FMU_DIR}PID.fmu',
				name='pid'
			)
		],
		connections=[
			Connection('pid', 'PID.OUT', 'plant', 'u'),
			Connection('plant', 'e', 'pid', 'PID.IN')
		]
	)

	create_fmu_container(configuration, f"{FMU_DIR}Container.fmu")

	problems = validate_fmu(f"{FMU_DIR}Container.fmu")
	if problems:
		print("PROBLEMS ENCOUNTERED WITH COMBINED FMU:")
		print(problems)
		exit()


def simulateFMU(name, duration, step_size, debug_logging=False, fmi_call_logger=None):
	return simulate_fmu(
		name,
		stop_time=duration,
		output_interval=step_size,
		debug_logging=debug_logging,
		fmi_call_logger=fmi_call_logger
	)


def plotResults(x_lead, x_tgt, err, u):
	plt.plot(x_lead[0], x_lead[1], label="Lead Car position (x_lead)")
	plt.plot(x_tgt[0], x_tgt[1], label="Target Car position (x_tgt)")
	plt.plot(err[0], err[1], label="Error (x_err)")

	plt.xlabel("Time (s)")
	plt.ylabel("Position (m)")

	plt.title("FMU Target Car Movement")

	# Horizontal grid
	plt.grid(axis="y")

	plt.legend()
	plt.tight_layout()

	plt.savefig("graphs/target-movement.png")
	plt.show()

	# Plot with two y-axes
	fig, ax1 = plt.subplots()


	ax1.axhline(y=0, color="black", linestyle="dotted", linewidth=0.5, alpha=0.5)

	ax1.plot(err[0], err[1], label="Error (x_err)", alpha=0.5, linewidth=2)
	ax1.set_xlabel("Time (s)")
	ax1.set_ylabel("Error desired distance (m)")

	ax2 = ax1.twinx()
	ax2.plot(u[0], u[1], label="Control signal (u)", color="#516C7F", linestyle="dotted")

	ax2.set_ylabel("Control signal (u)")




	# Combine two legends
	lines, labels = ax1.get_legend_handles_labels()
	lines2, labels2 = ax2.get_legend_handles_labels()
	ax2.legend(lines + lines2, labels + labels2)

	plt.tight_layout()

	plt.savefig("graphs/error-control.png")
	plt.show()



def getFMUData(results):
	# Get each column as a list
	columns = [results[name] for name in results.dtype.names]
	# return [(columns[0], col) for col in columns[1:]]
	return { name: (columns[0], col) for name, col in zip(results.dtype.names[1:], columns[1:]) }


if __name__ == "__main__":
	# combineFMU()
	result = simulateFMU(f"{FMU_DIR}Container.fmu", 70, 0.01)

	data = getFMUData(result)
	x_lead, x_tgt, err, u = data["x_ego"], data["x_tgt"], data["x_err"], data["u"]


	plotResults(x_lead, x_tgt, err, u)
