import logging
import json
import requests
from typing import Text, List, Any, Dict

from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
)

from actions.config import get_config
from actions.api import Zomato
from actions.exceptions import (
    KeyNotInConfigError,
    InvalidCityId,
    InvalidRestaurantId,
    InvalidCityName,
    StringNotNumeric,
    RequestFailedError
)


logger = logging.getLogger(__name__)

config = get_config()
zomato = Zomato(config)

base_url = "https://developers.zomato.com/api/v2.1/"

class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        name = tracker.get_slot("name")
        if name is not None:
            dispatcher.utter_message(template="utter_greet_name")
        else:
            dispatcher.utter_message(template="utter_greet")

        return []


class ValidateRestaurantForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_restaurant_form"

    @staticmethod
    def cuisine_db() -> List[Text]:
        """Database of supported cuisines"""
        
        supported_cuisines = ["mexican", "chinese", "italian", "american", "south indian", "north indian"]
        return supported_cuisines

    def validate_cuisine(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if slot_value.lower() in self.cuisine_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"cuisine": slot_value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            dispatcher.utter_message(template="utter_cuisine_denied")
            dispatcher.utter_message(text = "Try again!")

            return {"cuisine": None}

    def validate_location(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        try:
            logger.info("calling Zomato /locations API with location - '%s'", slot_value)
            
            location_details = zomato.get_location(slot_value)
            
            logger.info(json.dumps(location_details, sort_keys=False, indent=4))
        
            return {"location": slot_value}
        
        except RequestFailedError(base_url, slot_value) as e:
            logger.error(
                "Failed to obtain location details. Error: {}" "".format(e.message),
                exc_info=True,
            )
            dispatcher.utter_message(template="utter_location_denied")
            dispatcher.utter_message(text = "Try again!")
        
            return {"location": None}


def get_filtered_cuisines(supported_cuisines, city_id) -> dict:
    assert(len(supported_cuisines) > 0)

    logger.info("calling Zomato /cuisines API with city_id - '%d'", city_id)

    response_cuisines = zomato.get_cuisines(city_id)

    filtered_cuisines = {
        key: value
        for key, value in response_cuisines.items()
        if value in supported_cuisines
    }

    logger.info(json.dumps(filtered_cuisines, sort_keys=False, indent=4))

    return filtered_cuisines

class ActionRestaurantSearch(Action):
    def name(self) -> Text:
        return "action_restaurant_search"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        location = tracker.get_slot("location")
        cuisine = tracker.get_slot("cuisine")


        logger.info("calling Zomato /locations API with location - '%s'", location)
        location_details = zomato.get_location(location)
        logger.info(json.dumps(location_details, sort_keys=False, indent=4))

        supported_cuisines = ["mexican", "chinese", "italian", "american", "south indian", "north indian"]
        filtered_cuisines = get_filtered_cuisines(supported_cuisines, city_id=location_details["city_id"])

        cuisine_list = [
            key
            for key, value in filtered_cuisines.items()
            if str(value).lower() == cuisine.lower()
        ]

        logger.info(
            "calling Zomato /search API with '%s' location and '%s' cuisine",
            location,
            cuisine,
        )

        try:
            restaurant_ids = zomato.restaurant_search(
                query=location,
                latitude=location_details["latitude"],
                longitude=location_details["longitude"],
                cuisines=cuisine_list,
                entity_id=location_details["city_id"],
                entity_type=location_details["entity_type"]
            )

        except RequestFailedError(base_url, slot_value) as e:
            logger.error(
                "Failed to obtain restaurant details. Error: {}" "".format(e.message),
                exc_info=True,
            )
            dispatcher.utter_message(template="utter_no_results_found")
            dispatcher.utter_message(text = "Try again!")

            return [SlotSet("restaurant_search_sucess", False)]
        
        except RestaurantSearchNoneFindError:
            dispatcher.utter_message(template="utter_showing_all_restaurants")
            restaurant_ids = zomato.restaurant_search(
                query=location,
                latitude=location_details["latitude"],
                longitude=location_details["longitude"],
                entity_id=location_details["city_id"],
                entity_type=location_details["entity_type"]
            )

        restaurants_found = []

        response = "Showing you 5 top rated restaurants:" + "\n"

        for cnt, res_id in enumerate(restaurant_ids):
            restaurant_info = zomato.get_restaurant(res_id)
            response += str(cnt+1) + ". Name: " + restaurant_info["name"] + ", location: " +\
                        restaurant_info["location"] + ", City: " + restaurant_info["city"] +\
                        ", User Rating: " + restaurant_info["user_rating"] + "\n"

            restaurants_found.append(restaurant_info)

        logger.info(json.dumps(restaurants_found, sort_keys=False, indent=4))
        
        dispatcher.utter_message(text=response)

        return [SlotSet("restaurant_search_sucess", True)]
