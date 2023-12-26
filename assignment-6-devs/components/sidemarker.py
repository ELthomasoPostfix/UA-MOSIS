from pypdevs.DEVS import AtomicDEVS



class SideMarker(AtomicDEVS):
    """Marks all inputted QueryAcks to have sideways set to true. It also immediately outputs the inputted events.

    This block should be placed in-between the (Q_sack, Q_rack) connection of two RoadSegments if both want to merge onto a third RoadSegment.
    """
    def __init__(self, block_name: str):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        """
        super().__init__(block_name)
