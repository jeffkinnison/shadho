from shadho.scaling import linear, ln, log_10, log_2

from pyrameter import ContinuousDomain, DiscreteDomain
import scipy.stats


# Uniform distribution
def uniform(lo, hi):
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi,
                            callback=linear)


def ln_uniform(lo, hi):
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi, callback=ln)


def log10_uniform(lo, hi):
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi,
                            callback=log_10)


def log2_uniform(lo, hi):
    return ContinuousDomain(scipy.stats.uniform, loc=lo, scale=hi,
                            callback=log_2)


# Normal distribution
def normal(mu, sigma):
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi,
                            callback=linear)


def ln_normal(mu, sigma):
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi, callback=ln)


def log10_normal(mu, sigma):
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi,
                            callback=log_10)


def log2_normal(mu, sigma):
    return ContinuousDomain(scipy.stats.norm, loc=lo, scale=hi,
                            callback=log_2)


# Randint distributions
def randint(lo, hi, step=1):
    return DiscreteDomain(list(range(lo, hi, step)))


def ln_randint(lo, hi, step=1):
    return DiscreteDomain([ln(i) for i in range(lo, hi, step)])


def log10_randint(lo, hi, step=1):
    return DiscreteDomain([log_10(i) for i in range(lo, hi, step)])


def log2_randint(lo, hi, step=1):
    return DiscreteDomain([log2(i) for i in range(lo, hi, step)])


# Choice
def choice(choices):
    return DiscreteDomain(choices)
