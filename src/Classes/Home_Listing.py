import datetime as dt
from typing import Optional


class HomeListing(object):

    def __init__(self, address: str, town: str, zip: str, state: str, listing_url: str, beds: int, baths: float,
                 sqft: int, listing_time: Optional[dt.datetime], parking: Optional[str], appliances: list[str],
                 interior_features: list[str], exterior_features: list[str]):
        self.address = address
        self.town = town
        self.zip = zip
        self.state = state
        self.listing_time = listing_time
        self.listing_url = listing_url
        self.sqft = sqft
        self.baths = baths
        self.beds = beds
        self.appliances = appliances
        self.interior_features = interior_features
        self.exterior_features = exterior_features
        self.parking = parking


