import json
from tqdm import tqdm
import numpy as np
import pandas as pd


# for nlp part ===
import spacy
nlp = spacy.load('en_core_web_sm')
# ========

# for labeling and extracting locations from images ===
from google.cloud import vision
from google.cloud.vision_v1 import types
import os
KEY_PATH = '../apikey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = KEY_PATH
# ======================================================

# for normalizing location names using Google Maps API ==
import requests
google_maps_api_key = ''
api_key = google_maps_api_key
# ============================================================



def build_csv(data, testing=False):
    '''
    Builds csv dataframe from given users json data
    '''
    result = []
    for user in (data):
        user_is_open = data[user].get('graphql')
        if user_is_open:
            user_posts = (data[user].get('graphql')['user']['edge_owner_to_timeline_media']['edges'])
            for post in user_posts:
                post = post['node']
                img_source = post['display_url']
                is_video = post['is_video']
                if is_video: img_source = np.nan

                has_subscription = (len(post['edge_media_to_caption']['edges']) > 0)
                if has_subscription:
                    subscription = post['edge_media_to_caption']['edges'][0]['node']['text']
                else:
                    subscription = np.nan

                timestamp = post['taken_at_timestamp']
                location = post['location']
                if location:
                    location = location['name']
                else:
                    location = np.nan
                result.append((user, location, img_source, subscription, timestamp))

        else:
            pass
    df = pd.DataFrame(result, columns=['user', 'location', 'source', 'subscription', 'timestamp'])
    if testing:
        return df
    else:
        df.to_csv('data/df_full.csv', index=False)


def extractLocationFrom(string):
    '''
    Extracts location entities from given string.
    Is used to extract locations from user post subsciptions.
    '''
    gpe = [];
    loc = [];
    is_adv = False

    if not string:
        return np.nan, is_adv

    if '.com' in string:
        is_adv = True
        return np.nan, is_adv

    doc = nlp(string)

    for entity in doc.ents:
        if len(entity.text) > 2 and entity.text:
            if entity.label_ == 'GPE':
                gpe.append(entity.text)
            elif entity.label_ == 'LOC':
                loc.append(entity.text)
    n_locations = len(set(loc).union(set(gpe)))

    if n_locations == 1 or n_locations == 2:
        if loc:
            return loc[0], is_adv
        else:
            return gpe[0], is_adv

    else:
        if n_locations >= 5:
            is_adv = True
        return np.nan, is_adv


def detect_landmark(image):
    '''
    GCV function. Detects landmark from given image url.
    '''

    landmark_response = client.landmark_detection(image)
    landmarks = landmark_response.landmark_annotations

    if len(landmarks) == 0:
        return None
    else:
        landmark = landmarks[0]

        landmark_name = landmark.description

        lat_lng = landmark.locations[0].lat_lng
        lat = lat_lng.latitude
        lng = lat_lng.longitude

        #         return lat, lng

        city, country, code, landmark_alias = get_location_from(lat, lng)

        names = {landmark_name, landmark_alias}

        return {'names': names, 'city': city, 'country': country, 'country_code': code}


def get_location_from(latitude, longitude):
    '''
    Gets country, city, landmark_name from latitute, longitude
    '''
    lat_long = ', '.join((str(latitude), str(longitude)))
    location = geolocator.reverse(lat_long, language='en')
    #     return location
    address = location.raw['address']

    city = address.get('state') or address.get('city')
    country = address.get('country')
    code = address['country_code']
    landmark_name = address.get('tourism') or address.get('road')

    return city, country, code, landmark_name


def extract_city_country(addresses):
    '''
    Extracts city and country from google maps location info
    '''
    res = {}
    for address in addresses:
        if address['types']:
            res[address['types'][0]] = address['long_name']
        else:
            pass

    if 'country' in res:
        if 'administrative_area_level_1' in res:
            city = res['administrative_area_level_1']
        elif 'administrative_area_level_2' in res:
            city = res['administrative_area_level_2']
        elif 'administrative_area_level_3' in res:
            city = res['administrative_area_level_3']
        elif 'locality' in res:
            city = res['locality']
        else:
            return np.nan
        return {'city': city,
                'country': res['country']}
    else:
        return np.nan


def get_labels(image):
    '''
    Gets image labels using GCV from image source
    '''
    label_response = client.label_detection(image)
    labels = set()
    for label in label_response.label_annotations:
        labels.add(label.description)
    return labels


if __name__=='__main__':

    df_full = pd.read_csv('data/df_full.csv')
    # EXTRACTING LOCATIONS FROM SUBSCRIPTIONS USING nlp========================================================
    adv_accounts = set()
    print('EXTRACTING LOCATIONS FROM SUBSCRIPTIONS')
    for index, row in tqdm(df_full.iterrows()):

        if row['user'] in adv_accounts:
            continue
        loc = row['location']; subscript = row['subscription']
        if (loc is np.nan) and (subscript is not np.nan):
            extracted_loc, is_adv = extractLocationFrom(subscript)

            if is_adv:
                adv_accounts.add(row['user'])
            else:
                df_full.at[index, 'location'] = extracted_loc

    # DROPPING ADVERTISING ACCOUNTS
    df = df_full[~df_full['user'].isin(adv_accounts)].reset_index(drop=True)
    del df_full
    # =========================================================================================================



    # EXTRACTING LOCATIONS FROM IMAGES USING Google Cloud Vision  ===============================================
    print('EXTRACTING LOCATIONS FROM IMAGES')
    client = vision.ImageAnnotatorClient()
    image = types.Image()
    detect_landmark_images = set()
    for index, row in tqdm(df.iterrows()):
        loc = row['location']; img_source = row['source']
        if (loc is np.nan) and (img_source is not np.nan):
            detect_landmark_images.add(img_source)
    image_location = {}
    for source in detect_landmark_images:
        image.source.image_uri = source
        image_location[source] = detect_landmark(image)

    for index, row in tqdm(df.iterrows()):
        if (row['source'] in image_location) and (row['location'] is np.nan):
            df.at[index, 'location'] = image_location[row['source']]
    # ============================================================================================================



    # NORMALIZING LOCATIONS USING Google Maps API ================================================================
    print('NORMALIZING LOCATIONS USING Google Maps API')
    locations = set(df['location'].unique()) - {np.nan}
    loc_info = {}
    for loc in tqdm(locations):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={loc}&key={api_key}"
        loc_info[loc] = requests.get(url).json()

    locations_c = {}
    for loc in loc_info:
        if loc_info[loc]['status'] == 'OK':
            results = loc_info[loc]['results']
            if results:
                results = results[0]
                city_country = extract_city_country(results['address_components'])
                if city_country is not np.nan:
                    locations_c[loc] = results['geometry']['location']
                    locations_c[loc].update(city_country)
    def map_locations(x):
        if x in locations_c:
            return locations_c[x]['city'] + ', ' + locations_c[x]['country']
        else:
            return np.nan
    df['location'] = df['location'].apply(map_locations)
    # ============================================================================================================



    # CUTTING USERS WITH LESS THEN THREE CHECK-INS ================================================================
    print('CUTTING USERS WITH LESS THEN THREE CHECK-INS')
    enough_locs = set()
    loc_mask = df.groupby('user')['location'].apply(lambda x: len(set(x)) - int(np.nan in x)) >= 3
    for user in df['user'].unique():
        if loc_mask[user]:
            enough_locs.add(user)

    df = df[df['user'].isin(enough_locs)].reset_index(drop=True)
    # df.to_csv('df_cutted.csv', index=False)
    # =============================================================================================================



    # LABELING IMAGES USING GOOGLE CLOUD VISION API ===============================================================
    print('LABELING IMAGES USING GOOGLE CLOUD VISION API')
    client = vision.ImageAnnotatorClient()
    image = types.Image()
    sources = set(df['source']) - {np.nan}
    labels = {}
    i=0
    for source in tqdm(sources):
        i+=1
        image.source.image_uri = source
        labels[source] = list(get_labels(image))
        if i == 2:
            break
    with open('data/img_labels.json', 'w') as json_file:
        json.dump(labels, json_file)
    # =============================================================================================================




