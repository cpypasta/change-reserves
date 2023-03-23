from deca.ff_rtpc import rtpc_from_binary, RtpcProperty, RtpcNode
from pathlib import Path
from typing import List, Tuple
from functools import reduce
from enum import Enum
import os

def _parent_path() -> Path:
   return Path(os.path.realpath(__file__)).parents[0]

DROPZONE_NAME = "dropzone/settings/hp_settings"
SOURCE_PATH = _parent_path() / "data"
MOD_PATH = Path().home() / "Documents/ReserveChanger/mods"
MOD_PATH.mkdir(exist_ok=True, parents=True)

class ReserveValue:
  def __init__(self, value: int, offset: int) -> None:
    self.value = value
    self.offset = offset
    
  def __repr__(self):
    return f"{self.value:} ({self.offset})"

class Deployable(str, Enum):
  LAYOUTBLIND = "layoutblind"
  TREESTAND = "treestand"
  TENT = "tent"
  TRIPOD = "tripodstand"
  GROUNDBLIND = "groundblind"

def _is_deployable_prop(value: str):
  return Deployable.LAYOUTBLIND in value or \
    Deployable.TREESTAND in value or \
      Deployable.TENT in value or \
        Deployable.TRIPOD in value or \
          Deployable.GROUNDBLIND in value

class DeployableValue:
  def __init__(self, value: int, offset: int) -> None:
    self.value = value
    self.offset = offset

  def __repr__(self):
    return f"{self.value:} ({self.offset}))"

def _open_reserve(filename: Path) -> Tuple[RtpcNode, bytearray]:
  with(filename.open("rb") as f):
    data = rtpc_from_binary(f) 
  f_bytes = bytearray(filename.read_bytes())
  return (data.root_node, f_bytes)

def _all_non_zero_props(props: List[RtpcProperty]) -> List[ReserveValue]:
  offsets = []
  for prop in props:
    if prop.data != 0:
      offsets.append(ReserveValue(prop.data, prop.data_pos))
  return offsets

def _big_props(props: List[RtpcProperty]) -> List[ReserveValue]:
  offsets = []
  first = props[-4]
  second = props[-1]
  if first.data != 0:
    offsets.append(ReserveValue(first.data, first.data_pos))
  if second.data != 0:
    offsets.append(ReserveValue(second.data, second.data_pos))
  return offsets

def _update_uint(data: bytearray, offset: int, new_value: int) -> None:
    value_bytes = new_value.to_bytes(4, byteorder='little')
    for i in range(0, len(value_bytes)):
        data[offset + i] = value_bytes[i]

def _is_deployable(props: List[RtpcProperty]) -> bool:
  for prop in props:
    if isinstance(prop.data, bytes) and _is_deployable_prop(prop.data.decode("utf-8")):
      return True
  return False

def get_mod_path() -> Path:
  return MOD_PATH / DROPZONE_NAME

def _save_file(filename: str, data: bytearray) -> None:
    base_path = get_mod_path()
    base_path.mkdir(exist_ok=True, parents=True)
    (base_path / filename).write_bytes(data)  

def update_reserve_population(root: RtpcNode, f_bytes: bytearray, multiply: int, debug: bool = False) -> None:
  config_children = root.child_table[0].child_table

  offsets_to_change = []
  for child in config_children:
    first_child = child.child_table[0]
    second_child = child.child_table[1]

    pattern_one = first_child.prop_count == 4
    pattern_two = first_child.prop_count == 0 
    if pattern_one:
      pattern_one_one = second_child.prop_count == 0
      if pattern_one_one: # child[0],child[1]->children
        if first_child.child_count == 0: # edge case where some have children
          result = _all_non_zero_props(first_child.prop_table)
          if debug:
            print(f"{'*':5} {result}")
          offsets_to_change.append(result)
        second_child_children = second_child.child_table
        for child in second_child_children:     
          result = _big_props(child.prop_table)
          if debug:
            print(f"{'*':5} {result}")  
          offsets_to_change.append(result)    
      else: # child[0]                     
        result = _all_non_zero_props(first_child.prop_table)
        if debug:
          print(f"{'**':5} {result}")  
        offsets_to_change.append(result)
    elif pattern_two: # child[0]->children
        first_child_children = first_child.child_table
        for child in first_child_children:
          result = _big_props(child.prop_table)
          if debug:
            print(f"{'***':5} {result}")            
          offsets_to_change.append(_big_props(child.prop_table))
    else:
       print("unknown")

  reserve_values = reduce(lambda a, b: a + b, offsets_to_change)
  try:
    for reserve_value in reserve_values:
      _update_uint(f_bytes, reserve_value.offset, reserve_value.value * multiply)
  except Exception as ex:
     print(f"received error: {ex}")
           
def update_all_populations(source: Path, multiply: int) -> None:
  for filename in os.listdir(source):    
    print(f"updating population in {filename.rjust(15)}")
    root, data = _open_reserve(source / filename)
    update_reserve_population(root, data, multiply)
    _save_file(filename, data)
  print("done")

def update_reserve_deployables(root: RtpcNode, f_bytes: bytearray, multiply: int, debug: bool = False) -> None:
  deployables = root.child_table[6].child_table
  deployable_values = []
  for deployable in deployables:
    if _is_deployable(deployable.prop_table):
      prop = deployable.prop_table[-1]
      deployable_values.append(DeployableValue(prop.data, prop.data_pos))
  if debug:
    print(deployable_values)

  try:
    for deployable_value in deployable_values:
      _update_uint(f_bytes, deployable_value.offset, deployable_value.value * multiply)
  except Exception as ex:
     print(f"received error: {ex}")

def update_all_deployables(source: Path, multiply: int) -> None:
  for filename in os.listdir(source):
    print(f"updating deployables in {filename.rjust(15)}")
    root, data =_open_reserve(source / filename)
    update_reserve_deployables(root, data, multiply)
    _save_file(filename, data)
  print("done")

def process(source: Path, population: bool, deployables: bool, pop_multiply: int = 2, deploy_multiply: int = 2) -> str:
  if population and deployables:
    update_all_populations(source, pop_multiply)
    source_path = get_mod_path()
    update_all_deployables(source_path, deploy_multiply)
    return source_path
  elif population:
    update_all_populations(source, pop_multiply)
    return get_mod_path()
  elif deployables:
    update_all_deployables(source, deploy_multiply)
    return get_mod_path()

def main():
    # update_all_reserves(5)
    # update_reserve_population("reserve_0.bin", 2, True)
    update_all_deployables(SOURCE_PATH, 2)