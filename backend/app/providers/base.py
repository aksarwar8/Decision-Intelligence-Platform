"""Contract shared by demand data providers."""
from typing import Protocol
import pandas as pd

class DemandProvider(Protocol):
    name: str
    def load(self, *, item_id: str, store_id: str) -> pd.DataFrame:
        """Return canonical date/product_id/market/demand rows."""
        ...
