DV_POS_MAX: float = 28.0
DV_NEG_MAX: float = 21.0

V_PREF_FALLBACK: float = 1.0
"""If the sampled v_pref <= 0.0, then instead set v_pref = v_pref_fallback. This prevents undesirable negative v_pref values, or Cars with v_pref == 0.0 that would always result in deadlock."""

REFUEL_DELAY_MU: float = 10 * 60  # The Car refuel delay time normal dist. mean in seconds
REFUEL_DELAY_STD: float = 130     # The Car refuel delay time normal dist. standard deviation in seconds
REFUEL_DELAY_MIN: float = 120     # The Car refuel delay time minimum value (clamp) in seconds
