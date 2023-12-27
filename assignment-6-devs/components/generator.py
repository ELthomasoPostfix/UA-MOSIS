import uuid

from pypdevs.DEVS import AtomicDEVS



class Generator(AtomicDEVS):
    """Periodically generates Cars. This component allows cars to enter the system.
    The inter-arrival time (IAT) for the Cars is given by a uniform distribution.
    Upon generation, each car is given a preferred velocity v_pref by sampling from a normal distribution.

    When a Car is generated, a Query is sent over the Q_send port. As soon as a QueryAck is received,
    the generated car is output over the car_out port. Next, the Generator waits for some time before generating another Car.
    Upon generation, the Car's no_gas is randomly set to be either true or false.
    """
    def __init__(self, block_name: str, IAT_min: float, IAT_max: float,
                 v_pref_mu: float, v_pref_sigma: float, destinations: list, limit: int):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        :param IAT_min: Lower bound for the IAT uniform distribution.
        :param IAT_max: Upper bound for the IAT uniform distribution.
        :param v_pref_mu: Mean of the normal distribution that is used to sample v_pref.
        :param v_pref_sigma: Standard deviation of the normal distribution that is used to sample v_pref.
        :param destinations: A non-empty list of potential (string) destinations for the Cars. A random destination will be selected.
        :param limit: Upper limit of the number of Cars to generate.
        """
        super().__init__(block_name)
