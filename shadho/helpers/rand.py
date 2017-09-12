import scipy.stats


# Uniform distribution
def uniform(lo, hi):
    return {
        'domain': {
            'distribution': 'uniform',
            'args': (),
            'kwargs': {'loc': lo, 'scale': hi},
        },
        'scaling': 'linear',
        'strategy': 'random'
    }


def ln_uniform(lo, hi):
    return {
        'domain': {
            'distribution': 'uniform',
            'args': (),
            'kwargs': {'loc': lo, 'scale': hi},
        },
        'scaling': 'ln',
        'strategy': 'random'
    }


def log10_uniform(lo, hi):
    return {
        'domain': {
            'distribution': 'uniform',
            'args': (),
            'kwargs': {'loc': lo, 'scale': hi},
        },
        'scaling': 'log_10',
        'strategy': 'random'
    }


def log2_uniform(lo, hi):
    return {
        'domain': {
            'distribution': 'uniform',
            'args': (),
            'kwargs': {'loc': lo, 'scale': hi},
        },
        'scaling': 'log_2',
        'strategy': 'random'
    }


# Normal distribution
def normal(mu, sigma):
    return {
        'domain': {
            'distribution': 'norm',
            'args': (),
            'kwargs': {'loc': mu, 'scale': sigma},
        },
        'scaling': 'linear',
        'strategy': 'random'
    }


def ln_normal(mu, sigma):
    return {
        'domain': {
            'distribution': 'norm',
            'args': (),
            'kwargs': {'loc': mu, 'scale': sigma},
        },
        'scaling': 'ln',
        'strategy': 'random'
    }


def log10_normal(mu, sigma):
    return {
        'domain': {
            'distribution': 'norm',
            'args': (),
            'kwargs': {'loc': mu, 'scale': sigma},
        },
        'scaling': 'log_10',
        'strategy': 'random'
    }


def log2_normal(mu, sigma):
    return {
        'domain': {
            'distribution': 'norm',
            'args': (),
            'kwargs': {'loc': mu, 'scale': sigma},
        },
        'scaling': 'log_2',
        'strategy': 'random'
    }


# Randint distributions
def randint(lo, hi):
    return {
        'domain': list(range(lo, hi)),
        'scaling': 'linear',
        'strategy': 'random'
    }


# Choice
def choice(choices):
    return {
        'domain': list(choices) if isinstance(choices, (list, tuple, set)) else [choices],
        'scaling': 'linear',
        'strategy': 'random'
    }
