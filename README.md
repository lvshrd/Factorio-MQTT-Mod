# Factorio MQTT Notify

This project contains:

1. A **Factorio 2.0 mod** (in `control.lua` & `info.json`) that periodically writes a JSON snapshot (`factory_state.json`) with:
   - Machine status
   - Inventories
   - Pollution
   - Fluid info
   - Production counts

2. A **Python script** (`main.py`) that watches the generated `factory_state.json` and publishes updates to an MQTT broker with structured JSON messages.

## Author

- **Mario Gonsales Ishikawa** (GitHub: [marioishikawa](https://github.com/marioishikawa))  
  For Intellic Integration  
  Licensed under the [Apache 2.0 License](LICENSE).

## Installation & Usage

### Mod Installation

1. Copy or zip the `mqtt_notify` folder (with `control.lua` & `info.json`) into your Factorio `mods` directory.  
2. Ensure your Factorio version is **2.0** or compatible with no direct `write_file` restrictions.  

### Python Script

1. Install Python 3.  
2. From this folder, create a virtual environment (optional) and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Edit `main.py` if needed:
   - `FACTORY_STATE_FILE` points to your `script-output/factory_state.json`.
   - `BROKER` and `PORT` to your MQTT broker settings.

4. Run `main.py`:
   ```bash
   python main.py
   ```
   It will monitor the Factorio JSON file and publish MQTT messages at `factorio/<category>/<type>/<id>/...`.

## Mod Behavior

- When Factorio starts or loads, the mod scans for existing tracked entities (assembling machines, furnaces, mining drills, containers, etc.).
- Every 1 second (60 ticks), it updates:
  - Production progress
  - Inventories
  - Status (bitmask integer)
  - Pollution, fluids
- Writes `script-output/factory_state.json`.

The JSON file has a structure like:

```json
{
  "tick": 123456,
  "assets": [
    {
      "unit_number": 14,
      "name": "assembling-machine-2",
      "type": "assembling-machine",
      "last_status": 53
    }
  ]
}
```

The Python script picks this up and publishes to MQTT.

## Modifying

- **Entity Types**: If you want to track belts, inserters, etc., add them to `TRACKED_TYPES` in `control.lua`.
- **MQTT Topic Structure**: Edit `publish_asset_data()` in `main.py` if you want different subtopic naming.

## Known issues

- Machine state is not correctly identifying the downtime state, due to the lack of proper information on the API documentation.

## License

This project is licensed under Apache License 2.0.
