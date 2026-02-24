from jsonmerge import merge
import json
import argparse
import os
import sys
from jsonget import json_get
import copy


def resolve_refs_internal(resolve_root, current_object, result):
    if isinstance(current_object, dict):
        for k in current_object.keys():
            result[k] = current_object[k]
            if isinstance(current_object[k], dict):
                if '$ref' in current_object[k].keys():
                    ref_path = current_object[k]['$ref']
                    result[k] = json_get(resolve_root, ref_path[1:])
                else:
                    resolve_refs_internal(resolve_root, current_object[k], result[k])


def resolve_refs(json_data):
    resolve_root = copy.deepcopy(json_data)
    result = {}
    resolve_refs_internal(json_data, json_data, result)
    return result


PARSER = argparse.ArgumentParser(description='')
PARSER.add_argument('--input', '-i', required=False, default=os.getcwd())
PARSER.add_argument('--output', '-o', required=True)
PARSER.add_argument('--resolve_ref', '-r', action='store_true', required=False, default=False)
ARGS = PARSER.parse_args()

swagger = {}
for root, dirs, files in os.walk(ARGS.input):
    for f in files:
        if f.endswith('.json'):
            try:
                j = json.load(open(os.path.join(root, f), encoding='utf-8'))
            except Exception as e:
                raise Exception(f"fail to load {f} {e}")
            swagger = merge(swagger, j)

if ARGS.resolve_ref:
    print("Resolving refs in openapi")
    resolved_refs = resolve_refs(swagger)
    json.dump(resolved_refs, open(ARGS.output, 'w'))
else:
    print("SKIP! Resolving refs in openapi")
    json.dump(swagger, open(ARGS.output, 'w'))
