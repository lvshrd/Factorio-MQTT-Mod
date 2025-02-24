import time
import os
import json
from paho.mqtt import client as mqtt_client

FACTORY_STATE_FILE = "C:/Users/Your-user/AppData/Roaming/Factorio/script-output/factory_state.json" # change this to your own path
BROKER = "localhost" # change this to your MQTT broker IP
PORT = 1883 # change this to your MQTT broker port
TOPIC_PREFIX = "factorio" # change this to your desired MQTT topic prefix

# Keep track of last published values for each subtopic, so we only publish if changed
last_published = {}

def publish_if_changed(client, subtopic, new_payload):
    """
    Publish 'new_payload' to 'subtopic' only if 'new_payload' differs
    from the last published payload for this subtopic.
    """
    old_payload = last_published.get(subtopic)
    if old_payload != new_payload:
        client.publish(subtopic, new_payload)
        last_published[subtopic] = new_payload

def publish_json(client, subtopic, value):
    """
    Convert 'value' to a valid JSON string via json.dumps(...),
    then publish if changed.
    """
    payload = json.dumps(value)  # always a valid JSON representation
    publish_if_changed(client, subtopic, payload)

# 1) Category map
TYPE_TO_CATEGORY = {
    "assembling-machine": "machines",
    "furnace":            "machines",
    "mining-drill":       "machines",
    "boiler":             "machines",   # Added boiler
    "pump":               "machines",   # Added pump
    "generator":          "machines",   # Added generator (steam engine)
    
    "container":          "storage",
    "logistic-container": "storage",
    "car":                "storage",
    "cargo-wagon":        "storage",
    "fluid-wagon":        "storage",
    "locomotive":         "storage",
    "spider-vehicle":     "storage",
    "roboport":           "storage",
}


# 2) Factorio 2.0 bitmask status definitions
STATUS_FLAGS = {
    1:    "working",
    2:    "no_power",
    4:    "no_fuel",
    8:    "low_power",
    16:   "no_minable_resources",
    32:   "disabled_by_control_behavior",
    64:   "disabled_by_script",
    128:  "item_ingredient_shortage",
    256:  "fluid_ingredient_shortage",
    512:  "full_output",
    1024: "no_research_in_progress",
}
STATUS_PRIORITY = [
    (1024, "No Research In Progress"),
    (512,  "Output Full"),
    (8,    "Low Power"),
    (64,   "Disabled by Script"),
    (32,   "Target Full"),
    (256,  "Fluid Shortage"),
    (128,  "Item Shortage"),
    (16,   "No Resources"),
    (2,    "No Power"),
    (4,    "No Fuel"),
    (1,    "Working")
]


def decode_all_flags(status_int):
    flags = []
    for bit_value, name in STATUS_FLAGS.items():
        if (status_int & bit_value) != 0:
            flags.append(name)
    if not flags:
        flags.append("none")
    return flags

def decode_dominant_flag(status_int):
    for bit_val, label in STATUS_PRIORITY:
        if (status_int & bit_val) != 0:
            return label
    return "none"

def connect_mqtt():
    client = mqtt_client.Client("factorio_publisher")
    client.connect(BROKER, PORT, keepalive=60)
    return client

def publish_asset_list(client, asset_groups):
    """
    For each (category, type_slug), publish the array of IDs (as JSON).
    E.g. factorio/machines/mining_drill => '[{"id":14},{"id":20}]'
    """
    for (category, type_slug), id_list in asset_groups.items():
        topic = f"{TOPIC_PREFIX}/{category}/{type_slug}"
        # 'id_list' is a Python list like: [ {"id":14}, {"id":20} ]
        publish_json(client, topic, id_list)

def publish_asset_data(client, asset):
    """
    Publish data for a single asset to multiple subtopics:
      factorio/<category>/<type_slug>/<id>/<subtopic>
    All values are JSON-encoded for correct parsing.

    'unit_number' -> 'id'
    """
    asset_id = asset.get("id", asset.get("unit_number", "unknown_id"))
    asset["id"] = asset_id

    asset_type = asset.get("type", "unknown")
    category   = TYPE_TO_CATEGORY.get(asset_type, "other")
    type_slug  = asset_type.replace('-', '_')

    base_topic = f"{TOPIC_PREFIX}/{category}/{type_slug}/{asset_id}"

    # 1) Basic info
    publish_json(client, f"{base_topic}/id", str(asset_id))
    publish_json(client, f"{base_topic}/name", asset.get("name", "unknown_name"))
    publish_json(client, f"{base_topic}/model", asset.get("model", "unknown_model"))
    publish_json(client, f"{base_topic}/type", asset_type)
    publish_json(client, f"{base_topic}/position", asset.get("position", {}))

    # 2) Status
    raw_status = asset.get("last_status", 0)
    dominant   = decode_dominant_flag(raw_status)
    all_flags  = decode_all_flags(raw_status)

    publish_json(client, f"{base_topic}/status", dominant)
    publish_json(client, f"{base_topic}/status_bitmask", raw_status)
    publish_json(client, f"{base_topic}/status_flags", all_flags)

    # state_changed_tick
    state_changed_tick = asset.get("state_changed_tick", 0)
    publish_json(client, f"{base_topic}/state_changed_tick", state_changed_tick)

    # 3) Production
    production_count       = asset.get("production_count", 0)
    production_last_update = asset.get("production_last_updated", 0)
    publish_json(client, f"{base_topic}/production/count", production_count)
    publish_json(client, f"{base_topic}/production/last_updated", production_last_update)

    # 4) Pollution
    pollution_value = asset.get("pollution", 0.0)
    publish_json(client, f"{base_topic}/pollution", pollution_value)

    # 5) Inventory can be either a dict or a list, so handle both cases
    inventory = asset.get("inventory", {})
    inventory_topic_prefix = f"{base_topic}/inventory"
    if isinstance(inventory, dict):
        for inv_label, stack_list in inventory.items():
            publish_json(client, f"{inventory_topic_prefix}/{inv_label}", stack_list)
    elif isinstance(inventory, list):
        publish_json(client, f"{inventory_topic_prefix}", inventory)
    else:
        publish_json(client, f"{inventory_topic_prefix}", str(inventory))


    # 6) Fluids
    fluids = asset.get("fluids", [])
    # If you want each fluid box in a single array, you can do:
    # publish_json(client, f"{base_topic}/fluids", fluids)
    # Or individually:
    for i, fluid in enumerate(fluids):
        fluid_topic = f"{base_topic}/fluids/box_{i}"
        publish_json(client, fluid_topic, fluid if fluid else "empty")

def main():
    client = connect_mqtt()
    client.loop_start()

    last_mtime = 0

    while True:
        time.sleep(2)
        if not os.path.exists(FACTORY_STATE_FILE):
            continue

        mtime = os.path.getmtime(FACTORY_STATE_FILE)
        if mtime > last_mtime:
            last_mtime = mtime
            # file changed, read new snapshot
            try:
                with open(FACTORY_STATE_FILE, "r") as f:
                    data = json.load(f)

                # data: {"tick": ..., "assets": [...]}
                assets = data.get("assets", [])
                if not isinstance(assets, list):
                    print("Error: data['assets'] is not a list.")
                    continue

                # 1) Build dict grouping by (category, type_slug) -> list of { "id": ... }
                asset_groups = {}
                for asset in assets:
                    a_type     = asset.get("type", "unknown")
                    category   = TYPE_TO_CATEGORY.get(a_type, "other")
                    type_slug  = a_type.replace('-', '_')
                    asset_id   = asset.get("id", asset.get("unit_number", "unknown_id"))

                    key = (category, type_slug)
                    if key not in asset_groups:
                        asset_groups[key] = []
                    asset_groups[key].append({"id": asset_id})

                # 2) Publish array of IDs for each (category,type_slug)
                publish_asset_list(client, asset_groups)

                # 3) Publish subtopics for each asset
                for asset in assets:
                    publish_asset_data(client, asset)

            except Exception as e:
                print("Error parsing factory_state.json:", e)

if __name__ == "__main__":
    main()
