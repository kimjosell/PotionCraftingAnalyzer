import ctypes
import json
from collections import defaultdict
import math

lib = ctypes.CDLL("libeffect_engine_c.dylib")

c_int_p = ctypes.POINTER(ctypes.c_int)  # para los `int* out`

# ---- Errores ----
lib.effect_engine_last_error.argtypes = []          # void
lib.effect_engine_last_error.restype = ctypes.c_char_p

# ---- Lifecycle ----
lib.effect_engine_load.argtypes = [ctypes.c_char_p]
lib.effect_engine_load.restype = ctypes.c_void_p

lib.effect_engine_destroy.argtypes = [ctypes.c_void_p]
lib.effect_engine_destroy.restype = None            # void

# ---- Ingredients ----
lib.effect_engine_get_source.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
lib.effect_engine_get_source.restype = ctypes.c_void_p

lib.effect_engine_mix.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_char_p, ctypes.c_int]
lib.effect_engine_mix.restype = ctypes.c_void_p

lib.effect_engine_alter.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p]
lib.effect_engine_alter.restype = ctypes.c_void_p

lib.effect_engine_ingredient_free.argtypes = [ctypes.c_void_p]
lib.effect_engine_ingredient_free.restype = None    # void

lib.effect_engine_ingredient_domain_count.argtypes = [ctypes.c_void_p]
lib.effect_engine_ingredient_domain_count.restype = ctypes.c_int

lib.effect_engine_ingredient_dimensions.argtypes = [ctypes.c_void_p, c_int_p, ctypes.c_int]
lib.effect_engine_ingredient_dimensions.restype = ctypes.c_int

# ---- Craft ----
lib.effect_engine_craft.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
lib.effect_engine_craft.restype = ctypes.c_void_p

lib.effect_engine_crafted_free.argtypes = [ctypes.c_void_p]
lib.effect_engine_crafted_free.restype = None       # void

lib.effect_engine_crafted_effect_id.argtypes = [ctypes.c_void_p]
lib.effect_engine_crafted_effect_id.restype = ctypes.c_char_p

lib.effect_engine_crafted_dimensions.argtypes = [ctypes.c_void_p, c_int_p, ctypes.c_int]
lib.effect_engine_crafted_dimensions.restype = ctypes.c_int

lib.effect_engine_crafted_active_domain_count.argtypes = [ctypes.c_void_p]
lib.effect_engine_crafted_active_domain_count.restype = ctypes.c_int

lib.effect_engine_crafted_active_domain_id.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.effect_engine_crafted_active_domain_id.restype = ctypes.c_char_p

lib.effect_engine_crafted_active_domain_distance.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.effect_engine_crafted_active_domain_distance.restype = ctypes.c_float

# ---- Recipe tree (los nodos son punteros opacos: c_void_p) ----
lib.effect_engine_ingredient_root.argtypes = [ctypes.c_void_p]
lib.effect_engine_ingredient_root.restype = ctypes.c_void_p

lib.effect_engine_crafted_root.argtypes = [ctypes.c_void_p]
lib.effect_engine_crafted_root.restype = ctypes.c_void_p

lib.effect_engine_node_kind.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_kind.restype = ctypes.c_int

lib.effect_engine_node_id.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_id.restype = ctypes.c_char_p

lib.effect_engine_node_tier.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_tier.restype = ctypes.c_char_p

lib.effect_engine_node_operation_id.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_operation_id.restype = ctypes.c_char_p

lib.effect_engine_node_time.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_time.restype = ctypes.c_int

lib.effect_engine_node_alter_object_id.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_alter_object_id.restype = ctypes.c_char_p

lib.effect_engine_node_domain_count.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_domain_count.restype = ctypes.c_int

lib.effect_engine_node_dimensions.argtypes = [ctypes.c_void_p, c_int_p, ctypes.c_int]
lib.effect_engine_node_dimensions.restype = ctypes.c_int

lib.effect_engine_node_child_count.argtypes = [ctypes.c_void_p]
lib.effect_engine_node_child_count.restype = ctypes.c_int

lib.effect_engine_node_child.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.effect_engine_node_child.restype = ctypes.c_void_p

# ---- Alter object inspection ----
lib.effect_engine_alter_exponents.argtypes = [ctypes.c_void_p, ctypes.c_char_p, c_int_p, ctypes.c_int]
lib.effect_engine_alter_exponents.restype = ctypes.c_int

# ---- Config queries para UI ----
lib.effect_engine_source_count.argtypes = [ctypes.c_void_p]
lib.effect_engine_source_count.restype = ctypes.c_int

lib.effect_engine_source_id.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.effect_engine_source_id.restype = ctypes.c_char_p

lib.effect_engine_tier_count.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
lib.effect_engine_tier_count.restype = ctypes.c_int

lib.effect_engine_tier_id.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
lib.effect_engine_tier_id.restype = ctypes.c_char_p

lib.effect_engine_alter_object_count.argtypes = [ctypes.c_void_p]
lib.effect_engine_alter_object_count.restype = ctypes.c_int

lib.effect_engine_alter_object_id.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.effect_engine_alter_object_id.restype = ctypes.c_char_p

lib.effect_engine_domain_count.argtypes = [ctypes.c_void_p]
lib.effect_engine_domain_count.restype = ctypes.c_int

lib.effect_engine_domain_id.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.effect_engine_domain_id.restype = ctypes.c_char_p


JSON_config_path = "tea_alchemist_config-v1.0.0.json"

potion_engine = lib.effect_engine_load(JSON_config_path.encode('utf-8'))

with open(JSON_config_path, 'r') as file:
    config_data = json.load(file)

ing_count = lib.effect_engine_source_count(potion_engine)
dcount = lib.effect_engine_domain_count(potion_engine)
cap = dcount * 3
step = 0
points_list = {}


for i in range(ing_count):
    ing_id = lib.effect_engine_source_id(potion_engine, i)
    tier_count = lib.effect_engine_tier_count(potion_engine, ing_id)
    for j in range(tier_count):
        tier_id = lib.effect_engine_tier_id(potion_engine, ing_id, j)
        buf = (ctypes.c_int * cap)()
        ing = lib.effect_engine_get_source(potion_engine, ing_id, tier_id)
        n = lib.effect_engine_ingredient_dimensions(ing, buf, cap)
        point = list(buf)
        
        key = tuple(point)

        points_list[key] = { "handle": ing, "steps":  step, "ingredients": { ing_id.decode()}, "operations": set(), "effect": ""}


fronteir = {}
print(len(points_list))
for round in range(5):
    new_points = {}
    if round == 0:
        fronteir = points_list
    for k1, v1 in fronteir.items():
        for k2, v2 in points_list.items():
            if v1["steps"] + v2["steps"] + 1 > 5:
                continue
            for operation, max_modifier in config_data["operations"].items():
                for modifier in range(max_modifier["max_modifier"] + 1):
                    time = modifier * max_modifier["time_per_point"]
                    new1 = lib.effect_engine_mix(potion_engine, v1["handle"], v2["handle"], operation.encode('utf-8'), time)
                    new2 = lib.effect_engine_mix(potion_engine, v2["handle"], v1["handle"], operation.encode('utf-8'), time)

                    for new in [new1, new2]:
                        buf = (ctypes.c_int * cap)()
                        n = lib.effect_engine_ingredient_dimensions(new, buf, cap)
                        if tuple(buf) in points_list or tuple(buf) in new_points:
                            lib.effect_engine_ingredient_free(new)
                            continue

                        crafted_object = lib.effect_engine_craft(potion_engine, new)
                        effect = lib.effect_engine_crafted_effect_id(crafted_object)
                        distances = {}
                        active_domains = lib.effect_engine_crafted_active_domain_count(crafted_object)
                        for domain in range(active_domains):
                            dom = lib.effect_engine_crafted_active_domain_id(crafted_object, domain).decode()
                            dist = lib.effect_engine_crafted_active_domain_distance(crafted_object, domain)
                            distances[dom] = dist
                        new_points[tuple(buf)] = { "handle": new, "steps": v1["steps"] + v2["steps"] + 1, "ingredients": v1["ingredients"] | v2["ingredients"], "operations": v1["operations"] | v2["operations"] | {operation}, "effect": effect.decode(), "distance": distances }

                        lib.effect_engine_crafted_free(crafted_object)
    points_list.update(new_points)
    fronteir = new_points
    if not new_points:
        break

by_effect = defaultdict(lambda: {
    "min_steps": float('inf'), "count": 0,
    "ingredients": set(), "operations": set(),
    "min_distance": None,
    "best_dist": float('inf'),
    "best_dist_steps": None
})
for value in points_list.values():
    effect = value["effect"]
    if effect == "":
        continue

    e = by_effect[effect]
    e["min_steps"] = min(e["min_steps"], value["steps"])
    e["count"] += 1
    e["ingredients"] |= value["ingredients"]
    e["operations"] |= value["operations"]

    if e["min_distance"] is None:
        e["min_distance"] = dict(value["distance"])
    else:
        for dom, d in value["distance"].items():
            e["min_distance"][dom] = min(e["min_distance"].get(dom, float('inf')), d)

    d = sum(value["distance"].values()) / len(value["distance"])
    if d < e["best_dist"]:
        e["best_dist"] = d
        e["best_dist_steps"] = value["steps"]


    

print("----------------------------")
for key, value in by_effect.items():
    print(key, "|", value["min_steps"], "|", value["count"], "|", value["ingredients"], "|", value["operations"], "|", value["min_distance"], "|", value["best_dist"], "|", value["best_dist_steps"])

print("-----------------------------")




    

    




        

            


