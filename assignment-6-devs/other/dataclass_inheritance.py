from dataclasses import dataclass, field, InitVar
from typing import List


@dataclass
class Base:
    base_name: str = "base"


@dataclass
class Derived(Base):
    list_len: InitVar[int | None] = None
    derived_name: str = "derived"
    l: List[int] = field(init=False)

    def __post_init__(self, ll):
        ll = ll if ll  is not None else 0 
        self.l = [i for i in range(ll)]



d1 = Derived(list_len=3)
d2 = Derived()

print(d1)
print("==> manual member access: ", d1.base_name, d1.derived_name, d1.l)
print(d2)
