from clarifai.client import ClarifaiApi
import pprint

pp = pprint.PrettyPrinter(indent=4)


# returns fire_accident, road_accident, police or fine
def find_type(image_name):
    clarifai_api = ClarifaiApi('ph4Sk2DtEk0Et_9aRUxdzxLPzMpMjv75WlFPnT5H',
                               'kg_cH9uYZHYikRSrjv7izSRA1fgxCORKryLe8Mn6')  # assumes environment variables are set.

    road_classes = ['vehicle', 'road', 'car', 'transportation system', 'truck', 'street', 'ambulance', 'storm']
    common_classes = ['calamity', 'battle', 'accident', 'offense', 'police']
    fire_classes = ['flame', 'smoke', 'burnt', 'light', 'energy', 'fire_truck', 'heat', 'explosion']

    clf = clarifai_api.tag_images(open(image_name, 'rb'))
    img_classes = clf['results'][0]['result']['tag']['classes']
    if len(img_classes) == 0:
        return 'Failed'
    common_score = 0
    road_score = 0
    fire_score = 0
    for cl in img_classes:
        if cl in common_classes:
            common_score += 1
        if cl in road_classes:
            road_score += 1
        if cl in fire_classes:
            fire_score += 1
    res = {'fire': fire_score, 'road': road_score, 'fine': common_score}
    print res
    if (res['road'] >= 3 and res['road'] > res['fire']):
        return 'road'
    if (res['fire'] > 1):
        print res['fire']
        return 'fire'
    if (res['fine'] <= 1):
        return 'fine'
    else:
        return 'police'

#print find_type('1.jpg')