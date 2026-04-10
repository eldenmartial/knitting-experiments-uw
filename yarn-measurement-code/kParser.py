import argparse
import io
import os
import regex
import warnings

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument('-k', '--knitout_path', type=str, help='input knitout file path', required=True)
parser.add_argument('-m', '--machine', type=str, help='knitting machine model', default='swgn2')
parser.add_argument('-c','--carriers', nargs='+', help='carriers to parse knitout for', default=[]) #[] means parse for all

parser.add_argument('-s', '--swatch_flag', type=str, help='flag at begin of comments to indicate new swatch (if there are multiple swatches in the file)', default=';begin swatch:')


parser.add_argument('-o', '--out_path', type=str, help='path to write output file to', default='data-auto/')


parser.add_argument('-n', '--normalize', action='store_true')


parser.add_argument('--masses_path', type=str, help='directory containing the masses', default='masses-auto/')

args = parser.parse_args()

if args.swatch_flag and args.swatch_flag[0] != ';': args.swatch_flag = ';' + args.swatch_flag

args.machine = args.machine.lower()
if args.machine == 'kniterate':
    machine_width = 252
    yarn_ops_d = {'in': '+', 'out': '-'}
else:
    machine_width = 540
    yarn_ops_d = {'inhook': '-', 'outhook': '+'}

fn = os.path.splitext(os.path.basename(args.knitout_path))[0]

with open(args.knitout_path, 'r+') as f:
    content = f.read().split(os.linesep) # for either \n or \r\n

# grams/cm
def normalizeMass(mass, lindensity, norm_density):
    return mass/lindensity*norm_density


def addMissingConeLabels(fpath, delimiter=','):
    # inspired by: https://stackoverflow.com/a/52862557
    s_data = []
    cone_label_ct = 0
    last_cone = None
    max_num_delims = 0

    with open(fpath, 'r') as f:
        for i, ln in enumerate(f):
            delim_ct = ln.count(delimiter)
            if i == 0:
                cone_labels = ln.strip().split(',')
                if not len(cone_labels[-1]):
                    cone_labels.pop()
                    ln = ','.join(cone_labels)
                    delim_ct -= 1

                cone_label_ct = delim_ct
                last_cone = cone_labels[-1]
            
            s_data.append(ln)

            if delim_ct > max_num_delims:
                max_num_delims = delim_ct

    if max_num_delims > cone_label_ct:
        cone_labels.extend([last_cone]*(max_num_delims-cone_label_ct))
        s_data[0] += ',' + ','.join([last_cone]*(max_num_delims-cone_label_ct))

    s_data = '\n'.join(s_data)

    return cone_labels, pd.read_csv(io.StringIO(s_data), sep=',', header=None)


lindensity = None
masses = None
default_cone = 1

mass_files = [f for f in os.listdir(args.masses_path) if regex.search(fn + r"(_\d+|-\d+|_v\d+|-v\d+)*.csv", f)]


if len(mass_files):
    cone_labels = np.empty(0, dtype=str)
    for f in mass_files:
        f_cone_labels, masses_df = addMissingConeLabels(os.path.join(args.masses_path, f))
        cone_labels = np.append(cone_labels, f_cone_labels)

        avg_scale_masses = np.nanmean(masses_df.values[1:].astype(float), axis=1)[:,np.newaxis]

        if masses is not None: masses = np.append(masses, avg_scale_masses, axis=1)
        else: masses = avg_scale_masses.copy()

    masses = masses.astype(float)

    if os.path.exists(f'{args.masses_path}/lindensity.csv'):
        
        lindensities = []
        cone_densities = pd.read_csv(f'{args.masses_path}/lindensity.csv', sep=',', header=None, index_col=0).dropna()
        
        cone_densities.index = cone_densities.index.astype(str)

        norm_density = cone_densities.values[0][0]

        for i, label in enumerate(cone_labels):
            try:
                lindensity = cone_densities.loc[label].values[0]
                lindensities.append(lindensity)

                if args.normalize:
                    for j in range(masses.shape[0]):
                        masses[j][i] = normalizeMass(masses[j][i], lindensity, norm_density)
            except:
                warnings.warn(f"missing linear density for cone {label}. No linear density will be recorded.")
            
        warnings.warn("using average linear density for now.")
        if len(lindensities): lindensity = np.mean(lindensities)
        else: lindensity = None

position_header = ';;Position: Center'

# get min/max needle
min_n, max_n = float('inf'), float('-inf')

for ln in content:
    if ln[:11] == 'Position':
        position_header = ln
        continue

    pat = r'(?<!;.*)(?<=(?:f|b)(?:s?))(\d+)'
    needles = regex.findall(pat, ln)

    for n in needles:
        n = int(n)
        if n < min_n: min_n = n
        if n > max_n: max_n = n

width = max_n-min_n+1


if position_header == ';;Position: Left':
    if args.machine == 'kniterate': out_n = min_n-1
    else: out_n = max_n+machine_width-width+1
elif position_header == ';;Position: Right':
    if args.machine == 'kniterate': out_n = max_n-machine_width
    else: out_n = max_n+1
elif position_header == ';;Position: Center':
    if args.machine == 'kniterate': out_n = max_n + round((machine_width-width)/2)-1
    else: out_n = min_n - round((machine_width-width)/2)+1
elif position_header == ';;Position: Keep':
    if args.machine == 'kniterate': out_n = min_n-1
    else: out_n = max_n+1

stitch_number = None

additive_ops = ['knit', 'tuck', 'backknit'] #TODO: add split

op_data = {
    'carrier': None,
    'knit': 0,
    'backknit': 0,
    'tuck': 0,
    'miss': 0,
    'gap': 0, #gap btw needles/slots
    'xknit': 0,
    'edge-knit': 0,
    'edge-backknit': 0
}

dfs = []

class OpCounter:
    def __init__(self, carrier):
        self.data = op_data.copy()
        self.data['carrier'] = carrier

datasets = []
op_cts = {}

data_df = []

carrier_track = {}


yarn_ops = ['in', 'out', 'inhook', 'releasehook', 'outhook']

def knitoutInfo(ln):
    ln = ln.strip()

    info = []
    op = None
    d = None
    bn0 = []
    bn = []
    cs = []
    param = None
    comment = None

    if ';;' in ln:
        info = ln.split(':')
        op = info[0] + ':'
    elif ';' in ln:
        comment_idx = ln.index(';')
        comment = ln[comment_idx:]
        info = ln[:comment_idx].strip().split(' ')
    else:
        info = ln.strip().split(' ')

    if len(info[0].strip()):
        op = info[0]
        if op == 'rack' or (len(op) > 1 and (op[:2] == 'x-' or op[:2] == ';;')):
            param = info[1].strip()
        else:
            if op in yarn_ops: cs = info[1:]
            elif op == 'knit' or op == 'tuck' or op == 'miss' or op == 'split':
                d = info[1]
                if op == 'split':
                    bn0 = [
                        regex.search(r'[a-zA-Z]+', info[2]).group(0),
                        int(regex.search(r'\d+', info[2]).group(0))
                    ]
                    bn = [
                        regex.search(r'[a-zA-Z]+', info[3]).group(0),
                        int(regex.search(r'\d+', info[3]).group(0))
                    ]
                    cs = info[4:]
                else:
                    bn = [
                        regex.search(r'[a-zA-Z]+', info[2]).group(0),
                        int(regex.search(r'\d+', info[2]).group(0))
                    ]
                    cs = info[3:]
            elif op == 'xfer':
                bn0 = [
                    regex.search(r'[a-zA-Z]+', info[1]).group(0),
                    int(regex.search(r'\d+', info[1]).group(0))
                ]
                bn = [
                    regex.search(r'[a-zA-Z]+', info[2]).group(0),
                    int(regex.search(r'\d+', info[2]).group(0))
                ]
            elif op == 'drop':
                bn = [
                    regex.search(r'[a-zA-Z]+', info[1]).group(0),
                    int(regex.search(r'\d+', info[1]).group(0))
                ]
            else: raise ValueError(f'Unrecognized operation: {op}.')

    return {'op': op, 'd': d, 'bn0': bn0, 'bn': bn, 'cs': cs, 'param': param, 'comment': comment}


note = ''

swatch_ct = 0
for i, ln in enumerate(content):
    info = knitoutInfo(ln)

    if args.swatch_flag and info['comment'] is not None:
        if info['comment'].startswith(args.swatch_flag):
            data_df = []
            if len(op_cts.keys()):
                for c in op_cts.keys():
                    carrier_track[c] = {'bn': None, 'd': None}
                    data_df.append(pd.Series(op_cts[c].data))

                if swatch_ct == 0: op_cts = {} # don't add data if haven't started a swatch yet (e.g. if there was a tuck pattern before)
                elif note != 'drop finish': #debug
                    datasets.append(op_cts)
                    df = pd.DataFrame(data_df).set_index('carrier').fillna(0)
                    df['comment'] = note
                    dfs.append(df)

            swatch_ct += 1

            note = info['comment'].replace(args.swatch_flag, '').strip()

            op_cts = {}

    if info['op'] == 'x-stitch-number': stitch_number = info['param']
    elif info['op'] == 'xfer':
        for c in carrier_track:
            if carrier_track[c]['bn'] is None: continue
            elif carrier_track[c]['bn'][1] == info['bn'][1]:
                carrier_track[c]['bn'][0] = info['bn'][0] #reflect bed change (i.e. for diags)
    elif len(info['cs']) and info['op'] != 'releasehook' and info['op'] != 'miss': #for now, only count misses if they are sandwiched between 'anchoring' yarn ops
        if info['op'] in yarn_ops:
            if args.swatch_flag:
                info['d'] = None
                info['bn'] = None
            else:
                info['d'] = yarn_ops_d[info['op']]
                info['bn'] = ['f', out_n]

        for c in info['cs']:
            if len(args.carriers) and c not in args.carriers: continue

            if info['op'][:2] == 'in':
                if c not in carrier_track: op_cts[c] = OpCounter(c)
            else:
                if c not in carrier_track: raise ValueError(f'Carrier {c} needs to be brought in before use (error generated @ knitout line {i+1}).')
                else:
                    if c not in op_cts: op_cts[c] = OpCounter(c) #e.g. new swatch in same file

                    if info['op'] == 'knit' and info['bn'][0] == 'b': op_cts[c].data['backknit'] += 1
                    elif info['op'] in additive_ops: op_cts[c].data[info['op']] += 1

                    if carrier_track[c]['bn'] is None or info['bn'] is None: miss_ct = 0
                    else:
                        gap_ct = abs(info['bn'][1]-carrier_track[c]['bn'][1])
                        if 'gap' in op_cts[c].data: op_cts[c].data['gap'] += gap_ct

                        if carrier_track[c]['d'] is not None and len(info['bn']) and info['bn'][0] != carrier_track[c]['bn'][0]:
                            if gap_ct > 0:
                                if not f'd{gap_ct}' in op_cts[c].data:
                                    op_cts[c].data[f'd{gap_ct}'] = 1
                                else: op_cts[c].data[f'd{gap_ct}'] += 1
                            else:
                                op_cts[c].data['xknit'] += 1
                                
                                op_cts[c].data['knit'] -= 1
                                op_cts[c].data['backknit'] -= 1
                        else:
                            if info['d'] == carrier_track[c]['d']:
                                if (info['d'] == '+' and info['bn'][1] < carrier_track[c]['bn'][1]) or (info['d'] == '-' and info['bn'][1] > carrier_track[c]['bn'][1]): # twisted stitch
                                    miss_ct = gap_ct+1
                                else:
                                    miss_ct = gap_ct-1
                            else:
                                if carrier_track[c]['d'] is not None:
                                    miss_ct = gap_ct

                                    if len(info['bn']) and info['bn'][0] == carrier_track[c]['bn'][0]:
                                        if carrier_track[c]['bn'][0] == 'f':
                                            op_cts[c].data['knit'] -= 2
                                            op_cts[c].data['edge-knit'] += 2
                                        else:
                                            op_cts[c].data['backknit'] -= 2
                                            op_cts[c].data['edge-backknit'] += 2

                            op_cts[c].data['miss'] += miss_ct

            carrier_track[c] = {'d': info['d'], 'bn': info['bn']}


# if any leftover:
if len(op_cts.keys()) and note != 'drop finish': #debug
    data_df = []
    for c in op_cts.keys():
        data_df.append(pd.Series(op_cts[c].data))

    df = pd.DataFrame(data_df).set_index('carrier').fillna(0)
    df['comment'] = note
    dfs.append(df)
    datasets.append(op_cts)


if masses is not None:
    assert swatch_ct == len(masses), f'swatch count: {swatch_ct} does not equal mass count: {len(masses)}'

    if not os.path.exists(args.out_path): os.mkdir(args.out_path)

    for i, df in enumerate(dfs):
        #v
        df['knit'] = df.loc[:,['knit','backknit']].sum(axis=1)
        df['edge-knit'] = df.loc[:,['edge-knit','edge-backknit']].sum(axis=1)
        df = df.drop(['backknit', 'edge-backknit'], axis=1)
        #^

        try:
            if masses is not None and i < len(masses):
                swatch_masses = masses[i][~np.isnan(masses[i])] # get rid of any nan values (from there being more data for other swatches in the file)
                if not len(swatch_masses): raise Exception("no masses recorded, skipping swatch.")
                for n in range(len(swatch_masses)):
                    df[f'mass {n}'] = swatch_masses[n]
            
            if lindensity is not None: df['lindensity'] = lindensity

            df.to_csv(os.path.join(args.out_path, fn + f'-{i}.csv'))
        except Exception as e:
            warnings.warn(str(e))
            pass
else: warnings.warn("no masses recorded, skipping file.")
