"""Verify that the heursitic should be used before using it.
"""
import shadho


def heuristic_check(heuristic):
    def no_heuristic(*args, **kwargs):
        return None
    try:
        h = heuristic.__name__
        if shadho.config.heuristic[h]:
            return heuristic
    except AttributeError:
        return no_heuristic
