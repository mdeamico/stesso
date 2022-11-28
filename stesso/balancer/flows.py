class Flows():
    """Track inflows and outflows of a network part (link or node)."""
    def __init__(self, key) -> None:
        self.key = key

        self.inflows: list = []
        self.outflows: list = []
