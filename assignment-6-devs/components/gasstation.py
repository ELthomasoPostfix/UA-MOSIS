from pypdevs.DEVS import AtomicDEVS



class GasStation(AtomicDEVS):
    """Represents the notion that some Cars need gas. It can store an infinite amount of Cars,
    who stay for a certain delay inside an internal queue.
    
    This component can be available (default) or unavailable
    """
    def __init__(self, block_name: str, observ_delay: float):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        :param observ_delay: The interval at which the GasStation must poll if the received QueryAck has an infinite delay.
        """
        super(GasStation, self).__init__(block_name)
