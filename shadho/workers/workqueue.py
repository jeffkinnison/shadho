"""Utilities for submitting and starting Work Queue workers.


"""
import argparse
import os
import re
import subprocess

from shadho.configuration import ShadhoConfig


def parse_args(args=None):
    p = argparse.ArgumentParser(
        description='Start a Work Queue worker and connect to SHADHO.')

    p.add_argument('-M', '--master', type=str, default='',
        help='name of the Work Queue master to connect to')
    p.add_argument('-u', '--user', type=str, default=os.environ['USER'],
        help='name of the user running the Work Queue master')
    p.add_argument('--timeout', type=int,
        help='amount of time worker idles before exiting')
    p.add_argument('--cores', type=int, default=1,
        help='the number of cores for the worker to use;' +
             ' pass 0 to use all available cores')
    p.add_argument('--feature', type=str, nargs='*', default=[],
        help='user specified feature to advertise, e.g. GPU model name')

    return p.parse_args(args)


def shadho_wq_worker(args=None, config=None):
    """Start a Work Queue worker."""

    if config is None:
        config = ShadhoConfig()

    if args is None:
        cmd_args = ''
    else:
        cmd_args = f'{"-M" if args.master else ""} {args.master} --cores {args.cores}'
        for feature in args.feature:
            cmd_args += f' --feature {feature}'

    if not re.search(r'(^|[\s])-M([\s]|$)', cmd_args):
        cmd_args = ' '.join([cmd_args, '-M', config.workqueue.name]).strip()

    if not re.search(r'[\s]*-M[\s][\S]*' + args.user + r'.*[\s]*', cmd_args):
        print('Replacing')
        cmd_args = re.sub(r'(^|[\s]*)(.*-M[\s])([\S]+)([\s]*.*$)',
                          r'\1\2\3-' + args.user + r'\4',
                          cmd_args)

    executable = os.path.join(config.shadho_dir, 'bin', 'work_queue_worker')

    print(cmd_args)
    subprocess.run([executable] + cmd_args.split(), stderr=subprocess.STDOUT)


def main():
    args = parse_args()
    shadho_wq_worker(args=args)


if __name__ == '__main__':
    main()
