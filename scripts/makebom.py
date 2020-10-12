#!/usr/bin/env python

import argparse
from os import listdir
from os.path import join, dirname, realpath, splitext
import glob

from pathlib import Path
import csv

project_root_dir = join(dirname(realpath(__file__)), "..")
panel_list_dir = join(project_root_dir, "boms", "panels")
module_bom_dir = join(project_root_dir, "boms", "modules")
part_numbers_lookup = join(project_root_dir, "boms", "partnumbers.csv")

def list_panels():
    for panel in listdir(panel_list_dir):
        name, _ = splitext(panel)
        print(name)


def gen_panel_bom(outputfile, panels):
    modules = []
    for p in panels:
        for m in read_panel_modules(p):
            modules.append(m)
    module_boms = []
    print("comining boms for:")
    for m in modules:
        bom = read_module_bom(m)
        # account for modules being used multiple times
        for _ in range(int(m["number"])):
            module_boms.append(bom)
            print(m["module"] + " - " + m["name"])

    part_numbers = read_part_numbers()
    final_bom = combine_boms(module_boms, part_numbers)
    write_bom_csv(outputfile, final_bom)


def read_panel_modules(panel_name):
    panel_list_path = join(panel_list_dir, panel_name + ".csv")
    module_panels = []
    with open(panel_list_path) as csvfile:
        panel_list_reader = csv.DictReader(csvfile, skipinitialspace=True)
        module_panels = [row for row in panel_list_reader]
    return module_panels


def read_module_bom(module_info):
    bom_path = join(module_bom_dir, module_info["module"] + ".csv")
    parts = []
    with open(bom_path) as csvfile:
        bom_reader = csv.DictReader(csvfile, skipinitialspace=True)
        parts = [p for p in bom_reader]
    return parts

def read_part_numbers():
    part_numbers = {}
    with open(part_numbers_lookup) as csvfile:
        for pn in csv.DictReader(csvfile, skipinitialspace=True):
            key = pn['type'] + pn['value'] + pn['info']
            if key in part_numbers:
                raise Exception('Duplicate part entry {pn[type]} {pn[value]} {pn[info]}'.format(pn=pn))
            else:
                part_numbers[key] = pn['order code']
    return part_numbers

def combine_boms(module_boms, part_numbers):
    final_bom = {}
    for bom in module_boms:
        for part in bom:
            key = part["type"] + part["value"] + part["info"]
            quantity = int(part["quantity"])
            if key in final_bom:
                final_bom[key]["quantity"] += quantity
            else:
                final_bom[key] = {
                    "type": part["type"],
                    "value": part["value"],
                    "info": part["info"],
                    "order code": part_numbers.get(key, ''),
                    "quantity": quantity
                }
    return list(final_bom.values())

def write_bom_csv(outputfile, final_bom):
    final_bom.sort(key = lambda p: p["value"])
    final_bom.sort(reverse = True, key = lambda p: p["quantity"])
    final_bom.sort(key = lambda p: p["type"])
    with open(outputfile, "w") as csvfile:
        fieldnames = ["type", "value", "quantity", "info", "order code"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in final_bom:
            writer.writerow(line)
    print("Finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create combined BOMs for Serge CGS panels')
    parser.add_argument('-o', '--out', dest='outputfile', nargs='?', help='output file', default='../bom.csv')
    parser.add_argument('panels', nargs='*', help='panels to create BOM for')
    args = parser.parse_args()
    if len(args.panels) < 1:
        list_panels()
    else:
        gen_panel_bom(Path(args.outputfile).with_suffix('.csv'), args.panels)
