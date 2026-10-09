import ctypes
import heapq
import weakref
import json
from collections import defaultdict
import math
import time
# import tracemalloc
# import resource

from collections import Counter
from dataclasses import dataclass, field

lib = ctypes.CDLL("libeffect_engine_c.dylib")

c_int_p = ctypes.POINTER(ctypes.c_int)  # para los `int* out`

c_void_p_p = ctypes.POINTER(ctypes.c_void_p)  # para `const EEIngredient* const*`

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

lib.effect_engine_mix.argtypes = [ctypes.c_void_p, c_void_p_p, ctypes.c_size_t, ctypes.c_char_p]
lib.effect_engine_mix.restype = ctypes.c_void_p

lib.effect_engine_subtract.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
lib.effect_engine_subtract.restype = ctypes.c_void_p

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

lib.effect_engine_crafted_effect_distance.argtypes = [ctypes.c_void_p]
lib.effect_engine_crafted_effect_distance.restype = ctypes.c_float

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

# ---- Wrappers con dueño (equivalente a EEIngredientRef de Godot) ----
# El handle se libera solo cuando muere la ultima referencia Python, igual que
# RefCounted. weakref.finalize corre a lo mucho una vez -> no hay doble free.

NODE_KIND = {0: "source", 1: "mix", 2: "alter", 3: "subtract"}

class EngineBackend:
    def __init__(self, engine):
        self.engine = engine
        self.object_for = {}

    def register(self, obj:EEIngredient) -> tuple:
        vector = tuple(obj.dimensions())
        if vector not in self.object_for:
            self.object_for[vector] = obj
        return vector

    def getObject(self, vector:tuple) -> EEIngredient:
        if vector not in self.object_for:
            raise ValueError(f"the vector does not have an object")
        return self.object_for[vector]

    def apply(self, op_name, a, b) -> tuple:
        """Tuples in, tuple out. the engine works underneath."""
        obj_a : EEIngredient = self.object_for[a]
        obj_b : EEIngredient = self.object_for[b]

        handles = (obj_a._h, obj_b._h)
        arr = (ctypes.c_void_p * len(handles))(*handles)

        if op_name == "add":
            result = lib.effect_engine_mix(self.engine, arr, len(arr), "add".encode())
        elif op_name == "multiply":
            result = lib.effect_engine_mix(self.engine, arr, len(arr), "multiply".encode())
        elif op_name == "subtract":
            result = lib.effect_engine_subtract(self.engine, obj_a._h, obj_b._h)
        else:
            raise ValueError(f"unknown operation: {op_name}")

        return self.register(EEIngredient(result, f"{op_name}"))

    def alter(self, a, alter_object_name: str) -> tuple:
        result = lib.effect_engine_alter(self.engine, self.object_for[a]._h, alter_object_name.encode())
        return self.register(EEIngredient(result, f"alter {alter_object_name}"))


def _err(what):
    detail = lib.effect_engine_last_error().decode() or "sin detalle"
    return RuntimeError(f"{what}: {detail}")


def _read_ints(fn, handle, n):
    """Lee un `int* out` de n enteros a una lista de Python."""
    buf = (ctypes.c_int * n)()
    if fn(handle, buf, n) < 0:
        raise _err(fn.__name__)
    return list(buf)


def _node_to_dict(node):
    """Arbol de receta como dicts anidados. Los nodos son vistas prestadas, asi que
    copiamos todo a datos planos mientras el handle padre sigue vivo."""
    kind = lib.effect_engine_node_kind(node)
    d = {
        "kind": NODE_KIND.get(kind, kind),
        "id": lib.effect_engine_node_id(node).decode(),
        "dimensions": _read_ints(lib.effect_engine_node_dimensions, node,
                                 lib.effect_engine_node_domain_count(node) * 3),
        "children": [_node_to_dict(lib.effect_engine_node_child(node, i))
                     for i in range(lib.effect_engine_node_child_count(node))],
    }
    if kind == 0:
        d["tier"] = lib.effect_engine_node_tier(node).decode()
    else:
        d["operation_id"] = lib.effect_engine_node_operation_id(node).decode()
        if kind == 2:
            d["alter_object_id"] = lib.effect_engine_node_alter_object_id(node).decode()
    return d


class _Owned:
    _free = None  # la *_free correspondiente; los _FuncPtr no son descriptores

    def __init__(self, handle, what):
        if not handle:
            raise _err(what)
        self._h = handle
        self._fin = weakref.finalize(self, type(self)._free, handle)

    def free(self):
        """Libera ya. Opcional: el finalize lo hace solo."""
        self._fin()
        self._h = None


class EEIngredient(_Owned):
    _free = lib.effect_engine_ingredient_free

    @classmethod
    def source(cls, source_id, tier):
        return cls(lib.effect_engine_get_source(potion_engine, source_id.encode(), tier.encode()),
                   f"source {source_id}/{tier}")

    def dimensions(self):
        """Coordenadas planas [d0x,d0y,d0z, d1x,d1y,d1z, ...]."""
        return _read_ints(lib.effect_engine_ingredient_dimensions, self._h,
                          lib.effect_engine_ingredient_domain_count(self._h) * 3)

    def recipe_tree(self):
        return _node_to_dict(lib.effect_engine_ingredient_root(self._h))

    def craft(self):
        return EECrafted(lib.effect_engine_craft(potion_engine, self._h), "craft")


class EECrafted(_Owned):
    _free = lib.effect_engine_crafted_free

    @property
    def effect_id(self):
        """"" = efecto nulo (cayo fuera de todo radio de captura)."""
        return lib.effect_engine_crafted_effect_id(self._h).decode()

    def dimensions(self):
        return _read_ints(lib.effect_engine_crafted_dimensions, self._h, cap)

    def active_domains(self):
        """[(domain_id, fuerza)] con fuerza = 1 - distancia normalizada."""
        return [(lib.effect_engine_crafted_active_domain_id(self._h, i).decode(),
                 1.0 - lib.effect_engine_crafted_active_domain_distance(self._h, i))
                for i in range(lib.effect_engine_crafted_active_domain_count(self._h))]

    def recipe_tree(self):
        return _node_to_dict(lib.effect_engine_crafted_root(self._h))

    def distance(self) -> float:
        return lib.effect_engine_crafted_effect_distance(self._h)


def alter_exponents(alter_object_id):
    buf = (ctypes.c_int * dcount)()
    if lib.effect_engine_alter_exponents(potion_engine, alter_object_id.encode(), buf, dcount) < 0:
        raise _err(f"alter_exponents {alter_object_id}")
    return list(buf)


def sources():
    """[(source_id, [tiers])] del config."""
    out = []
    for i in range(lib.effect_engine_source_count(potion_engine)):
        sid = lib.effect_engine_source_id(potion_engine, i).decode()
        out.append((sid, [lib.effect_engine_tier_id(potion_engine, sid.encode(), t).decode()
                          for t in range(lib.effect_engine_tier_count(potion_engine, sid.encode()))]))
    return out


def alter_objects():
    return [lib.effect_engine_alter_object_id(potion_engine, i).decode()
            for i in range(lib.effect_engine_alter_object_count(potion_engine))]


MODULUS = 11
BASE_ACTION_COST = { "add": 1.0, "subtract": 1.5, "multiply": 2.0, "alter": 2.0}
TIER_COST = {"standard": 0.2, "rare":1.0, "legendary": 2.0 }
REPETITION_PENALTY = 2.0
COST_PER_EXTRA_INPUT =  0.5
MAX_COST = 9

ALTER_EXPONENTS =tuple(range(2, MODULUS - 1))

COMMUTATIVE = { "add": True, "multiply": True, "subtract": False}
DIMENSIONS = 3


@dataclass(frozen=True)
class Ingredient:
    name:str
    vector: tuple
    tier: str

@dataclass(frozen=True)
class Action:
    operation:str
    inputs:tuple
    exponent: int = None

def action_cost(action, tier_of):
    """
    Cost of performing this one action, ignoring what it cost to obtain
    the inputs. `tier_of` maps a point-tuple to a tier name, but only for
    BASE ingredients. Intermediate products are not in that dict, because
    their rarity was already paid for when they were built.
    """
    cost = BASE_ACTION_COST[action.operation]
    cost += COST_PER_EXTRA_INPUT * (len(action.inputs) - 2)
 
    duplicates = len(action.inputs) - len(set(action.inputs))
    cost += REPETITION_PENALTY * duplicates
 
    for point in action.inputs:
        tier = tier_of.get(point)
        if tier is not None:
            cost += TIER_COST[tier]
 
    return cost

def compute_cost_map(backend, engine_ingredients, alter_objects, max_cost=MAX_COST,):

    tier_of = {}
    cost = {}
    recipe = {}
    queue = []

    for ing in engine_ingredients:
        if type(backend) == EngineBackend:
            engine_ing = EEIngredient.source(ing[0], ing[1])
            vector : tuple = backend.register(engine_ing)
            tier_of[vector] = ing[1]
            if vector not in cost:
                cost[vector] = 0.0
                heapq.heappush(queue, (0.0, vector))

    settled = []
    settled_set = set()

    def relax(new_point, new_cost):
        if new_cost > max_cost:
            return
        if new_cost < cost.get(new_point, float("inf")):
            cost[new_point] = new_cost
            heapq.heappush(queue, (new_cost, new_point))

    while queue:
        current_cost, point = heapq.heappop(queue)

        if point in settled_set:
            continue
        if current_cost > cost[point]:
            continue
        if current_cost > max_cost:
            break

        settled_set.add(point)
        settled.append(point)

        for k in alter_objects:
            action = Action("alter", (point,),k )
            result = backend.alter(point, k)
            relax(result, current_cost + action_cost(action, tier_of))

        for other in settled:
            for op_name in ("add", "subtract", "multiply"):
                if COMMUTATIVE[op_name] or point == other:
                    pairs = [(point, other)]
                else:
                    pairs = [(point, other), (other, point)]

                for a, b in pairs:
                    result = backend.apply(op_name, a, b)
                    total = cost[a] + cost[b] + action_cost(Action(op_name, (a , b)), tier_of)
                    relax(result, total)

    return cost

def walk_tree(node):
    yield node
    for child in node["children"]:
        for desendant in walk_tree(child):
            yield desendant


def recipe_parts(tree):
    """(ingredientes, operaciones) de un recipe_tree, con cuantas veces sale cada uno.

    ingredientes: Counter{(source_id, tier): n}
    operaciones:  Counter{"add"/"multiply"/"subtract"/"alter <objeto>": n}
    """
    ingredients, operations = Counter(), Counter()
    for node in walk_tree(tree):
        if node["kind"] == "source":
            ingredients[(node["id"], node["tier"])] += 1
        elif node["kind"] == "alter":
            operations[f"alter {node['alter_object_id']}"] += 1
        else:
            operations[node["operation_id"]] += 1
    return ingredients, operations


def tally_usage(trees):
    """(n_recetas, ingredientes, operaciones); cada tabla es {nombre: [usos, recetas]}."""
    tables = ({}, {})
    trees = list(trees)
    for tree in trees:
        for table, counts in zip(tables, recipe_parts(tree)):
            for name, n in counts.items():
                row = table.setdefault(name, [0, 0])
                row[0] += n
                row[1] += 1
    return len(trees), tables[0], tables[1]


def print_usage_table(title, table, total_recipes):
    print(f"\n{title:<28}{'usos':>8}{'% recetas':>12}")
    for name, (uses, recipes) in sorted(table.items(), key=lambda kv: -kv[1][0]):
        label = "/".join(name) if isinstance(name, tuple) else name
        print(f"{label:<28}{uses:>8}{recipes / total_recipes:>12.1%}")


def _test_recipe_parts():
    tree = {"kind": "mix", "id": "m", "operation_id": "add", "children": [
        {"kind": "source", "id": "mint", "tier": "standard", "children": []},
        {"kind": "alter", "id": "a", "operation_id": "alter", "alter_object_id": "k3",
         "children": [{"kind": "source", "id": "mint", "tier": "standard", "children": []}]},
    ]}
    ings, ops = recipe_parts(tree)
    assert ings == Counter({("mint", "standard"): 2}), ings
    assert ops == Counter({"add": 1, "alter k3": 1}), ops

    solo = {"kind": "source", "id": "sage", "tier": "rare", "children": []}
    n, ings, ops = tally_usage([tree, solo])
    assert n == 2
    assert ings == {("mint", "standard"): [2, 1], ("sage", "rare"): [1, 1]}, ings
    assert ops == {"add": [1, 1], "alter k3": [1, 1]}, ops



def init_engine(config_path=JSON_config_path):
    """Loads the C engine and publishes the handles the wrappers read."""
    # ponytail: EEIngredient/EECrafted read `potion_engine` and `cap` as module
    # globals. Injecting the engine into them is the real DIP fix; not done here
    # because it touches every wrapper. Do it if a second engine is ever needed.
    global potion_engine, dcount, cap
    potion_engine = lib.effect_engine_load(config_path.encode("utf-8"))
    if not potion_engine:
        raise _err(f"effect_engine_load {config_path}")
    dcount = lib.effect_engine_domain_count(potion_engine)
    cap = dcount * 3
    return EngineBackend(potion_engine)


def load_config(config_path=JSON_config_path):
    with open(config_path, encoding="utf-8") as file:
        return json.load(file)


def base_ingredients_of(config):
    """[(source_id, tier_id)] for every source/tier pair in the config."""
    return [(source, tier)
            for source, obj in config["source_objects"].items()
            for tier in obj["tiers"]]


def base_alters_of(config):
    return list(config["alter_objects"])


def classify_effects(engine, cost):
    """Groups reached points by effect and keeps the closest one to each anchor."""
    effects_reached = defaultdict(lambda: {"count": 0, "points": []})
    best_by_effect = {}

    for point, price in cost.items():
        obj = engine.getObject(point)

        if lib.effect_engine_node_kind(lib.effect_engine_ingredient_root(obj._h)) == 0:
            continue  # base ingredient, nothing was crafted

        crafted = obj.craft()
        effect_id = crafted.effect_id
        if not effect_id:
            continue
        distance = crafted.distance()

        entry = effects_reached[effect_id]
        entry["points"].append((point, price))
        entry["count"] += 1

        best = best_by_effect.get(effect_id)
        if best is None or distance < best["distance"]:
            best_by_effect[effect_id] = {"point": point, "price": price, "distance": distance}

    return effects_reached, best_by_effect


def report(engine, cost, effects_reached, best_by_effect):
    total_points = MODULUS ** DIMENSIONS
    costs = sorted(cost.values())

    print(f"reached {len(cost)} / {total_points} points under cost {MAX_COST}")
    print(f"practical coverage: {len(cost) / total_points:.1%}")
    print(f"median cost: {costs[len(costs) // 2]:.2f}")
    print(f"most expensive reached: {costs[-1]:.2f}")

    print("Effects reached:")
    for effect_id, effect_data in effects_reached.items():
        best = best_by_effect[effect_id]
        print(f"{effect_id}")
        print(f"Points reached: {effect_data['count']}")
        print(f"Closer point to anchor: {best['point']} by: {best['distance']} cost: {best['price']}")

    # effects_reached solo tiene puntos con efecto: los nulos ya se filtraron al craftear
    total, ingredients, operations = tally_usage(
        engine.getObject(point).recipe_tree()
        for data in effects_reached.values() for point, _ in data["points"])

    print(f"\nUso en las {total} recetas con efecto")
    print_usage_table("Ingrediente", ingredients, total)
    print_usage_table("Operacion", operations, total)


def main(config_path=JSON_config_path):
    engine = init_engine(config_path)
    config = load_config(config_path)

    # tracemalloc.start()
    start = time.perf_counter()
    cost = compute_cost_map(engine, base_ingredients_of(config), base_alters_of(config))
    # current, peak = tracemalloc.get_traced_memory()
    print(f"\nTime to process the points {time.perf_counter() - start:.2f}s")
    # print(f"actual: {current / 1024**2:.1f} MB, pico: {peak / 1024**2:.1f} MB")
    # tracemalloc.reset_peak()
    report(engine, cost, *classify_effects(engine, cost))
    # pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # print(f"peak C++: {pico / 1024**2:.1f} MB")

    return cost


if __name__ == "__main__":
    main()
