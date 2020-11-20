__all__ = ['KeyNotInConfigError',
           'InvalidCityId',
           'InvalidRestaurantId',
           'InvalidCityName',
           'StringNotNumeric',
           'RequestFailedError',
           'RestaurantSearchNoneFindError']


class KeyNotInConfigError(KeyError):
    """Exception raised when config is missing a required field

    Attributes
        key : field missing from config
    """

    def __init__(self, key):
        self.key = key
        self.message = str(self.key) + " is missing from config"
        super().__init__(self.message)

class InvalidCityId(ValueError):
    """Exception raised when cityid is invalid a/c to zomato api
    """

    def __init__(self, city_ID=None):
        self.message = 'Given cityid : ' + (str(city_ID) if city_ID is not None else '') + ' is missing in Zomato-api'
        super().__init__(self.message)

class InvalidRestaurantId(ValueError):
    """Exception raised when restaurantid is invalid a/c to zomato api
    """

    def __init__(self, restaurant_ID=None):
        self.message = 'Given restaurantid : ' + (str(restaurant_ID) if restaurant_ID is not None else '') + ' is missing in Zomato-api'
        super().__init__(self.message)

class InvalidCityName(ValueError):
    """Exception raised when city-name (location) is invalid a/c to zomato api
    """

    def __init__(self, city_name=None):
        self.message = 'Given cityname (location) : ' + (city_name if city_name is not None else '') + ' is missing in Zomato-api'
        super().__init__(self.message)

class StringNotNumeric(ValueError):
    """Exception raised when string passed is not numeric
    """

    def __init__(self, var_name, var):
        self.message = 'Given ' + var_name + ' : ' + var + ' is not numeric'
        super().__init__(self.message)

class RequestFailedError(Exception):
    """Exception raised when request failed
    """

    def __init__(self, url, code):
        self.message = 'Request to ' + url + ' failed with error code ' + str(code)
        super().__init__(self.message)

class RestaurantSearchNoneFindError(Exception):
    """No restaurants found, using zomato api
    """

    def __init__(self):
        self.message = "Restaurant search failed"
        super().__init__(self.message)
