#!/usr/bin/env python

###############################################################
# < next few lines under version control, D O  N O T  E D I T >
# $Date: 2018-03-29 10:12:00 -0400 (Thu, 29 Mar 2018) $
# $Revision: 100014 $
# $Author: Barry.Baker@noaa.gov $
# $Id: nemsio2nc4.py 100014 2018-03-29 14:12:00Z Barry.Baker@noaa.gov $
###############################################################

__author__  = 'Barry Baker'
__email__   = 'Barry.Baker@noaa.gov'
__license__ = 'GPL'

'''
Simple utility to convert nemsio file into a netCDF4 file
Utilizes mkgfsnemsioctl utility from NWPROD and CDO
'''

import os
from glob import glob
import sys
import subprocess
from distutils.spawn import find_executable
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
#try: 
#    import multiprocessing as mp
#    parallel=True
#except ImportError:
#    usedask=False

def execute_subprocess(cmd, verbose=False):
    '''
    call the subprocess command
    :param cmd: command to execute
    :param type: str
    '''
    if verbose:
        print( 'Executing: %s' % cmd)

    try:
        out = subprocess.check_output(cmd,shell=True)
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError('',cmd,output=e.output)
    return


def get_exec_path(exec_name, verbose=False, ctl_path=None):
    '''
    get the full path to a given executable name
    :param exec_name: executable to fine
    :param type: str
    '''
    if ctl_path is not None:
        exec_path_def = ctl_path
    else:
        exec_path_def = '/gpfs/dell2/emc/modeling/noscrub/Barry.Baker/global-workflow.gefs/exec/%s' % exec_name

    exec_path = find_executable(exec_name)
    if exec_path is None:
        exec_path = exec_path_def

    if verbose:
        print( '%s: %s' % (exec_name, exec_path))

    return exec_path

def chdir(fname):
    dir_path = os.path.dirname(os.path.realpath(fname))
    os.chdir(dir_path)
    return os.path.basename(fname)


def change_file(finput,verbose=False, ctl=None):
    fname = finput.strip('.nemsio') if finput.endswith('.nemsio') else finput
    fname = chdir(finput)
    if ctl is None:
        mkgfsnemsioctl = get_exec_path('mkgfsnemsioctl', verbose=verbose)
    else:
        mkgfsnemsioctl = ctl
    cdo = get_exec_path('cdo', verbose=verbose)

    cmd = '%s %s' % (mkgfsnemsioctl, fname)
    execute_subprocess(cmd, verbose=verbose)

    cmd = '%s -f nc4 import_binary %s.ctl %s.nc4' % (cdo, fname, fname)
    execute_subprocess(cmd, verbose=verbose)


if __name__ == '__main__':

    parser = ArgumentParser(description='convert nemsio file to netCDF4 file', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--files', help='input nemsio file name', type=str, required=True)
    #parser.add_argument('-n', '--nprocs', help='Number of Processors', type=int, required=False, default=2)
    parser.add_argument('-v', '--verbose', help='print debugging information', action='store_true', required=False)
    parser.add_argument('-c', '--ctl', help='Location of the grads control file to use', default=None)
    args = parser.parse_args()
    
    finput = args.files
    verbose = args.verbose
    #nprocs = args.nprocs

    files = sorted(glob(finput))
    for i,j in enumerate(files):
        files[i] = os.path.realpath(j)
    if len(files) == 1:
        finput = files[0]
        change_file(finput,verbose=verbose, ctl=args.ctl)
    else:
        realfiles = []
        for finput in files:
            if finput.endswith('.nemsio'):
                realfiles.append(finput)
        for finput in realfiles:
            change_file(finput,verbose=verbose, ctl=args.ctl)
   
