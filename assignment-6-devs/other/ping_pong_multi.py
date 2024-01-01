from dataclasses import dataclass, field
from typing import List, Tuple

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import *



@dataclass
class PingPongMultiState:
	items_queue: List[Tuple[Query, float]] = field(default_factory=list)
	"""The list of items to ping pong. Every item must wait for the same pong_delay before after entry."""
	trace: str = field(default_factory=str)
	"""A trace of the changes applied by the `_update_timers(float)` method to the items queue."""
	rem_x_inf: int = 0
	"""The first X Queries that come in via extTransition will result in a QueryAck with t_until_dep = INFINITY instead of the designated t_until_dep value."""

	def __repr__(self) -> str:
		return f"""PingPongMultiState(
			items_queue  = {self.items_queue})"""

class PingPongMulti(AtomicDEVS):
	def __init__(self, name, t_until_dep: float = 0.0, pong_delay: float = 0.2, first_x_inf: int = 0, do_max: bool = False):
		super(PingPongMulti, self).__init__(name)
		self.t_until_dep: float = t_until_dep
		self.pong_delay: float = pong_delay

		self.state = PingPongMultiState()

		# Immutable members
		self.FIRST_X_INF: float = first_x_inf
		"""A constant value to reset the rem_x_inf state member."""
		self.DO_MAX: bool = do_max
		"""Whether the max function should be used after decrementing Query pong timers using elapsed time, to clamp the pong timer value to 0.0"""

		# Update initial state
		self.state.rem_x_inf = self.FIRST_X_INF

		# ports
		self.inp = self.addInPort("inp")
		self.out = self.addOutPort("out")

	def timeAdvance(self):
		if len(self.state.items_queue) == 0:
			return INFINITY

		assert self.state.items_queue[0][1] >= 0.0, f"""=== Trace ===

{self.state.trace}
"""
		return self.state.items_queue[0][1]

	def extTransition(self, inputs):
		# TODO If do_max is set to True, then timeAdvance() never returns negative values !!!
		self._update_timers(self.elapsed, do_max=self.DO_MAX)

		if self.inp in inputs:
			self.state.items_queue.append((inputs[self.inp], self.pong_delay))

		return self.state

	def outputFnc(self):
		if len(self.state.items_queue) > 0:
			t_until_dep_out: float = self.t_until_dep if self.state.rem_x_inf <= 0 else INFINITY
			return {
				self.out: QueryAck(self.state.items_queue[0][0].ID, t_until_dep_out)
			}
		return {}

	def intTransition(self):
		self._update_timers(self.timeAdvance())

		self.state.items_queue.pop(0)
		self.state.rem_x_inf = max(0, self.state.rem_x_inf - 1)
		return self.state

	def _update_timers(self, time_delta: float, do_max: bool = False) -> None:
		# If do_max False, ignore the 0.0
		# If do_max True, then take max of 0.0 and x
		max_func = max if do_max else lambda _, x: x

		pre = self.state.items_queue
		self.state.items_queue = [
			(query, max_func(0.0, delay - time_delta))
			for query, delay in self.state.items_queue
		]

		self._add_trace_entry(time_delta, pre)

	def _add_trace_entry(self, time_delta: float, pre_list: List[Tuple[Query, float]] = None) -> None:
		pre_str: str = "" if pre_list is None else\
			("\n\t" + str(pre_list))
		self.state.trace += f"\n== time delta : {time_delta} ==" + pre_str + "\n\t" + str(self.state.items_queue)
