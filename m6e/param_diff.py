#!/usr/bin/env python
import collections
import itertools
import os
import sys


def report_param_diff():
    lpath, rpath = sys.argv[1:3]

    old_keys = collections.defaultdict(set)
    new_keys = collections.defaultdict(set)

    param_left = collections.defaultdict(dict)
    param_right = collections.defaultdict(dict)


    # TODO: Verify filenames?  git mangles the temp filename...
    filename = os.path.basename(rpath)

    if not filename.startswith('MOM_parameter_doc.'):
        return

    pfile = filename.split('.')[1]

    lpar = parse_param(lpath)
    rpar = parse_param(rpath)

    param_left[pfile].update(lpar)
    param_right[pfile].update(rpar)

    # NOTE: We might not need these anymore, could generate from param?
    old_keys[pfile].update(param_left[pfile].keys())
    new_keys[pfile].update(param_right[pfile].keys())

    for pfile in old_keys:
        added_params = new_keys[pfile] - old_keys[pfile]
        removed_params = old_keys[pfile] - new_keys[pfile]
        common_params = old_keys[pfile] & new_keys[pfile]

        if added_params:
            print("\nAdded to MOM_parameter_doc.{}:".format(pfile))
            for param in added_params:
                print("    - {}".format(param))

        if removed_params:
            print("\nRemoved from MOM_parameter_doc.{}:".format(pfile))
            for param in removed_params:
                print("    - {}".format(param))

        if any(
            param_left[pfile][param]['value'] != param_right[pfile][param]['value']
            for param in common_params
        ):
            print("\nChanged values in MOM_parameter_doc.{}:".format(pfile))
            for param in common_params:
                lvalue = param_left[pfile][param]['value']
                rvalue = param_right[pfile][param]['value']
                if lvalue != rvalue:
                    print("    - {}: {} -> {}".format(param, lvalue, rvalue))

        if any(
            param_left[pfile][param]['desc'] != param_right[pfile][param]['desc']
            for param in common_params
        ):
            print("\nChanged descriptions in MOM_parameter_doc.{}".format(pfile))
            for param in common_params:
                ldesc = param_left[pfile][param]['desc']
                rdesc = param_right[pfile][param]['desc']
                if ldesc != rdesc:
                    print('    - {}:'.format(param))
                    print('<-- |' + '\n    |'.join(ldesc))
                    print('--> |' + '\n    |'.join(rdesc))


def parse_param(path):
    parameters = {}

    current_module = None
    current_param = None
    current_group = None

    with open(path) as param_file:
        for line_number, rline in enumerate(param_file):
            line = rline.rstrip('\n')

            # Skip blank lines
            if not line:
                continue

            # Update the module status
            if line.startswith('! ==='):
                assert line[:13] == '! === module '
                current_module = line[13:-4]
                continue

            # Update the current group (if any)
            # TODO: We don't use this info, will need to do it later!
            if line.endswith('%'):
                # TODO: comments? endlines?  what are the rules here?
                current_group = line.rstrip('%')
                continue

            # Clear the group on exit
            if line.startswith('%'):
                assert(line[1:] == current_group)
                current_group = None
                continue

            try:
                expr, cmt = line.split('!', 1)
            except ValueError:
                print(path)
                print(repr(line))
                raise

            if expr.rstrip():
                pname, _, pval = expr.strip().split(None, 2)

                # Build the parameter entry
                param = {}
                param['line'] = line_number
                param['value'] = pval
                param['desc'] = []
                param['module'] = current_module

                parameters[pname] = param
                current_param = param

            if cmt and current_param:
                current_param['desc'].append(cmt)

    return parameters


if __name__ == '__main__':
    report_param_diff()
