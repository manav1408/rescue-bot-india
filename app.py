import os
import json
import pickle

import requests
import contacts as c
import tweepy
import sys, md5, magic
import image_classify as ic
import disaster
import userdb
import googlemaps
from twilio.rest import TwilioRestClient
from flask import Flask, request

app = Flask(__name__)


def update_location(loc):
    fname = "location.p"
    fileObj = open(fname,'wb')
    pickle.dump(loc,fileObj)
    fileObj.close()

def get_location():
    try:
        fname = "location.p"
        fileObj = open(fname, 'r')
        return pickle.load(fileObj)
    except:
        return None

def update_image_url(image_url):
    fname = "image_url.p"
    fileObj = open(fname,'wb')
    pickle.dump(image_url,fileObj)
    fileObj.close()

def get_image_url():
    try:
        fname = "image_url.p"
        fileObj = open(fname, 'r')
        return pickle.load(fileObj)
    except:
        return None

def set_setup_variable():
    fname = "setup_var.p"
    fileObj = open(fname,'wb')
    pickle.dump(True,fileObj)
    fileObj.close()

def reset_setup_variable():
    fname = "setup_var.p"
    fileObj = open(fname,'wb')
    pickle.dump(False,fileObj)
    fileObj.close()

def get_setup_variable():
    try:
        fname = "setup_var.p"
        fileObj = open(fname, 'r')
        return pickle.load(fileObj)
    except:
        return False

def location_to_url(location):
    lat = str(location['lat'])
    lng = str(location['lng'])
    url = "https://www.google.co.in/maps/place/"+lat+','+ lng
    return url

def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)

def enhance_tweet_text(tweet_text, acc_type):
    try:
        accident_location = get_location()
        gmaps = googlemaps.Client(key='AIzaSyDph9boEoD8gqNKmQvvai3c8Dpp20grxP0')
        reverse_geocode_result = gmaps.reverse_geocode((str(accident_location.get("lat")), str(accident_location.get("lng"))))
        accident_address = str(reverse_geocode_result[0]["formatted_address"])
        #accident_address = accident_address[:75]
        n = findnth(accident_address, ",", 2)
        accident_address = accident_address[:n] + "."
        components = reverse_geocode_result[0]["address_components"]
        accident_city = "India"
        if components:
            for c in components:
                if "locality" in c["types"]:
                    accident_city = c["short_name"]
            if accident_city == "India":
                for c in components:
                    if "administrative_area_level_1" in c["types"]:
                        accident_city = c["short_name"]
        accident_city = "".join(accident_city.split(" "))
        tweet = acc_type + " accident at " + accident_address
        if acc_type == "Fire" :
            tweet = tweet + " #FireDepartment" + accident_city
            log("Case fire")
            log(tweet)
        elif acc_type == "Road" :
            tweet = tweet + " #"+accident_city+"Police"
            log("Case road")
            log(tweet)
        return tweet
    except:
        return tweet

def setup_tweepy(tweet_text,filename, sender_id, acc_type="Road"):
    cfg = {
        "consumer_key": "octn8nPbaps5KM8VCw5NX7M5A",
        "consumer_secret": "ZLtAQpqLD8CvWInT8NamwDPGW4rfid1c2EWufa418bXmWqqkn5",
        "access_token": "764585010804383744-Zro2gSL2xqs5THJgyxECA1JHvOVMhmQ",
        "access_token_secret": "Il2b221rmBHCjoz6RLlTOpOGKxUhLGHx6IOPSMAVscRXf"
    }

    a = acc_type

    api = get_api(cfg)
    tweet = enhance_tweet_text(tweet_text, a)

    try:
        #api.update_with_media(filename, status=tweet)
        log(str(tweet))
        api.update_with_media(filename, status=tweet)

    except IndexError:
        api.update_with_media(filename)

    #status = api.update_status(status=tweet)
    log("Tweet has been posted!")
    # Yes, tweet is called 'status' rather confusing
    send_message(sender_id, "Thanks! We have shared your image via Twitter with the appropriate authority. Twitter handle - @bot_rescue")
    send_message(sender_id, "In the meanwhile, don't panic and follow these instructions.")




@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello Mayank Saxena!", 200


@app.route('/', methods=['POST'])
def webook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    if messaging_event.get("message").get("text"):
                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                        try:
                            message_text = messaging_event["message"]["text"]  # the message's text
                            # send_message(sender_id, message_text)
                            message_text = message_text.lower()
                            if message_text == "hi" or message_text == "hello" or message_text == "hey" or message_text == "start" or message_text == "begin" or message_text == "yo" :

                                f = open('credentials')
                                lines = f.readlines()
                                token = lines[5]

                                user_details_url = "https://graph.facebook.com/v2.6/%s" % sender_id
                                user_details_params = {'fields': 'first_name,last_name,profile_pic',
                                                       'access_token': token}

                                user_details = requests.get(user_details_url, user_details_params).json()
                                send_message(sender_id, "Hello " + user_details['first_name'] + " " + user_details['last_name'] + ". Welcome to Rescue Bot!")

                            elif message_text == "setup":
                                create_button_message(sender_id)
                                set_setup_variable()

                            elif (message_text == "police station"):
                                police_station_results = c.find_contacts(get_location(), "police")
                                log(str(police_station_results))
                                data = json.loads(police_station_results)
                                for i in range(0, len(data)):
                                    j = data[i]
                                    subtitle =  "Distance : " + j["distance"] + "\t Time : " + j["time"] + " /n" + j["address"]
                                    create_generic_template(sender_id, j["name"], subtitle, j["image_url"], j["phone"], j["url"] )
                            elif (message_text == "hospital"):
                                hospital_results = c.find_contacts(get_location(), "hospital")
                                log(str(hospital_results))
                                data = json.loads(hospital_results)
                                for i in range(0, len(data)):
                                    j = data[i]
                                    subtitle =  "Distance : " + j["distance"] + "\t Time : " + j["time"] + " /n" + j["address"]
                                    create_generic_template(sender_id, j["name"], subtitle, j["image_url"], j["phone"], j["url"] )
                            elif (message_text == "fire station"):
                                fire_station_results = c.find_contacts(get_location(), "fire_station")
                                log(str(fire_station_results))
                                data = json.loads(fire_station_results)
                                for i in range(0, len(data)):
                                    j = data[i]
                                    subtitle =  "Distance : " + j["distance"] + "\t Time : " + j["time"] + " /n" + j["address"]
                                    create_generic_template(sender_id, j["name"], subtitle, j["image_url"], j["phone"], j["url"] )

                            elif ("snake" in message_text or "bite" in message_text):
                                image_url = "http://www.pediatricsconsultantlive.com/sites/default/files/peds/1457669.png"
                                create_image_message(sender_id, image_url)
                                log("Snake bite case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("shock" in message_text):
                                image_url = "http://image.slidesharecdn.com/electricshock12-150326135323-conversion-gate01/95/electric-shock-10-638.jpg?cb=1443946633"
                                create_image_message(sender_id, image_url)
                                log("Electrick shock case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("stroke" in message_text):
                                image_url = "http://67.media.tumblr.com/100c0dc4191629f7dbc899607e3bb7ea/tumblr_nm9l7aKRjN1urwcapo1_500.jpg"
                                create_image_message(sender_id, image_url)
                                log("Heat Stroke case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("nose" in message_text or "nose bleed" in message_text):
                                image_url = "http://image.slidesharecdn.com/finalfirstaidslidespresentation-100822055615-phpapp02/95/final-first-aid-slides-presentation-4-728.jpg?cb=1282731053"
                                image_url_2 = "http://image.slidesharecdn.com/thefirstaid-120114071752-phpapp02/95/the-first-aid-by-dr-aftab-alam-4-728.jpg?cb=1326526236"
                                create_image_message(sender_id, image_url)
                                create_image_message(sender_id, image_url_2)
                                log("Nose bleed case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("heart attack" in message_text or "cardiac arrest" in message_text):
                                image_url = "http://image.slidesharecdn.com/finalfirstaidslidespresentation-100822055615-phpapp02/95/final-first-aid-slides-presentation-6-728.jpg?cb=1282731053"
                                create_image_message(sender_id, image_url)
                                log("Heart attack case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("burn" in message_text or "chemical" in message_text or "burn" in message_text):
                                image_url_1 = "http://image.slidesharecdn.com/finalfirstaidslidespresentation-100822055615-phpapp02/95/final-first-aid-slides-presentation-10-728.jpg?cb=1282731053"
                                image_url_2 = "http://image.slidesharecdn.com/finalfirstaidslidespresentation-100822055615-phpapp02/95/final-first-aid-slides-presentation-11-728.jpg?cb=1282731053"
                                create_image_message(sender_id, image_url_1)
                                create_image_message(sender_id, image_url_2)
                                log("Burns case")
                                send_message(sender_id, "Pleased follow the instructions provided in the image.")

                            elif ("choking" in message_text or "choke" in message_text):
                                image_url_1 = "http://image.slidesharecdn.com/finalfirstaidslidespresentation-100822055615-phpapp02/95/final-first-aid-slides-presentation-13-728.jpg?cb=1282731053"
                                image_url_2 = "http://image.slidesharecdn.com/finalfirstaidslidespresentation-100822055615-phpapp02/95/final-first-aid-slides-presentation-14-728.jpg?cb=1282731053"
                                create_image_message(sender_id, image_url_1)
                                create_image_message(sender_id, image_url_2)
                                log("Choking case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("cut" in message_text or "abrasion" in message_text):
                                image_url = "http://www.mc-sea.de/media/catalog/product/cache/4/image/5e06319eda06f020e43594a9c230972d/p/o/po555.210.11.png"
                                create_image_message(sender_id, image_url)
                                log("Cuts and abrasions case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("insect" in message_text):
                                image_url = "http://image.slidesharecdn.com/thefirstaid-120114071752-phpapp02/95/the-first-aid-by-dr-aftab-alam-4-728.jpg?cb=1326526236"
                                create_image_message(sender_id, image_url)
                                log("Insect bite case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("bee" in message_text or "sting" in message_text or "wasp" in message_text):
                                image_url = "http://image.slidesharecdn.com/firstaid-120205082226-phpapp02/95/firstaid-15-728.jpg?cb=1328430472"
                                create_image_message(sender_id, image_url)
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif ("dog" in message_text):
                                image_url = "http://images.slideplayer.com/24/7222662/slides/slide_20.jpg"
                                create_image_message(sender_id, image_url)
                                log("Dog bite case")
                                send_message(sender_id, "Please follow the instructions provided in the image.")

                            elif get_setup_variable():
                                numbers = userdb.get_user_numbers(sender_id)
                                if(numbers):
                                    send_message(sender_id,"Your Details \n Phone number : "+numbers.get('user_number')+"\n Emergency Numbers"+numbers.get('emergency_numbers'))
                                log("trying to save number in userdb")
                                userdb.save_numbers(sender_id, message_text)
                                print "testing saved results",userdb.get_user_numbers(sender_id)
                                send_message(sender_id,"Setup successful!")
                                reset_setup_variable()

                            elif "help" in message_text:
                                image_url = "https://scontent.fdel1-2.fna.fbcdn.net/v/t34.0-0/p206x206/14193620_1238315046208309_1596749298_n.png?oh=587f6a5837592a9fa900839ab87e07bd&oe=57CCF812"
                                create_image_message(sender_id, image_url)
                                log("Inside help case")

                            else:
                                send_message(sender_id,
                                         "Sorry I couldn't understand you.. Please type help for instructions.")
                        except Exception as e:
                            log("error, no text")
                            log(str(e))

                    if messaging_event.get("message").get("attachments"):  # someone sent us an attachment
                        log("Message has an attachment")
                        sender_id = messaging_event["sender"]["id"]

                        try :
                            if messaging_event["message"]["attachments"][0]["type"] == "image":
                                log("Image received from user.")
                                image_url = messaging_event["message"]["attachments"][0]["payload"]["url"]
                                log(image_url)
                                update_image_url(image_url)
                                if get_location() is None:
                                    send_message(sender_id, "Now please send your location!")
                                else :
                                    classify_image(sender_id)

                            if messaging_event["message"]["attachments"][0]["type"] == "location":
                                 #recipient_id = messaging_event["recipient"]["id"]
                                 lat = float(messaging_event["message"]["attachments"][0]["payload"]["coordinates"]["lat"])
                                 lng = float(messaging_event["message"]["attachments"][0]["payload"]["coordinates"]["long"])
                                 d = {"lat": lat, "lng": lng}
                                 log(str(d))
                                 update_location(d)
                                 image_url = get_image_url()
                                 disasters = disaster.top_disasters()
                                 for d in disasters:
                                     if d["is_recent"]:
                                         send_message(sender_id, "ALERT ALERT ALERT !!!")
                                         send_message(sender_id, d["title"])
                                         send_message(sender_id,
                                                      "Please follow the instructions provided in the image.")
                                         if d["type"] == "earthquake":
                                             image_url = "http://www.hlimg.com/images/stories/738X538/what%20to%20do%20during%20earthquake_1430115831e12.png"
                                             create_image_message(sender_id, image_url)
                                         elif d["type"] == "cyclone":
                                             image_url = "http://www.sulata.net/wp-content/uploads/2014/10/cyclone-safety-tips.png"
                                             create_image_message(sender_id, image_url)
                                         elif d["type"] == "flood":
                                             image_url = "http://paolopunzalan.com/wp-content/uploads/2012/08/632303496.jpeg"
                                             create_image_message(sender_id, image_url)
                                 if image_url is None:
                                    create_quick_replies(sender_id)
                                 else:
                                    classify_image(sender_id)

                            else:
                                #send_message(sender_id, "Attachment is not of type location")
                                log("Attachment is not of type location")
                                pass

                        except Exception as e:
                            log(str(e))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass


                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    try:
                        message_text = messaging_event["postback"]["payload"]  # the message's text
                        log("Inside postback")

                        message_text = message_text.lower()

                        sender_id = messaging_event["sender"]["id"]

                        if (message_text == "report an accident"):
                            send_message(sender_id, "Please send the image of the accident.")
                            log("Case 1")

                        elif (message_text == "alert family and friends"):
                            #send_message(sender_id,"Your families and friends have been sent an SMS.")
                            send_message(sender_id, "This feature is currently unavailable. It will be added soon. ")
                            log("Case 2")
                            user_address = ""
                            map_url = ""
                            account_sid = "AC493bc0237b4d0911fdd3fb4da9d8d305"
                            auth_token = "23072addcfa505a50115a86cbaa7c7be"
                            client = TwilioRestClient(account_sid, auth_token)

                            try:
                                user_location = get_location()

                                gmaps = googlemaps.Client(key='AIzaSyDph9boEoD8gqNKmQvvai3c8Dpp20grxP0')

                                reverse_geocode_result = gmaps.reverse_geocode(
                                    (str(user_location.get("lat")), str(user_location.get("lng"))))

                                user_address = str(reverse_geocode_result[0]["formatted_address"])

                                map_url = location_to_url(get_location())
                                log(str(map_url))
                                log(str(get_location()))

                            except Exception as e:
                                log(str(e))

                            sms_body = "I am in a problem!"
                            if user_address:
                                sms_body = sms_body + " My location is " + user_address+ ". " + map_url

                            mayank_number = "+919910002161"
                            twilio_phone_number = "+12679327133"
                            satwik_number = "+918447370864"
                            numbers = userdb.get_user_numbers(sender_id)
                            emergency_numbers = []
                            user_number = ''
                            if numbers:
                                user_number = numbers.get('user_number')
                                emergency_numbers = numbers.get('emergency_numbers')
                            else:
                                log("User's numbers doesn't exist in the database.")

                            # for num in emergency_numbers:
                            #     message = client.messages.create(
                            #         to='+91'+num,
                            #         from_=twilio_phone_number,
                            #         body=sms_body
                            #     )
                            # message = client.messages.create(
                            #          to=satwik_number,
                            #          from_=twilio_phone_number,
                            #          body=sms_body
                            #      )
                            # message = client.messages.create(
                            #          to=mayank_number,
                            #          from_=twilio_phone_number,
                            #          body=sms_body
                            #      )


                        elif (message_text == "find nearest emergency numbers"):
                            #send_message(sender_id,"Select hospital/police station/fire station")
                            send_message(sender_id, "Send your location to find nearest hospital/police station/fire station.")
                            #create_quick_replies(sender_id)
                            log("Case 3")
                        elif (message_text == "connect to a doctor"):
                            send_message(sender_id,"Please mention medical emergency")
                            log("Case 4")
                        elif (message_text == "call"):
                            # Keywords
                            #mudit_number = "+919810906050"
                            #test_number = "+918468980861"
                            #user_number = ''
                            #user_number = userdb.get_user_numbers(sender_id).get('user_number')
                            #if user_number:
                            #    user_number = "+91"+user_number
                            #else:
                                #send_message(sender_id,"We don't have your contact details. Please type setup to add")
                            #    log("Inside else")
                            mayank_number = "+919910002161"
                            satwik_number = "+918447370864"
                            #account_sid = "AC493bc0237b4d0911fdd3fb4da9d8d305"
                            #auth_token = "23072addcfa505a50115a86cbaa7c7be"
                            #client = TwilioRestClient(account_sid, auth_token)

                            #call = client.calls.create(to=mayank_number,
                                                #       from_=satwik_number,
                                                 #      url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient")

                            #log(str(call.sid))
                            send_message(sender_id, "Calling feature is currently unavailable. It will be added soon. ")
                            log("Case 5")
                            log("Twilio call executed")
                            #send_message(sender_id, "Call has been scheduled. Please wait.")

                        elif (message_text == "recent disasters in your area"):
                            log("Reporting a disaster")
                            disasters = disaster.top_disasters()
                            log("Before loop")
                            for d in disasters:
                                log("Inside loop")
                                send_message(sender_id, d["title"])
                                send_message(sender_id, "Please follow the instructions provided in the image.")
                                if d["type"] == "earthquake" :
                                    image_url = "http://www.hlimg.com/images/stories/738X538/what%20to%20do%20during%20earthquake_1430115831e12.png"
                                    create_image_message(sender_id, image_url)
                                elif d["type"] == "cyclone" :
                                    image_url = "http://www.sulata.net/wp-content/uploads/2014/10/cyclone-safety-tips.png"
                                    create_image_message(sender_id, image_url)
                                elif d["type"] == "flood" :
                                    image_url = "http://paolopunzalan.com/wp-content/uploads/2012/08/632303496.jpeg"
                                    create_image_message(sender_id, image_url)

                        elif message_text == "setup":
                            log("Setting up account")
                            send_message(sender_id, "Please send us your mobile number followed by your emergency contact number.")

                        elif message_text == "skip" :
                            log("Skipping account setup")
                            send_message(sender_id, "No problem, you can set up your account later. To setup your account send \"Setup\" ")

                        elif message_text == "view account info" :
                            log("Inside view account info part")

                        elif message_text == "get started" :
                            log("Inside get started case")
                            f = open('credentials')
                            lines = f.readlines()
                            token = lines[5]

                            user_details_url = "https://graph.facebook.com/v2.6/%s" % sender_id
                            user_details_params = {'fields': 'first_name,last_name,profile_pic',
                                                   'access_token': token}

                            user_details = requests.get(user_details_url, user_details_params).json()

                            send_message(sender_id, "Hello " + user_details['first_name'] + " " + user_details['last_name'] + ". Welcome to Rescue Bot!")

                            send_message(sender_id, "Please choose one of the options from the menu on the bottom left to start using Rescue Bot.")

                        else:
                            log("Invalid case")
                            pass
                    except Exception as e:
                        log("Inside exception")
                        log(str(e))

    return "ok", 200


def classify_image(sender_id):
    image_url = get_image_url()
    session = requests.session()
    response = session.get(image_url)
    filename = 'poster_%s.jpeg' % md5.new(image_url).hexdigest()
    with open(filename, 'wb') as handle:
        for block in response.iter_content(1048576):
            if not block:
                break
            handle.write(block)
        handle.close()

    mimetype = magic.from_file(filename, mime=True)
    if not mimetype.startswith('image/'):
        raise Exception('Not an image: ' + mimetype)
    if os.stat(filename).st_size > 3072 * 1024:  # 3MB? unsure
        raise Exception('Bigger than 3MB')
    else:
        # filename = sys.argv[1]
        log("Shouldn't be here.")
    result = ic.find_type(filename)
    log("Clarifai API called")
    if result == 'fine':
        send_message(sender_id,
                     "Sorry, We couldn't identify any accident in the image. But don't worry, we've forwarded the image to police. For quick aids, please send more clear pic.")
    else:
        result = result.capitalize()
        setup_tweepy("Hello World", filename, sender_id, result)
        if result == "Fire":
            fire_accident_url = "https://s-media-cache-ak0.pinimg.com/736x/57/96/ab/5796ab1eff8f7f335aad74c59c067209.jpg"
            create_image_message(sender_id, fire_accident_url)
            fire_station_results = c.find_contacts(get_location(), "fire_station")
            data = json.loads(fire_station_results)
            j = data[0]
            subtitle =  "ETA fire van: " + j["time"] 
            send_message(sender_id,subtitle)

        elif result == "Road":
            road_accident_url = "http://www.pointblank7.in/wp-content/uploads/2015/06/Help-Road-Accident-Victims-Good-Samaritans-Infographic.png"
            create_image_message(sender_id, road_accident_url)
            hospital_results = c.find_contacts(get_location(), "hospital")
            data = json.loads(hospital_results)
            j = data[0]
            subtitle =  "ETA Ambulance: " + j["time"] 
            police_station_results = c.find_contacts(get_location(), "police")
            data = json.loads(police_station_results)
            j = data[0]
            subtitle +=  "\n ETA Police: " + j["time"] 
            send_message(sender_id,subtitle)
        else:
            pass


def send_sms(sid, token, sms_from, sms_to, sms_body):
    return requests.post('https://twilix.exotel.in/v1/Accounts/{sid}/Sms/send.json'.format(sid=sid),
                         auth=(sid, token),
                         data={
                                'From': sms_from,
                             'To': sms_to,
                             'Body': sms_body
                         })


def create_button_message(sender_id):
    button_message = json.dumps({
    "recipient":{
                    "id": sender_id
                },
    "message":{
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": "Would you like to setup your account?",
                "buttons": [
                    {
                        "type": "postback",
                        "title": "Yes",
                        "payload": "Setup"
                    },
                    {
                        "type": "postback",
                        "title": "View account info",
                        "payload": "view account info"
                    },
                    {
                        "type": "postback",
                        "title": "Skip",
                        "payload": "Skip"
                    }
                    ]
                }
            }
        }
    })

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers,
                      data=button_message)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def create_image_message(sender_id, image_url):

    image_message = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url
                }
            }
        }
    })

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers,
                      data=image_message)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def create_quick_replies(sender_id):
    quick_reply = json.dumps({
        "recipient":{
                        "id": sender_id
                    },
                    "message":{
        "text": "Choose one of the following:",
        "quick_replies": [
            {
                "content_type": "text",
                "title": "Police Station",
                "payload": "Police Station"
            },
            {
                "content_type": "text",
                "title": "Hospital",
                "payload": "Hospital"
            },
            {
                "content_type": "text",
                "title": "Fire Station",
                "payload": "Fire Station"
            }
        ]
       }
    })

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers,
                      data=quick_reply)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def create_generic_template(sender_id, name, subtitle, image_url, phone, navigation_url):
    log("inside create generic template method")
    response_msg = json.dumps(
        {"recipient": {"id": sender_id},
         "message": {
             "attachment": {
                 "type": "template",
                 "payload": {
                     "template_type": "generic",
                     "elements": [
                         {
                             "title": name,
                             "subtitle": subtitle,
                             "image_url": image_url,
                             "buttons": [
                                 {
                                     "type": "postback",
                                     "payload": "Call",
                                     "title": "Call"
                                 },
                                 {
                                     "type": "web_url",
                                     "title": "Navigate",
                                     "url": navigation_url
                                 }
                             ]
                         }
                     ]
                 }
             }
         }
         })

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers,
                      data=response_msg)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)

