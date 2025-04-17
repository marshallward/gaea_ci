#!/usr/bin/env python
import collections
import errno
import filecmp
import os
import shlex
import shutil
import subprocess
import time

import f90nml

#NPROCS_MAX = 576
NPROCS_MAX = 480
#NPROCS_MAX = 64
#NPROCS_MAX = 32
#NPROCS_MAX = 1
OVERRIDE = False

verbose = True
override_fname = 'MOM_override_global'
DOC_LAYOUT = 'MOM_parameter_doc.layout'
TEST_MODE = 'repro'
#TEST_MODE = 'debug' # NOTE: debug and repro may have different answers!

def regressions():
    base_path = os.getcwd()
    regressions_path = os.path.join(base_path, 'regressions')
    regression_tests = get_regression_tests(regressions_path)

    override_path = os.path.join(base_path, override_fname)
    use_override = OVERRIDE and os.path.isfile(override_fname)

    # Check output
    if (verbose):
        for compiler in ('gnu',):
            print('{}: ['.format(compiler))
            for config in regression_tests[compiler]:
                print('    {}:'.format(config))
                for reg, test in regression_tests[compiler][config]:
                    print('        {}'.format(reg))
                    print('        {}'.format(test))
            print(']')

    n_tests = sum(len(t) for t in regression_tests['gnu'].values())
    print('Number of tests: {}'.format(n_tests))

    # Set up the scheduler
    n_nodes = int(os.environ['SLURM_JOB_NUM_NODES'])
    n_cores_per_node = int(os.environ['SLURM_CPUS_ON_NODE'])
    n_max_cores = n_nodes * n_cores_per_node

    # Track the number of active cores, and only submit the next job will
    # fit in the queue (aka the world's dumbest scheduler)
    n_running = 0

    for compiler in ('gnu',):
    #for compiler in ('gnu', 'intel', 'pgi'):
    #for compiler in ('pgi',):
        # TODO: static, [no]symmetric, etc
        for mode in (TEST_MODE,):
            running_tests = []
            for config in regression_tests[compiler]:
                for reg_path, test_path in regression_tests[compiler][config]:
                    test = RegressionTest()
                    test.refpath = reg_path
                    test.runpath = test_path

                    prefix = os.path.join(base_path, 'regressions', config)
                    test.name = reg_path[len(prefix + os.sep):]

                    mom_layout_path = os.path.join(test.runpath, 'MOM_layout')
                    if os.path.isfile(mom_layout_path):
                        layout_params = parse_mom6_param(mom_layout_path)
                        layout = layout_params['LAYOUT']
                        ocean_ni, ocean_nj = (int(n) for n in layout.split(','))

                        masktable = layout_params.get('MASKTABLE')
                        if masktable:
                            n_mask = int(masktable.split('.')[1])
                        else:
                            n_mask = 0
                    else:
                        layout_path = os.path.join(test.runpath, DOC_LAYOUT)
                        params = parse_mom6_param(layout_path)

                        # If a run crashes, its proc count may be incorrect
                        # TODO: Re-checkout the files?
                        if not any(p in params for p in ('NIPROC', 'NJPROC')):
                            print('ERROR: {} missing CPU layout'.format(test.name))
                            continue

                        ocean_ni = int(params['NIPROC'])
                        ocean_nj = int(params['NJPROC'])

                        n_mask = 0

                    input_nml_path = os.path.join(test.runpath, 'input.nml')
                    input_nml = f90nml.read(input_nml_path)

                    # Set up a global override for testing across experiments
                    if use_override:
                        local_override_path = os.path.join(test.runpath, OVERRIDE)
                        if not os.path.islink(local_override_path):
                            os.symlink(override_path, local_override_path)

                    # Add the global override to the list of parameters
                    param_fnames = input_nml['MOM_input_nml']['parameter_filename']
                    if OVERRIDE and not override_fname in param_fnames:
                        print('{}: Updating input.nml...'.format(test.name))
                        param_fnames.append(OVERRIDE)
                        input_nml.write(input_nml_path, force=True)

                    # Assume that unset atmos PEs are zero, but verify the
                    # ocean PEs from MOM_input or layout
                    coupler_nml = input_nml.get('coupler_nml', {})
                    atmos_npes = coupler_nml.get('atmos_npes', 0)
                    ocean_npes = coupler_nml.get('ocean_npes')

                    if ocean_npes:
                        assert(ocean_npes == ocean_ni * ocean_nj)
                    else:
                        ocean_npes = ocean_ni * ocean_nj

                    test.nprocs = (ocean_npes - n_mask) + atmos_npes
                    test.nnodes = (test.nprocs + n_cores_per_node - 1) // n_cores_per_node

                    print('{}: {} ({}x{})'.format(test.name, test.nprocs, ocean_ni, ocean_nj))

                    for grid in ('dynamic_symmetric', ):
                        # OBC tests require symmetric grids
                        if (os.path.basename(test_path) == 'circle_obcs' and
                                grid != 'dynamic_symmetric'):
                            continue

                        exe_path = os.path.join(
                            base_path, 'MOM6-examples', 'build', compiler,
                            mode, grid, config, 'MOM6'
                        )

                        # TODO: Replace with node test
                        if test.nprocs > NPROCS_MAX:
                            print('{}: skipping {} ({} ranks)'.format(
                                compiler, test.name, test.nprocs
                            ))
                            continue

                        # Set up output directories
                        # TODO: Ditch logpath, keep paths to stats file
                        test.logpath = os.path.join(
                            base_path, 'output', config, grid, test.name
                        )
                        mkdir_p(test.logpath)

                        stdout_path = os.path.join(test.logpath, compiler + '.out')
                        stderr_path = os.path.join(test.logpath, compiler + '.err')

                        test.stdout = open(stdout_path, 'w')
                        test.stderr = open(stderr_path, 'w')

                        # FMS requires an existing RESTART directory
                        os.chdir(test_path)
                        mkdir_p('RESTART')

                        # Stage the Slurm command
                        srun_flags = ' '.join([
                            '--ntasks {}'.format(test.nprocs),
                            '-mblock',
                            #'--exclusive',
                            #'--mem-per-cpu=16g',
                            '--overlap',
                            '--exact',
                            #'--cpus-per-task={}'.format(test.nprocs),
                            #'--cpu-bind=cores',
                            #'--ntasks-per-core=1',
                            #'--overcommit',
                            #'--mem-per-cpu=2G',
                        ])

                        cmd = '{launcher} {flags} {exe}'.format(
                            launcher='srun',
                            flags=srun_flags,
                            exe=exe_path
                        )

                        # Try a modified environment variable (openmp?)
                        my_env = os.environ.copy()
                        my_env['OMP_NUM_THREADS'] = '1'
                        my_env['KMP_STACKSIZE'] = '512m'
                        my_env['NC_BLKSZ'] = '1M'

                        while n_running + test.nnodes > n_nodes:
                            # Check jobs and update n_running
                            # TODO: Add a timeout counter?
                            n_running = 0
                            print(20*'=')
                            for job in running_tests:
                                if job.process.poll() is None:
                                    print('waiting on {}'.format(job.name))
                                    n_running += job.nnodes

                            print('Running nodes: {}'.format(n_running))
                            time.sleep(10)

                            os.system('ps | grep MOM6 | egrep -v srun | wc -l')

                        if (verbose):
                            print('    Starting {}...'.format(test.name))
                            print(cmd)

                        proc = subprocess.Popen(
                            shlex.split(cmd),
                            stdout=test.stdout,
                            stderr=test.stderr,
                            env=my_env,
                        )
                        test.process = proc
                        n_running += test.nnodes

                        if (verbose):
                            print('    n_running: {}'.format(n_running))

                        running_tests.append(test)

            print('{}: Running {} tests.'.format(compiler, len(running_tests)))

            jobs_are_running = True
            while jobs_are_running:
                # Update job status
                jobs_are_running = False
                for job in running_tests:
                    if job.process.poll() is None:
                        print('waiting on {}...'.format(job.name))
                        jobs_are_running = True

                if jobs_are_running:
                    print(20 * '-')

                time.sleep(10)

            # Wait for processes to complete
            # TODO: Cycle through and check them all, not just the first slow one
            # XXX: The previous block should make this redundant
            for test in running_tests:
                test.process.wait()

            # Check if any runs exited with an error
            if all(test.process.returncode == 0 for test in running_tests):
                print('{}: Tests finished, no errors!'.format(compiler))
            else:
                for test in running_tests:
                    if test.process.returncode != 0:
                        print('{}: Test {} failed with code {}'.format(
                            compiler, test.name, test.process.returncode
                        ))

            # Process cleanup
            # TODO: Make a class method
            for test in running_tests:
                # Store the stats files
                stat_files = [
                   f for f in os.listdir(test.runpath)
                   if f.endswith('.stats')
                ]
                for fname in stat_files:
                    src = os.path.join(test.runpath, fname)
                    dst = os.path.join(test.logpath, fname) + '.' + compiler
                    shutil.copy(src, dst)

                    # Add to logs
                    test.stats.append(dst)

                test.stdout.close()
                test.stderr.close()

            # Compare stats to reference
            test_results = {}
            for test in running_tests:
                test_results[test.name] = test.check_stats()

            if any(result == False for result in test_results.values()):
                for test in test_results:
                    if test_results[test] == False:
                        print('FAIL: {}'.format(test))
            else:
                print('{}: No regressions, test passed!'.format(compiler))


def get_regression_tests(reg_path, test_dirname='MOM6-examples'):
    regression_tests = {}

    model_configs = os.listdir(reg_path)
    for config in model_configs:
        config_path = os.path.join(reg_path, config)
        for path, _, files in os.walk(config_path):
            # TODO: symmetric and static support
            compilers = tuple(
                os.path.splitext(f)[1].lstrip('.')
                for f in files if f.startswith('ocean.stats')
            )
            if compilers:
                reg_dirname = os.path.basename(reg_path.rstrip(os.sep))
                r_s = path.index(reg_dirname)
                r_e = r_s + len(reg_dirname)
                test_path = path[:r_s] + test_dirname + path[r_e:]

                for compiler in compilers:
                    if not compiler in regression_tests:
                        regression_tests[compiler] = collections.defaultdict(list)

                    test_record = path, test_path
                    regression_tests[compiler][config].append(test_record)

    return regression_tests


def parse_mom6_param(path):
    params = {}
    with open(path) as param_file:
        for line in param_file:
            param_stmt = line.split('!')[0].strip()
            if param_stmt:
                key, val = [s.strip() for s in param_stmt.split('=')]
                params[key] = val
    return params


def mkdir_p(path):
    try:
        os.makedirs(path)
    except EnvironmentError as exc:
        if exc.errno != errno.EEXIST:
            raise


class RegressionTest(object):
    def __init__(self):
        self.runpath = None
        self.logpath = None
        self.refpath = None

        self.stats = []

        self.process = None

        self.stdout = None
        self.stderr = None

    def check_stats(self):
        """Compare test stat results with regressions."""

        ref_stats = [
            os.path.join(self.refpath, os.path.basename(stat))
            for stat in self.stats
        ]

        if self.stats:
            match = all(
                filecmp.cmp(ref, stat)
                for ref, stat in zip(ref_stats, self.stats)
            )
        else:
            match = False

        return match


if __name__ == '__main__':
    regressions()
