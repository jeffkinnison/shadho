"""
"""


def random_search(domain):
    return domain.rvs() if hasattr(domain, 'rvs') else domain
