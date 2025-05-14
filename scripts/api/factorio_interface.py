"""
Factorio Interface Module

This module provides a high-level interface for interacting with a Factorio server
through RCON. It wraps the base API commands and handles the RCON connection,
command execution, and response parsing.
"""

import json
import logging
from typing import Optional, List, Dict, Any, Union, Tuple
import factorio_rcon as rcon
from api.sandbox.base import FactorioAPI
from api.prototype import get_entity_names, get_item_names, is_valid_entity, is_valid_item

# Configure logging
logger = logging.getLogger('factorio_interface')

class FactorioInterface:
    """
    High-level interface for interacting with a Factorio server through RCON.
    Wraps the base API commands and handles the RCON connection, command execution,
    and response parsing.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8088, password: str = "lvshrd"):
        """
        Initialize the Factorio interface.
        
        Args:
            host: RCON server hostname or IP address
            port: RCON server port
            password: RCON password
        """
        self.rcon_client = rcon.RCONClient(host, port, password)
        self.api = FactorioAPI()
        self._send_command("game.print('Hello, World!')")
    
    def _send_command(self, command: str) -> str:
        """
        Send a command to the Factorio server and return the response.
        
        Args:
            command: The command to send
            
        Returns:
            str: The server response
        """
        with self.rcon_client as client:
            response = client.send_command(command)
            return response if response else ""
    
    def _parse_json_response(self, response: str) -> Union[Dict, List, None]:
        """
        Parse a JSON response from the Factorio server.
        
        Args:
            response: The response string from the server
            
        Returns:
            Union[Dict, List, None]: Parsed JSON data or None if parsing fails
        """
        if not response:
            return None
            
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If it's not valid JSON, return the original string
            logger.warning(f"Failed to parse response as JSON: {response}")
            return None
    
    def _parse_success_response(self, response: str) -> Tuple[bool, str]:
        """
        Parse a success/failure response from the Factorio server.
        
        Args:
            response: The response string from the server
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not response:
            return False, "Something went wrong"
            
        if response.startswith("Success:"):
            return True, response[9:].strip()
        elif response.startswith("Failed:"):
            return False, response[8:].strip()
        else:
            return True, response
    
    # Player-related methods
    def get_player_position(self) -> Optional[Dict[str, float]]:
        """
        Get the player's current position.
        
        Returns:
            Optional[Dict[str, float]]: A dictionary with 'x' and 'y' coordinates or None if failed
        """
        command = self.api.Player.get_player_position()
        response = self._send_command(command)
        
        # Response format is typically: {x = 123.45, y = 678.90}
        if response:
            try:
                # Extract x and y values using string manipulation
                response = response.strip("{}")
                parts = response.split(",")
                position = {}
                for part in parts:
                    key, value = part.split("=")
                    position[key.strip()] = float(value.strip())
                return position
            except Exception as e:
                logger.error(f"Error parsing position response: {e}")
        
        return None
    
    def move_player(self, x: float, y: float) -> bool:
        """
        Move the player to a specific position.
        
        Args:
            x: The x coordinate
            y: The y coordinate
            
        Returns:
            bool: True if successful, False otherwise
        """
        command = self.api.Player.move_to(x, y)
        response = self._send_command(command)
        return bool(response) or response == ""
    
    # Entity-related methods
    def search_entities(self, 
                    name: Optional[Union[str, List[str]]] = None,
                    type: Optional[str] = None,
                    position_x: Optional[float] = None,
                    position_y: Optional[float] = None,
                    radius: Optional[float] = None,
                    bottom_left_x: Optional[float] = None,
                    bottom_left_y: Optional[float] = None,
                    top_right_x: Optional[float] = None,
                    top_right_y: Optional[float] = None,
                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search entities in the current game based on specified filters.
        
        Args:
            name: Entity prototype name(s) to filter by
            type: Entity type to filter by
            position_x: X coordinate of the center of the search circle
            position_y: Y coordinate of the center of the search circle
            radius: Radius of the search circle
            bottom_left_x: Bottom-left X coordinate of the search area
            bottom_left_y: Bottom-left Y coordinate of the search area
            top_right_x: Top-right X coordinate of the search area
            top_right_y: Top-right Y coordinate of the search area
            limit: Maximum number of entities to return
            
        Returns:
            List[Dict[str, Any]]: List of entity data dictionaries
        """
        if not is_valid_entity(name):
            return f"Failed: Invalid entity name: {name}"
        command = self.api.Entity.search_entities(
            name=name, type=type, 
            position_x=position_x, position_y=position_y, radius=radius,
            bottom_left_x=bottom_left_x, bottom_left_y=bottom_left_y,
            top_right_x=top_right_x, top_right_y=top_right_y,
            limit=limit
        )
        response = self._send_command(command)
        entities = self._parse_json_response(response)
        return entities if entities else []
    
    def place_entity(self, name: str, x: float, y: float, direction: int = 0) -> Tuple[bool, str]:
        """
        Place an entity in the game surface.
        
        Args:
            name: The entity prototype name to create
            x: The x coordinate
            y: The y coordinate
            direction: The direction (0, 4, 8, 12 for N, E, S, W)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not is_valid_entity(name):
            return False, f"Invalid entity name: {name}"
        command = self.api.Entity.place_entity(name, x, y, direction)
        response = self._send_command(command)
        return self._parse_success_response(response)
    
    def remove_entity(self, name: str, x: float, y: float) -> Tuple[bool, str]:
        """
        Remove an entity from the game surface.
        
        Args:
            name: The entity prototype name to remove
            x: The x coordinate
            y: The y coordinate
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        command = self.api.Entity.remove_entity(name, x, y)
        response = self._send_command(command)
        return self._parse_success_response(response)
    
    # Inventory-related methods
    def insert_item(self, item: str, count: int, 
                   inventory_type: str = "character_main", 
                   entity: str = "player", 
                   x: Optional[float] = None, 
                   y: Optional[float] = None) -> Tuple[bool, str]:
        """
        Insert items into an inventory.
        
        Args:
            item: The item name to insert
            count: The count of the item
            inventory_type: The type of inventory to insert into
            entity: The name of the entity to insert into
            x: The x coordinate of the entity (if not player)
            y: The y coordinate of the entity (if not player)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # if not is_valid_item(item):
        #     return False, f"Invalid item name: {item}"
            
        command = self.api.Inventory.insert_item(item, count, inventory_type, entity, x, y)
        response = self._send_command(command)
        return self._parse_success_response(response)
    
    def remove_item(self, item: str, count: int, 
                   entity: str = "player", 
                   x: Optional[float] = None, 
                   y: Optional[float] = None) -> Tuple[bool, str]:
        """
        Remove items from an inventory.
        
        Args:
            item: The item name to remove
            count: The count of the item
            entity: The name of the entity to remove from
            x: The x coordinate of the entity (if not player)
            y: The y coordinate of the entity (if not player)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not is_valid_item(item):
            return False, f"Invalid item name: {item}"
            
        command = self.api.Inventory.remove_item(item, count, entity, x, y)
        response = self._send_command(command)
        return self._parse_success_response(response)
    
    def get_inventory(self, inventory_type: str = "character_main", 
                     entity: str = "player", 
                     x: Optional[float] = None, 
                     y: Optional[float] = None) -> Dict[str, int]:
        """
        Get inventory contents.
        
        Args:
            inventory_type: The type of inventory to get
            entity: The name of the entity to get from
            x: The x coordinate of the entity (if not player)
            y: The y coordinate of the entity (if not player)
            
        Returns:
            Dict[str, int]: Dictionary mapping item names to counts
        """
        command = self.api.Inventory.get_inventory(inventory_type, entity, x, y)
        response = self._send_command(command)
        inventory = self._parse_json_response(response)
        return inventory if inventory else {}

    def list_supported_entities(self, mode: str = "all", search_type: str = None, keyword: str = None):
        """
        Get supported entities based on different search modes.
        
        Args:
            mode: Search mode - "all" for all entities names, "type" for entities of specific type with info,
                 "search" for keyword search with info
            search_type: When mode="type", specify the entity type to filter
            keyword: When mode="search", specify the keyword to search entity names
            
        Returns:
            List of entity names or Dict containing matched entity names and their info
        """
        from api.prototype import get_entity_names, get_entity_by_type, get_entity_info
        
        # Get all entities by default
        if mode == "all":
            result = get_entity_names()
                    
        # Filter by specific type
        elif mode == "type" and search_type:
            entity_names = get_entity_by_type(search_type)
            result = {name: get_entity_info(name) for name in entity_names}
            
        # Search by keyword
        elif mode == "search" and keyword:
            all_entities = get_entity_names()
            result = {}
            for name in all_entities:
                # Use fuzzy matching algorithm - fuzzywuzzy
                from fuzzywuzzy import fuzz
                similarity = fuzz.partial_ratio(keyword.lower(), name.lower())
                if similarity > 70:
                    result[name] = get_entity_info(name)
        else:
            result = {"error": "Invalid search parameters"}
            
        return result

    def list_supported_items(self):
        """Get all supported items"""
        from api.prototype import get_item_names, get_item_info
        
        items = get_item_names()
        return items

    def find_surface_tile(self, 
                    name: Optional[Union[str, List[str]]] = None,
                    position_x: Optional[float] = None,
                    position_y: Optional[float] = None,
                    radius: Optional[float] = None,
                    bottom_left_x: Optional[float] = None,
                    bottom_left_y: Optional[float] = None,
                    top_right_x: Optional[float] = None,
                    top_right_y: Optional[float] = None,
                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find the tile at the specified coordinates"""
        command = self.api.Surface.find_tiles_filtered(bottom_left_x, bottom_left_y, top_right_x, top_right_y, position_x, position_y, radius, name, limit)
        response = self._send_command(command)
        tiles = self._parse_json_response(response)
        return tiles if tiles else []