#!/usr/bin/env python3
"""
Factorio MQTT Subscriber

This script subscribes to MQTT topics from Node-RED agent workflow and 
executes the corresponding actions in the Factorio game.
"""
import time
import json
import logging
import toml
from paho.mqtt import client as mqtt_client
from api.factorio_interface import FactorioInterface
from typing import Optional
import os

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='factorio_mqtt.log'
)
logger = logging.getLogger('factorio_mqtt')

class FactorioMQTTSubscriber:
    def __init__(self, config_path: str = "config.toml"):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "config.toml")
            self.config = toml.load(config_path)
        except Exception as e:
            print(f"Error loading config.toml: {e}")
            exit(1)
        self.mqtt_config = self.config.get("mqtt", {})
        self.factorio: Optional[FactorioInterface] = None
        self.client = None
        self.retry_interval = 5  # retry interval (seconds)
        self.max_retries = 3      # maximum retry attempts

    def initialize_factorio(self) -> bool:
        """Initialize Factorio connection with retry mechanism"""
        retries = 0
        while retries < self.max_retries:
            try:
                self.factorio = FactorioInterface(
                    self.config["rcon"]["host"],
                    self.config["rcon"]["port"],
                    self.config["rcon"]["password"]
                )
                print("Successfully connected to Factorio server")
                return True
            except Exception as e:
                retries += 1
                if retries < self.max_retries:
                    print(f"Failed to connect to Factorio server (attempt {retries}/{self.max_retries}): {e}")
                    print(f"Retrying in {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                else:
                    logger.error(f"Failed to connect to Factorio server after {self.max_retries} attempts: {e}")
                    print(f"Failed to connect to Factorio server after {self.max_retries} attempts: {e}")
                    return False

    def on_connect(self, client, userdata, flags, rc):
        """MQTT connect callback"""
        if rc == 0:
            # Subscribe to both topics
            client.subscribe(self.mqtt_config.get("command_topic", "Factorio/Commands"))
            client.subscribe(self.mqtt_config.get("plan_topic", "Factorio/Plans"))
            logger.info("Subscribed to topics: Factorio/Commands and Factorio/Plans")
        else:
            logger.error(f"Failed to connect to MQTT Broker, return code {rc}")

    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            # Handle plan topic messages
            if msg.topic == self.mqtt_config.get("plan_topic", "Factorio/Plans"):
                plan_bytes = msg.payload
                try:
                    plan_str = plan_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    plan_str = str(plan_bytes)  # Fallback to raw bytes representation if UTF-8 fails
                log = f"Agent's plan: {plan_str}"
                logger.info(log)
                print(log)
                return
            
            payload = json.loads(msg.payload.decode())
            log = f"Received from {msg.topic}: {payload}"
            logger.info(log)
            print(log)
            # Handle command topic messages
            command = payload.get("command")
            params = payload.get("params", {})
            
            if command == "get_player_position":
                result = self.factorio.get_player_position()
                self.publish_result(client, command, result)
            
            elif command == "move_player":
                x = params.get("x")
                y = params.get("y")
                result = self.factorio.move_player(x, y)
                self.publish_result(client, command, result)
            
            elif command == "place_entity":
                name = params.get("name")
                x = params.get("x")
                y = params.get("y")
                direction = params.get("direction", 0)
                result = self.factorio.place_entity(name, x, y, direction)
                self.publish_result(client, command, result)
            
            elif command == "remove_entity":
                name = params.get("name")
                x = params.get("x")
                y = params.get("y")
                result = self.factorio.remove_entity(name, x, y)
                self.publish_result(client, command, result)
            
            elif command == "search_entities":
                name = params.get("name")
                entity_type = params.get("type")
                radius = params.get("radius", 10)
                position_x = params.get("position_x")
                position_y = params.get("position_y")
                limit = params.get("limit", 25)
                result = self.factorio.search_entities(name, entity_type, position_x, position_y, radius, limit=limit)
                self.publish_result(client, command, result)
            
            elif command == "get_inventory":
                entity = params.get("entity", "player")
                x = params.get("x")
                y = params.get("y")
                result = self.factorio.get_inventory(entity, x, y)
                self.publish_result(client, command, result)
            
            elif command == "insert_item":
                item = params.get("item")
                count = params.get("count")
                inventory_type = params.get("inventory_type", "main")
                entity = params.get("entity", "player")
                x = params.get("x")
                y = params.get("y")
                result = self.factorio.insert_item(item, count, inventory_type, entity, x, y)
                self.publish_result(client, command, result)
            
            elif command == "remove_item":
                item = params.get("item")
                count = params.get("count")
                entity = params.get("entity", "player")
                x = params.get("x")
                y = params.get("y")
                result = self.factorio.remove_item(item, count, entity, x, y)
                self.publish_result(client, command, result)
            
            elif command == "list_supported_entities":
                mode = params.get("mode", "all")
                search_type = params.get("search_type")
                keyword = params.get("keyword")
                result = self.factorio.list_supported_entities(mode, search_type, keyword)
                self.publish_result(client, command, result)
            
            elif command == "list_supported_items":
                result = self.factorio.list_supported_items()
                self.publish_result(client, command, result)

            elif command == "find_surface_tile":
                name = params.get("name")
                position_x = params.get("position_x")
                position_y = params.get("position_y")
                radius = params.get("radius", 10)
                limit = params.get("limit", 25)
                result = self.factorio.find_surface_tile(name, position_x, position_y, radius, limit=limit)
                self.publish_result(client, command, result)
                
            else:
                logger.warning(f"Unknown command: {command}")
                self.publish_result(client, command, {"error": f"Unknown command: {command}"}, success=False)
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            self.publish_result(client, "error", {"error": str(e)}, success=False)

    def publish_result(self, client, command, result, success=True):
        """Publish the result of a command"""
        response_topic = self.mqtt_config.get("response_topic", "Factorio/Responses")
        payload = {
            "command": command,
            "result": result
        }
        client.publish(response_topic, json.dumps(payload))
        log = f"Published feedback: {command}: {result}\n"
        logger.info(log)
        print(log)

    def run(self):
        """Run MQTT subscriber"""
        if not self.initialize_factorio():
            return

        client_id = self.mqtt_config.get("client_id", "factorio_subscriber")
        broker = self.mqtt_config.get("broker", "localhost")
        port = self.mqtt_config.get("port", 1883)
        username = self.mqtt_config.get("username", "")
        password = self.mqtt_config.get("password", "")
        
        self.client = mqtt_client.Client(client_id=client_id)
        
        if username and password:
            self.client.username_pw_set(username, password)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(broker, port)
            logger.info(f"Connected to MQTT broker: {broker}:{port}")
            print(f"Connected to MQTT broker: {broker}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            print(f"Failed to connect to MQTT broker: {e}")
            return
        
        self.client.loop_start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Subscriber stopped by user")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")

def main():
    subscriber = FactorioMQTTSubscriber()
    subscriber.run()

if __name__ == "__main__":
    main()