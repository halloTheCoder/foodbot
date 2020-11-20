"""
    Test ZOMATO developer API endpoints from CLI

    API : /locations
    CMD :  python action_api_test.py --type LOCATION -l seattle
    OUTPUT : 
        {
            "city_id": 279,
            "city_name": "Seattle",
            "country_id": 216,
            "country_name": "United States",
            "entity_id": 279,
            "entity_type": "city",
            "latitude": 47.60577,
            "longitude": -122.329437,
            "title": "Seattle, Washington State"
        }

    API : /cuisines
    CMD : python action_api_test.py --type CUISINE --location bangalore
    OUTPUT :
        {
            "1": "American",
            "25": "Chinese",
            "50": "North Indian",
            "55": "Italian",
            "73": "Mexican",
            "85": "South Indian"
        }

    API : /search
    CMD : python action_api_test.py --type SEARCH --location new york --cuisine mexican
    OUTPUT :
        [
            {
                "address": "32 Spring Street, New York 10012",
                "avg_cost_for_2": 50,
                "name": "Lombardi's Pizza",
                "rating": "4.9"
            },
            {
                "address": "205 East Houston Street, New York 10002",
                "avg_cost_for_2": 30,
                "name": "Katz's Delicatessen",
                "rating": "4.9"
            },
            {
                "address": "179 E Houston Street, New York 10002",
                "avg_cost_for_2": 25,
                "name": "Russ & Daughters",
                "rating": "4.9"
            },
            {
                "address": "65 4th Avenue, New York 10003",
                "avg_cost_for_2": 40,
                "name": "Ippudo",
                "rating": "4.9"
            },
            {
                "address": "Madison Square Park, 23rd & Madison, New York 10010",
                "avg_cost_for_2": 30,
                "name": "Shake Shack",
                "rating": "4.9"
            }
        ]

"""

import argparse
import sys

import json
import logging

from actions.api import Zomato
from actions.config import get_config


logger = logging.getLogger("__name__")
config = get_config()

_zomato = Zomato(config)


def test_location_search(location="") -> dict:
    location_details = _zomato.get_location(location)
    # location_details = {}

    # if response is not None:
    #     response_json = json.loads(response)
    #     if response_json["status"] == "success":
    #         location_details = response_json["location_suggestions"][0]

    logger.info("calling Zomato /locations API with location - '%s'", location)
    logger.info(json.dumps(location_details, sort_keys=True, indent=4))

    return location_details


def test_cuisine_search(location="", city_id=0) -> dict:
    response_cuisine = {}
    filtered_cuisine = {}

    if city_id is None or city_id == 0:
        location_details = test_location_search(location)
        city_id = location_details["city_id"]

    response_cuisine = _zomato.get_cuisines(city_id)
    supported_cuisines = [
        "American",
        "Chinese",
        "Italian",
        "Mexican",
        "North Indian",
        "South Indian",
    ]
    filtered_cuisine = {
        key: value
        for key, value in response_cuisine.items()
        if value in supported_cuisines
    }

    logger.info(
        "calling Zomato /cuisines API with location - '%s' or city_id - '%s'",
        location,
        city_id,
    )
    logger.info(json.dumps(filtered_cuisine, sort_keys=True, indent=4))

    return filtered_cuisine

def get_all_categories() -> dict:
    response_category = _zomato.get_categories()

    supported_categories = ['Dine-out', 'Delivery', 'Takeout', 'Cafes']

    filtered_category = {
        key: value
        for key, value in response_category.items()
        if value in supported_categories
    }

    return filtered_category



def test_restaurant_search(location="", cuisine="", category="") -> None:
    """
        Step 1 : retrieve details about the location
    """
    if location is not None:
        location_details = test_location_search(location=location)

        """
            Step 2 : Cuisine details
        """
        cuisine_details = test_cuisine_search(city_id=location_details["city_id"])
        if cuisine is not None:
            cuisine_list = [
                key
                for key, value in cuisine_details.items()
                if str(value).lower() == cuisine.lower()
            ]
        else:
            cuisine_list = [key for key, value in cuisine_details.items()]

        """
            Step 3 : Category details
        """
        # category_details = get_all_categories()
        # if category is not None:
        #     category_list = [
        #         key
        #         for key, value in category_details.items()
        #         if str(value).lower() == category.lower()
        #     ]
        # else:
        #     category_list = list(category_details.key())

        # _category = category_list[0]
        _category = ""

        """
            Step 4 : Search restaurants
        """
        logger.info(
            "calling Zomato /search API with '%s' location and '%s' cuisine",
            location,
            cuisine,
        )

        restaurant_ids = _zomato.restaurant_search(
            location,
            location_details["latitude"],
            location_details["longitude"],
            cuisine_list,
            _category,
            location_details["city_id"],
            location_details["entity_type"]
        )

        restaurants_found = []
        for res_id in restaurant_ids:
            restaurants_found.append(_zomato.get_restaurant(res_id))

        logger.info(json.dumps(restaurants_found, sort_keys=False, indent=4))


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        required=True,
        help="""LOCATION - to test /locations API
                CUISINE - to test /cuisines API 
                SEARCH - to test /search API """,
    )

    parser.add_argument(
        "-l",
        "--location",
        nargs="*",
        help="name of the city where you want to conduct your search in",
    )

    parser.add_argument("-c", "--cuisine", help="list of cuisines available in a city")

    # parser.add_argument("-a", "--category", help="list of categories available in a city")

    return parser


if __name__ == "__main__":
    parser = create_argument_parser()
    cmdline_arguments = parser.parse_args()

    test_type = (
        cmdline_arguments.type if cmdline_arguments.type is not None else "SEARCH"
    )
    location = (
        cmdline_arguments.location
        if cmdline_arguments.location is not None
        else "bangalore"
    )
    cuisine = (
        cmdline_arguments.cuisine
        if cmdline_arguments.cuisine is not None
        else "chinese"
    )
    # category = (
    #     cmdline_arguments.category
    #     if cmdline_arguments.category is not None
    #     else "Delivery"
    # )

    if test_type == "LOCATION":
        test_location_search(location=location)
    elif test_type == "CUISINE":
        test_cuisine_search(location=location)
    elif test_type == "SEARCH":
        # test_restaurant_search(location=location, cuisine=cuisine, category=category)
        test_restaurant_search(location=location, cuisine=cuisine)
