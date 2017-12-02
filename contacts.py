import requests
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

from googleplaces import GooglePlaces, types
import googlemaps

url = 'https://maps.googleapis.com/maps/api/place/details/output?parameters'

YOUR_API_KEY = 'AIzaSyBJuXDLb0vwzRtI8a_xZLEjxojylfJ6GiE'


# print 'fetching....'


def find_contacts(location, type):
    gmaps = googlemaps.Client(key='AIzaSyDph9boEoD8gqNKmQvvai3c8Dpp20grxP0')
    print 'LOCCC', str(location)
    google_places = GooglePlaces(YOUR_API_KEY)

    loc_type = {'hospital': [types.TYPE_HOSPITAL],
                'police': [types.TYPE_POLICE],
                'fire_station': [types.TYPE_FIRE_STATION],
                'all': [types.TYPE_HOSPITAL, types.TYPE_POLICE, types.TYPE_FIRE_STATION]
                }

    query_result = google_places.nearby_search(
        lat_lng=location,
        types=loc_type[type],
        keyword=type,
        rankby="distance")

    results = []

    for place in query_result.places:
        # Returned places from a query are place summaries.
        # print place.name
        # print place.geo_location
        # print place.place_id


        # The following method has to make a further API call.
        place.get_details()
        # Referencing any of the attributes below, prior to making a call to
        # get_details() will raise a googleplaces.GooglePlacesAttributeError.
        # print place.details # A dict matching the JSON response from Google.
        # print place.local_phone_number
        # print place.international_phone_number
        # print place.website
        # print place.url
        image_url = ""
        # # Getting place photos
        for photo in place.photos:
            print photo
            # 'maxheight' or 'maxwidth' is required
            photo.get(maxheight=500, maxwidth=500)
            # # MIME-type, e.g. 'image/jpeg'
            photo.mimetype
            # # Image URL
            image_url = photo.url
            print image_url
            # Original filename (optional)
            photo.filename
            # Raw image data
            photo.data
        url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&mode=driving&language=en-EN&sensor=false" % (
        str(location['lat']) + ',' + str(location['lng']),
        str(place.geo_location['lat']) + ',' + str(place.geo_location['lng']))
        # print url
        req = requests.get(url)
        res = json.loads(req.text)
        driving_time = ''
        distance = ''
        try:
            driving_time = res['rows'][0]['elements'][0]['duration']['text']
            distance = res['rows'][0]['elements'][0]['distance']['text']
        except:
            pass
        nav_url = "https://www.google.co.in/maps/dir/%s/%s" % (str(location['lat']) + ',' + str(location['lng']),
                                                               str(place.geo_location['lat']) + ',' + str(place.geo_location['lng']))
        components = place.details["address_components"]
        city = "India"
        if components:
          try:
            for c in components:
              if "locality" in c["types"]:
                city = c["short_name"]
          except:
            pass
        if city=="India":
          try:
            for c in components:
              if "administrative_area_level_1" in c["types"]:
                city = c["short_name"]
          except:
            pass
        if place.local_phone_number:
          results.append({
              'name': place.name,
              'location': {'lat': str(place.geo_location['lat']), 'lng': str(place.geo_location['lng'])},
              'phone': place.local_phone_number,
              'address': place.formatted_address,
              'distance': distance,
              'time': driving_time,
              'url': nav_url,
              'city': city,
              'image_url': image_url
          })
        if len(results) > 2:
            return json.dumps(results)
    return json.dumps(results)


# l = find_contacts({'lat':21.1619602, 'lng':72.7850744}, 'hospital')
# print type(l)
# pp.pprint(l)


'''
# Adding and deleting a place
try:
    added_place = google_places.add_place(name='Mom and Pop local store',
            lat_lng={'lat': 51.501984, 'lng': -0.141792},
            accuracy=100,
            types=types.TYPE_HOME_GOODS_STORE,
            language=lang.ENGLISH_GREAT_BRITAIN)
    print added_place.place_id # The Google Places identifier - Important!
    print added_place.id
    # Delete the place that you've just added.
    google_places.delete_place(added_place.place_id)
except GooglePlacesError as error_detail:
    # You've passed in parameter values that the Places API doesn't like..
    print error_detail
Reference
googleplaces.GooglePlacesError
googleplaces.GooglePlacesAttributeError
googleplaces.geocode_location(location, sensor=False)
  Converts a human-readable location to a Dict containing the keys: lat, lng.
  Raises googleplaces.GooglePlacesError if the geocoder fails to find the
  specified location.
googleplaces.GooglePlaces
  nearby_search(**kwargs)
    Returns googleplaces.GooglePlacesSearchResult
      kwargs:
        keyword  -- A term to be matched against all available fields, including but
                    not limited to name, type, and address (default None)
        language -- The language code, indicating in which language the results
                    should be returned, if possble. (default en)
        lat_lng  -- A dict containing the following keys: lat, lng (default None)
        location -- A human readable location, e.g 'London, England' (default None)
        name     -- A term to be matched against the names of the Places.
                    Results will be restricted to those containing the passed name value. (default None)
        radius   -- The radius (in meters) around the location/lat_lng to restrict
                    the search to. The maximum is 50000 meters (default 3200)
        rankby   -- Specifies the order in which results are listed:
                    'prominence' (default) or 'distance' (imply no radius argument)
        sensor   -- Indicates whether or not the Place request came from a device
                    using a location sensor (default False)
        types    -- An optional list of types, restricting the results to Places (default [])
  text_search(**kwargs)
    Returns googleplaces.GooglePlacesSearchResult
      kwargs:
        query  --  The text string on which to search, for example:
                   "Restaurant in New York".
        lat_lng  -- A dict containing the following keys: lat, lng (default None)
        location -- A human readable location, e.g 'London, England' (default None)
        language -- The language code, indicating in which language the results
                    should be returned, if possble. (default en)
        radius   -- The radius (in meters) around the location/lat_lng to restrict
                    the search to. The maximum is 50000 meters (default 3200)
        types    -- An optional list of types, restricting the results to Places (default [])
  autocomplete(**kwargs):
    Returns googleplaces.GoogleAutocompleteSearchResult
      kwargs:
        input  --   The text string on which to search, for example:
                    "Hattie B's".
        lat_lng -- A dict containing the following keys: lat, lng (default None)
        location -- A human readable location, e.g 'London, England' (default None)
        radius   -- The radius (in meters) around the location to which the
                    search is to be restricted. The maximum is 50000 meters.
                    (default 3200)
        language -- The language code, indicating in which language the
                    results should be returned, if possible. (default lang.ENGLISH)
        types    -- A type to search against. See `types.py` "autocomplete types"
                    for complete list
                    https://developers.google.com/places/documentation/autocomplete#place_types.
        components -- An optional grouping of places to which you would
                    like to restrict your results. An array containing one or
                    more tuples of:
                    * country: matches a country name or a two letter ISO 3166-1 country code.
                    eg: [('country','US')]
  radar_search(**kwargs)
    Returns googleplaces.GooglePlacesSearchResult
      kwargs:
        keyword  -- A term to be matched against all available fields, including
                    but not limited to name, type, and address (default None)
        name     -- A term to be matched against the names of Places. Results will
                    be restricted to those containing the passed name value.
        opennow  -- Returns only those Places that are open for business at the time
                    the query is sent
        lat_lng  -- A dict containing the following keys: lat, lng (default None)
        location -- A human readable location, e.g 'London, England' (default None)
        language -- The language code, indicating in which language the results
                    should be returned, if possble. (default en)
        radius   -- The radius (in meters) around the location/lat_lng to restrict
                    the search to. The maximum is 50000 meters (default 3200)
        sensor   -- Indicates whether or not the Place request came from a
                    device using a location sensor (default False).
        types    -- An optional list of types, restricting the results to Places (default [])
  get_place(**kwargs)
    Returns a detailed instance of googleplaces.Place
      place_id  -- The unique Google identifier for the required place.
      language   -- The language code, indicating in which language the results
                    should be returned, if possble. (default en)
      sensor     -- Indicates whether or not the Place request came from a
                    device using a location sensor (default False).
  checkin(place_id, sensor=False)
    Checks in an anonymous user in to the Place that matches the place_id.
      kwargs:
        place_id   -- The unique Google identifier for the required place.
        sensor      -- Boolean flag denoting if the location came from a device
                       using its location sensor (default False).
  add_place(**kwargs)
    Returns a dict containing the following keys: place_id, id.
      kwargs:
        name        -- The full text name of the Place. Limited to 255
                       characters.
        lat_lng     -- A dict containing the following keys: lat, lng.
        accuracy    -- The accuracy of the location signal on which this request
                       is based, expressed in meters.
        types       -- The category in which this Place belongs. Only one type
                       can currently be specified for a Place. A string or
                       single element list may be passed in.
        language    -- The language in which the Place's name is being reported.
                       (default googleplaces.lang.ENGLISH).
        sensor      -- Boolean flag denoting if the location came from a device
                       using its location sensor (default False).
  delete_place(place_id, sensor=False)
    Deletes a place from the Google Places database.
      kwargs:
        place_id   -- The unique Google identifier for the required place.
        sensor      -- Boolean flag denoting if the location came from a
                       device using its location sensor (default False).
googleplaces.GoogleAutocompleteSearchResult
  raw_response
    Returns the raw JSON response from the Autocomplete API.
  predictions
    Returns an array of prediction objects.
googleplaces.GooglePlacesSearchResult
  raw_response
    The raw JSON response returned by the Google Places API.
  places
    A list of summary googleplaces.Place instances.
  has_attributions()
    Returns a flag indicating if the search result has html attributions that
    must be displayed.
  html_attributions()
    Returns a List of String html attributions that must be displayed along with
    the search results.
googleplaces.Prediction
  description
    String representation of a Prediction location. Generally contains
    name, country, and elements contained in the terms property.
  id
    Returns a unique stable identifier denoting this Place. This identifier
    may not be used to retrieve information about this Place, but can be used
    to consolidate data about this Place, and to verify the identity of a
    Place across separate searches
  matched_substrings
    Returns the placement and offset of the matched strings for this search.
    A an array of dicts, each with the keys 'length' and 'offset', will be returned.
  place_id
    Returns the unique stable identifier denoting this place.
    This identifier may be used to retrieve information about this
    place.
    This should be considered the primary identifier of a place.
  reference
    Returns a unique identifier for the Place that can be used to fetch full
    details about it. It is recommended that stored references for Places be
    regularly updated. A Place may have many valid reference tokens.
  terms
    A list of terms which build up the description string
    A an array of dicts, each with the keys `offset` and `value`, will be returned.
  types
    Returns a List of feature types describing the given result.
  place
    Returns a Dict representing the full response from the details API request.
    This property will raise a googleplaces.GooglePlacesAttributeError if it is
    referenced prior to get_details()
  get_details(**kwargs)
    Retrieves full information on the place matching the reference.
      kwargs:
        language   -- The language code, indicating in which language the
                      results should be returned, if possible. This value defaults
                      to the language that was used to generate the
                      GooglePlacesSearchResult instance.
googleplaces.Place
  reference
    (DEPRECATED) Returns a unique identifier for the Place that can be used to
    fetch full details about it. It is recommended that stored references for
    Places be regularly updated. A Place may have many valid reference tokens.
  id
    (DEPECATED) Returns a unique stable identifier denoting this Place. This
    identifier may not be used to retrieve information about this Place, but
    can be used to consolidate data about this Place, and to verify the identity
    of a Place across separate searches.
  place_id
    A textual identifier that uniquely identifies a place. To retrieve information
    about the place, pass this identifier in the placeId field of a Places API
    request.
  icon
    contains the URL of a suggested icon which may be displayed to the user when
    indicating this result on a map.
  types
    Returns a List of feature types describing the given result.
  geo_location
    Returns the geocoded latitude,longitude value for this Place.
  name
    Returns the human-readable name for the Place.
  vicinity
    Returns a feature name of a nearby location. Often this feature refers to a
    street or neighborhood.
  rating
    Returns the Place's rating, from 0.0 to 5.0, based on user reviews.
  details
    Returns a Dict representing the full response from the details API request.
    This property will raise a googleplaces.GooglePlacesAttributeError if it is
    referenced prior to get_details()
  photos
    returns a list of available googleplaces.Photo objects.
  formatted_address
    Returns a string containing the human-readable address of this place. Often
    this address is equivalent to the "postal address".
    This property will raise a googleplaces.GooglePlacesAttributeError if it is
    referenced prior to get_details()
  local_phone_number
    Returns the Place's phone number in its local format.
    This property will raise a googleplaces.GooglePlacesAttributeError if it is
    referenced prior to get_details()
  international_phone_number
    Returns the Place's phone number in international format. International
    format includes the country code, and is prefixed with the plus (+) sign.
    This property will raise a googleplaces.GooglePlacesAttributeError if it is
    referenced prior to get_details()
  website
    Returns the authoritative website for this Place, such as a business'
    homepage.
  url
    Returns the official Google Place Page URL of this Place.
  has_attributions
    Returns a flag indicating if the search result has html attributions that
    must be displayed. along side the detailed query result.
  html_attributions
    Returns a List of String html attributions that must be displayed along with
    the detailed query result.
  checkin()
    Checks in an anonynomous user in.
  get_details(**kwargs)
    Retrieves full information on the place matching the place_id.
      kwargs:
        language   -- The language code, indicating in which language the
                      results should be returned, if possible. This value defaults
                      to the language that was used to generate the
                      GooglePlacesSearchResult instance.
googleplaces.Photo
  orig_height
    the maximum height of the origin image.
  orig_width
    the maximum height of the origin image.
  html_attributions
     Contains any required attributions. This field will always be present,
     but may be empty.
  photo_reference
     A string used to identify the photo when you perform a Photo request
     via the get method.
  get
    Fetches the actual photo data from the Google places API.
  mimetype
    Specifies the mimetype if the fetched image. This property is only
    available after the get API has been invoked.
  filename
    Specifies the filename of the fetched image. This property is only
    available after the get API has been invoked.
  data
    The binary data of the image. This property is only available after the
    get API has been invoked.
  url
    The url of the image. This property is only available after the get API
    has been invoked.
'''