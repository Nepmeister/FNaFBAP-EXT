from typing import List

from BaseClasses import Tutorial, Location, LocationProgressType, CollectionState, MultiWorld, ItemClassification
from worlds.AutoWorld import WebWorld, World
from .Items import FNaFB2Item, FNaFB2ItemData, get_items_by_category, item_table
from .Locations import FNaFB2Location, location_table
from .Options import fnafb2_options
from .Regions import create_regions
from .Rules import set_rules


class FNaFB2Web(WebWorld):
    theme = "partyTime"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Five Nights at Fuckboy's 2 client for use with Archipelago.",
        "English",
        "fnafb2_en.md",
        "fnafb2/en",
        ["Scrungip"]
    )]


class FNaFB2World(World):
    """
    Are you Freddy for ready?
    """
    game = "Five Nights at Fuckboy's 2"
    option_definitions = fnafb2_options
    topology_present = True
    data_version = 4
    required_client_version = (0, 5, 0)
    web = FNaFB2Web()

    item_name_to_id = {name: data.code for name, data in item_table.items()}
    location_name_to_id = {name: data.code for name, data in location_table.items()}

    def get_setting(self, name: str):
        return getattr(self.multiworld, name)[self.player]

    def fill_slot_data(self) -> dict:
        return {option_name: self.get_setting(option_name).value for option_name in fnafb2_options}

    def create_items(self):
        item_pool: List[FNaFB2Item] = []
        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        for name, data in item_table.items():
            quantity = data.max_quantity
            category = data.category
            classification = data.classification

            # Ignore Interior Walls if it's not enabled.
            if name == "Reveal Interior Walls" and not self.get_setting("interior_walls"):
                continue

            # Remove one of each weapon type if Interior Walls is not active
            if name == "Progressive Microphone" and not self.get_setting("trade_quest" or "levelsanity" or "interior_walls"):
                quantity -= 1
            if name == "Progressive Guitar" and not self.get_setting("trade_quest" or "levelsanity" or "interior_walls"):
                quantity -= 1
            if name == "Progressive Cupcakes" and not self.get_setting("trade_quest" or "levelsanity" or "interior_walls"):
                quantity -= 1
            if name == "Progressive Hook" and not self.get_setting("trade_quest" or "levelsanity" or "interior_walls"):
                quantity -= 1
            if name == "Dragon Dildo" and not self.get_setting("levelsanity" or "interior_walls"):
                continue
            
            # Remove more unneccessary items when Interior Walls/Trade Quest is not active to make room for filler
            if category == "Armor" and classification == ItemClassification.useful and not self.get_setting("interior_walls"):
                continue
            if name == "Fazbear Combo" and not self.get_setting("interior_walls" or "levelsanity"):
                continue
            if name == "Flighty Combo" and not self.get_setting("interior_walls" or "levelsanity"):
                continue
            if name == "Bonbon Combo" and not self.get_setting("interior_walls" or "levelsanity"):
                continue
            if name == "Pirate Combo" and not self.get_setting("interior_walls" or "levelsanity"):
                continue
            if name == "Fearless Flight" and not self.get_setting("interior_walls" or "levelsanity"):
                continue
            if name == "Speed Share" and not self.get_setting("interior_walls" or "levelsanity"):
                continue

            # Ignore filler, it will be added in a later stage.
            if data.category == "Filler":
                continue

            item_pool += [self.create_item(name) for _ in range(0, quantity)]
        while len(item_pool) < total_locations:
            item_pool.append(self.create_item(self.get_filler_item_name()))

        self.multiworld.itempool += item_pool

    def get_filler_item_name(self) -> str:
        fillers = get_items_by_category("Filler")
        weights = [data.weight for data in fillers.values()]
        return self.multiworld.random.choices([filler for filler in fillers.keys()], weights, k=1)[0]

    def create_item(self, name: str) -> FNaFB2Item:
        data = item_table[name]
        return FNaFB2Item(name, data.classification, data.code, self.player)

    def create_regions(self):
        create_regions(self.multiworld, self.player)

    def set_rules(self):
        set_rules(self.multiworld, self.player)