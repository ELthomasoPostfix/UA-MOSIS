from pypdevs.DEVS import AtomicDEVS



class Collector(AtomicDEVS):
    """Collects Cars from the simulation and stores all important information such that statistics can be computed afterwards."""
    def __init__(self, block_name: str):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(Collector, self).__init__(block_name)
