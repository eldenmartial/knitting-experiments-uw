import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser()

parser.add_argument('-k', '--knitout_path', type=str, help='', default='knitout-files/')

parser.add_argument('-m', '--masses_path', type=str, help='directory containing the masses', default='masses-auto/')

parser.add_argument('-o', '--out_path', type=str, help='path to write output file to', required=True)

parser.add_argument('-n', '--normalize', action='store_true')

parser.add_argument('-x', '--xclude_files', nargs='+', default=['test1.k','test2.k','test3.k','test4.k','test5.k','test6.k','test7.k','test8.k','test9.k','test10.k','test11.k']) 

parser.add_argument('-s', '--swatch_flag', type=str, help='flag at begin of comments to indicate new swatch (if there are multiple swatches in the file)', default=';begin swatch:')


parser.add_argument('--machine', type=str, help='knitting machine model', default='swgn2')

parser.add_argument('-c','--carriers', nargs='+', help='carriers to parse knitout for', default=['1']) #[] means parse for all

# parser.add_argument('--neighbors', action='store_true')


args = parser.parse_args()

p_args = ['-m', args.machine, '-s', args.swatch_flag, '--masses_path', args.masses_path]

out_path = os.path.normpath(args.out_path)

p_args.extend(['-o', out_path])
subprocess.run(['rm', '-rf', out_path])


if len(args.carriers): p_args.extend(['-c', ' '.join(args.carriers)])

if args.normalize: p_args.append('-n')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def fmt(msg, msg_type='Error'):
    if msg_type == 'Error':
        return "\033[0;31m%s\033[0m" % msg
    elif msg_type == 'Exception':
        return "\033[91m%s\033[0m" % msg
    elif msg_type == 'Warning':
        return "\033[93m%s\033[0m" % msg
        pass
    elif msg_type is None:
        return msg
    else: return "\033[0;32m%s\033[0m" % msg


def execute(cmd):
    msg_type = None
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    for ln in iter(popen.stdout.readline, ""):
        yield ln
    
    for ln in iter(popen.stderr.readline, ""):
        if not ln.startswith(' '):
            if 'Warning' in ln: msg_type = 'Warning'
            elif 'Exception' in ln: msg_type = 'Exception'
            elif 'Error' in ln: msg_type = 'Error'
            else: msg_type = None
        yield fmt(ln, msg_type)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code: raise subprocess.CalledProcessError(return_code, cmd)


files = os.listdir(args.knitout_path)

for i, file in enumerate(files):
    if file.endswith('.k') and not file in args.xclude_files:
        print(file, f'({i+1}/{len(files)})')
        print('-' * len(file))

        cmd = ['python', 'kParser.py', '-k', os.path.join(args.knitout_path, file)] + p_args

        try:
            for path in execute(cmd):
                print(path, end="")
        except subprocess.CalledProcessError as e:
            print(fmt(f'(at file {file}) subprocess.CalledProcessError: returned non-zero exit status 1.', msg_type='Error'))
            sys.exit(1)

    else: print(f'skipping {file}.')

print('done.')
