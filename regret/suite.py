"""Interface to the MOM6 regression test suite."""

class RegressionTests(object):
    def __init__(self):
        self.references
        self.tests

    def find_references(self, path):
        """Gather available regression tests based on directory tree.

        Current directory tree for references is as follows:
        - configuration (ocean_only, ice_ocean_SIS2, etc.)
            - experiment (double_gyre, etc)
                - subclasses of experiments (BML, KPP, etc.)
                    - Results: {ocean,seaice}.stats.${compiler}
                      (ocean.stats.gnu, ocean.stats.intel, etc)

        We parse this directory tree to find relevant tests.
        """

        # XXX: Redundant?
        base_path = os.path.abspath(path)

        for path, _, files in os.walk(path):
            # Find directories with ocean.stats.* files
            compilers = tuple(
                os.path.splitext(f)[1].lstrip('.')
                for f in files if f.startswith('ocean.stats')
            )

