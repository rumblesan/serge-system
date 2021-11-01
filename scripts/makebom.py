#!/usr/bin/env python

import argparse
from os import listdir
from os.path import join, dirname, realpath, splitext, isfile
import glob
import re

from pathlib import Path
import csv

project_root_dir = join(dirname(realpath(__file__)), "..")
panel_list_dir = join(project_root_dir, "boms", "panels")
module_bom_dir = join(project_root_dir, "boms", "modules")
part_numbers_lookup = join(project_root_dir, "boms", "partnumbers.csv")
default_output_path = join(project_root_dir, "bom.csv")

def list_modules():
    for module in sorted(listdir(module_bom_dir)):
        name, _ = splitext(module)
        print(name)

def list_panels():
    for panel in sorted(listdir(panel_list_dir)):
        name, _ = splitext(panel)
        print(name)


def combine_modules(outputfile, modules):
    module_boms = []
    print("combining boms for:")
    for m in modules:
        module_info = {"module": m, "name": m}
        bom = read_module_bom(module_info)
        module_boms.append(bom)
        print(m)

    part_numbers = read_part_numbers()
    final_bom = combine_boms(module_boms, part_numbers)
    sort_bom(final_bom)

    write_bom_csv(outputfile, final_bom)

def gen_panel_bom(outputfile, panels):
    modules = []
    for p in panels:
        for m in read_panel_modules(p):
            modules.append(m)
    module_boms = []
    print("combining boms for:")
    for m in modules:
        bom = read_module_bom(m)
        # account for modules being used multiple times
        for _ in range(int(m["number"])):
            module_boms.append(bom)
            print(m["module"] + " - " + m["name"])

    part_numbers = read_part_numbers()
    final_bom = combine_boms(module_boms, part_numbers)
    sort_bom(final_bom)

    write_bom_csv(outputfile, final_bom)


def read_panel_modules(panel_name):
    panel_list_path = join(panel_list_dir, panel_name + ".csv")
    module_panels = []
    if not isfile(panel_list_path):
        print("Could not find panel list for %s" % panel_name)
        return []
    with open(panel_list_path) as csvfile:
        panel_list_reader = csv.DictReader(csvfile, skipinitialspace=True)
        module_panels = [row for row in panel_list_reader]
    return module_panels


def read_module_bom(module_info):
    bom_path = join(module_bom_dir, module_info["module"].strip() + ".csv")
    parts = []
    if not isfile(bom_path):
        print("Could not find module bom for %s" % module_info["module"])
        return parts
    with open(bom_path) as csvfile:
        bom_reader = csv.DictReader(csvfile, skipinitialspace=True)
        parts = [p for p in bom_reader]
    return parts

def read_part_numbers():
    part_numbers = {}
    with open(part_numbers_lookup) as csvfile:
        for pn in csv.DictReader(csvfile, skipinitialspace=True):
            key = pn['type'].strip() + pn['value'].strip() + pn['info'].strip()
            if key in part_numbers:
                raise Exception('Duplicate part entry {pn[type]} {pn[value]} {pn[info]}'.format(pn=pn))
            else:
                part_numbers[key] = pn['order code']
    return part_numbers

def combine_boms(module_boms, part_numbers):
    final_bom = {}
    for bom in module_boms:
        for part in bom:
            key = part["type"].strip() + part["value"].strip() + part["info"].strip()
            quantity = int(part["quantity"].strip())
            if key in final_bom:
                final_bom[key]["quantity"] += quantity
            else:
                final_bom[key] = {
                    "type": part["type"].strip(),
                    "value": part["value"].strip(),
                    "info": part["info"].strip(),
                    "order code": part_numbers.get(key, ''),
                    "quantity": quantity
                }
    return list(final_bom.values())


cap_re = re.compile(r"(\d+)([pnu])(\d*)f$")
res_re = re.compile(r"(\d+)([kmr])(\d*)$")

def value_to_sortable(comp_type, value):
    m = None
    if comp_type == 'capacitor':
        m = cap_re.match(value)
        if not m:
            return 0
    elif comp_type == 'resistor' or comp_type == 'potentiometer' or comp_type == 'trimpot':
        m = res_re.match(value)
        if not m:
            return 0
    else:
        return 0
    num = float("%s.%s" % (m.group(1), m.group(3)))
    return num * get_mult(m.group(2))

def get_mult(mult):
    if mult == "p":
        return 1
    elif mult == "n" or mult == "k":
        return 1000
    elif mult == "u" or mult == "m":
        return 1000000
    else:
        return 0

def sort_bom(final_bom):
    final_bom.sort(reverse = True, key = lambda p: p["quantity"])
    final_bom.sort(key = lambda p: value_to_sortable(p["type"], p["value"]))
    final_bom.sort(key = lambda p: p["type"])

def write_bom_csv(outputfile, final_bom):
    with open(outputfile, "w") as csvfile:
        fieldnames = ["type", "value", "quantity", "info", "order code"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in final_bom:
            writer.writerow(line)
    print("Finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create combined BOMs for Serge modules')
    parser.add_argument('-o', '--out', dest='outputfile', nargs='?', help='output file', default=default_output_path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--modules', action='store_true', help='expect list of module names to create BOM for')
    group.add_argument('-p', '--panels', action='store_true', help='expect list of panel names to create BOM for')
    parser.add_argument('names', nargs='*', help='names of panels or modules')
    args = parser.parse_args()
    if args.panels:
        if len(args.names) < 1:
            print("Must specify one or more panels:")
            list_panels()
        else:
            gen_panel_bom(Path(args.outputfile).with_suffix('.csv'), args.names)
    elif args.modules:
        if len(args.names) < 1:
            print("Must specify one or more modules:")
            list_modules()
        else:
            combine_modules(Path(args.outputfile).with_suffix('.csv'), args.names)
    else:
        parser.print_help()
