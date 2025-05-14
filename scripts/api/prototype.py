"""
Factorio Prototype Definitions

This module provides comprehensive information about Factorio entities,
items, recipes and their relationships.
"""
#TODO: It should be replaced by another agent to search the information from the internet or the local database.

ENTITY_TYPES = {
    "production": ["assembling-machine", "furnace", "mining-drill"],
    "logistics": ["transport-belt", "splitter", "underground-belt", "inserter", "chest"],
    "energy": ["boiler", "steam-engine", "offshore-pump","pump", "pipe", "pipe-to-ground" ,"solar-panel", "accumulator", "electric-pole"],
    "defense": ["wall", "turret"],
    "resource": ["coal", "iron-ore", "copper-ore", "stone", "wood"],
    "fish": ["fish"],
}

ENTITIES = {
    "fish": {
        "type": "fish",
    },
    "coal": {
        "type": "resource",
        "resource_categories": ["basic-solid"],
    },
    "iron-ore": {
        "type": "resource",
        "resource_categories": ["basic-solid"],
    },
    "copper-ore": {
        "type": "resource",
        "resource_categories": ["basic-solid"],
    },
    "stone": {
        "type": "resource",
        "resource_categories": ["basic-solid"],
    },
    "wood": {
        "type": "resource",
        "resource_categories": ["basic-solid"],
    },
    "stone-furnace": {
        "type": "furnace",
        "crafting_categories": ["smelting"],
        "energy_source": "burner",
    },
    "electric-furnace": {
        "type": "furnace",
        "crafting_categories": ["smelting"],
        "energy_source": "electric",
    },
    "burner-mining-drill": {
        "type": "mining-drill",
        "resource_categories": ["basic-solid"],
        "energy_source": "burner",
    },
    "electric-mining-drill": {
        "type": "mining-drill",
        "resource_categories": ["basic-solid"],
        "energy_source": "electric",
    },
    "assembling-machine-1": {
        "type": "assembling-machine",
        "crafting_categories": ["crafting"],
        "energy_source": "electric",
    },
    "burner-inserter": {
        "type": "inserter",
        "energy_source": "burner",
    },
    "long-handed-inserter": {
        "type": "inserter",
        "energy_source": "electric",
    },
    "fast-inserter": {
        "type": "inserter",
        "energy_source": "electric",
    },
    "transport-belt": {
        "type": "transport-belt",
        "dimensions": 1*1,
        "speed": "15 items/s"
    },
    "wooden-chest": {
        "type": "chest",
        "inventory_size": 16
    },
    "iron-chest": {
        "type": "chest",
        "inventory_size": 32
    },
    "steel-chest": {
        "type": "chest",
        "inventory_size": 48
    },
    "small-electric-pole": {
        "type": "electric-pole",
        "supply_area_size": 5.0*5.0,
        "wire_reach_distance": 7.5
    },
    "medium-electric-pole": {
        "type": "electric-pole",
        "supply_area_size": 7.0*7.0,
        "wire_reach_distance": 9.0
    },
    "big-electric-pole": {
        "type": "electric-pole",
        "supply_area_size": 16.0*16.0,
        "wire_reach_distance": 32.0
    },
    "substation": {
        "type": "electric-pole",
        "supply_area_size": 18.0*18.0,
        "wire_reach_distance": 18.0
    },
    "pipe": {
        "type": "pipe",
        "fluid_storage_volume": 100,
        "dimensions": 1*1
    },
    "pipe-to-ground": {
        "type": "pipe-to-ground",
        "fluid_storage_volume": 100,
        "max_distance": 10,
        "dimensions": 1*1
    },
    "pump": {
        "type": "pump",
        "fluid_storage_volume": 400,
        "dimensions": 1*2
    },
    "boiler": {
        "type": "boiler",
        "energy_source": "burner",
        "fluid_storage_volume": {"input": 200, "output": 200},
        "dimensions": 2*3,
        "energy_consumption": "1.8MW",
        "fluid_consumption": "6/s",
        "pollution": "30/m"
    },
    "steam-engine": {
        "type": "generator",
        "fluid_storage_volume": 200,
        "dimensions": 3*5,
        "power_output": "900kW",
        "fluid_consumption": "30/s",
        "pollution": "N/A"
    },
    "solar-panel": {
        "type": "solar-panel",
        "dimensions": 3*3,
        "power_output": {"full daylight": "60kW", "average": "42kW"},
        "description": """A single (normal quality) solar panel outputs an average of 42 kW over a day on Nauvis and requires 0.84672 accumulators to sustain a constant power output through the night.
It takes approximately 23.8 solar panels to operate 1 MW of factory and charge 20.2 accumulators to sustain that 1 MW through the night.
The optimal ratio for normal quality solar panels to charge enough normal quality accumulators on Nauvis is 2646 accumulators for 3125 solar panels (supplying 42 kW per solar panel).
"""
    },
    "accumulator": {
        "type": "accumulator",
        "dimensions": 2*2,
        "energy_capacity": "5.0MJ",
        "energy_source": "electric",
        "power_input": "300kW",
        "power_output": "300kW"
    },
    "offshore-pump": {
        "type": "offshore-pump",
        "pumping_speed": 1200
    }
}

ITEMS = {
    "iron-plate": {
        "stack_size": 100,
        "fuel_value": None
    },
    "copper-plate": {
        "stack_size": 100,
        "fuel_value": None
    },
    "iron-ore": {
        "stack_size": 50,
        "fuel_value": None
    },
    "copper-ore": {
        "stack_size": 50,
        "fuel_value": None
    },
    "coal": {
        "stack_size": 50,
        "fuel_value": "8MJ"
    },
    "stone": {
        "stack_size": 50,
        "fuel_value": None
    },
    "wood": {
        "stack_size": 100,
        "fuel_value": "4MJ"
    },
    "iron-gear-wheel": {
        "stack_size": 100,
        "fuel_value": None
    },
    "electronic-circuit": {
        "stack_size": 200,
        "fuel_value": None
    },
    "advanced-circuit": {
        "stack_size": 200,
        "fuel_value": None
    },
    "steel-plate": {
        "stack_size": 100,
        "fuel_value": None
    },
    "stone-brick": {
        "stack_size": 100,
        "fuel_value": None
    },
    "copper-cable": {
        "stack_size": 200,
        "fuel_value": None
    }
}

RECIPES = {
    "iron-gear-wheel": {
        "ingredients": [{"iron-plate": 2}],
        "result": "iron-gear-wheel",
        "result_count": 1,
        "energy_required": 0.5,
        "category": "crafting"
    },
    "electronic-circuit": {
        "ingredients": [{"iron-plate": 1}, {"copper-cable": 3}],
        "result": "electronic-circuit",
        "result_count": 1,
        "energy_required": 0.5,
        "category": "crafting"
    },
    "copper-cable": {
        "ingredients": [{"copper-plate": 1}],
        "result": "copper-cable",
        "result_count": 2,
        "energy_required": 0.5,
        "category": "crafting"
    },
    "iron-plate": {
        "ingredients": [{"iron-ore": 1}],
        "result": "iron-plate",
        "result_count": 1,
        "energy_required": 3.2,
        "category": "smelting"
    },
    "copper-plate": {
        "ingredients": [{"copper-ore": 1}],
        "result": "copper-plate",
        "result_count": 1,
        "energy_required": 3.2,
        "category": "smelting"
    },
    "steel-plate": {
        "ingredients": [{"iron-plate": 5}],
        "result": "steel-plate",
        "result_count": 1,
        "energy_required": 16,
        "category": "smelting"
    },
    "stone-brick": {
        "ingredients": [{"stone": 2}],
        "result": "stone-brick",
        "result_count": 1,
        "energy_required": 3.2,
        "category": "smelting"
    },
    "burner-mining-drill": {
        "ingredients": [{"iron-gear-wheel": 3}, {"stone-furnace": 1}, {"iron-plate": 3}],
        "result": "burner-mining-drill",
        "result_count": 1,
        "energy_required": 2,
        "category": "crafting"
    },
    "stone-furnace": {
        "ingredients": [{"stone": 5}],
        "result": "stone-furnace",
        "result_count": 1,
        "energy_required": 0.5,
        "category": "crafting"
    }
}

def get_entity_names():
    """Get the list of valid entity names"""
    return list(ENTITIES.keys())

def get_entity_by_type(entity_type):
    """Get the list of entities of the specified type"""
    return [name for name, data in ENTITIES.items() if data["type"] == entity_type]

def get_item_names():
    """Get the list of valid item names"""
    return list(ITEMS.keys())

def get_recipe_names():
    """Get the list of valid recipe names"""
    return list(RECIPES.keys())

def get_recipe_for_item(item_name):
    """Get the recipe for the specified item"""
    for recipe_name, recipe in RECIPES.items():
        if recipe["result"] == item_name:
            return recipe
    return None

def get_entity_info(entity_name):
    """Get the detailed information of the entity"""
    return ENTITIES.get(entity_name)

def get_item_info(item_name):
    """Get the detailed information of the item"""
    return ITEMS.get(item_name)

def is_valid_entity(name):
    """Check if the entity name is valid"""
    return name in ENTITIES

def is_valid_item(name):
    """Check if the item name is valid"""
    return name in ITEMS