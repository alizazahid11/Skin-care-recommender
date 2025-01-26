# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
#
# class ActionHelloWorld(Action):
#     def name(self) -> Text: # [INFO]: tied with domain.yml -> actions
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: # [INFO]: Dict[Text, Any] -> dict
#         dispatcher.utter_message(text="Hello World!")
#         return [] # [INFO]: can return events as lists


import os

from tkinter import EventType
from typing import Any, Text, Dict, List # [INFO]: for type hinting (optional)

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from pymongo import MongoClient

# import openai
# from openai import OpenAI

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from dotenv import load_dotenv 
from rasa_sdk.events import SlotSet


load_dotenv() # [INFO]: load environment variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # [INFO]: default method -> os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")




class ActionResetSlots(Action):
    def name(self) -> str:
        return "action_reset_slots"

    def run(self, dispatcher, tracker, domain):
        # Reset the slots
        dispatcher.utter_message(text="Your form has been reset.")
        return [
            SlotSet("skin_type", None),
            SlotSet("skin_concern", None)
        ]

class ActionRetrieveReviews(Action):

    def name(self) -> Text:
        return "action_retrieve_reviews"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        

        # Get the product name from the slot
        product_name = tracker.get_slot("product_name")

        # Skip if product_name is empty
        if not product_name:
            return []


        # MongoDB connection setup
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client.get_database('recommendation_system_database')
        collection = db['reviews']



        # Query MongoDB for reviews of the given product name
        reviews = collection.find({"Name": product_name})

        # Collect ReviewText from the reviews
        review_texts = [review["ReviewText"] for review in reviews]

        if not review_texts:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any reviews for '{product_name}'.")
        else:
            # Format the reviews for user output
            formatted_reviews = "\n\n".join(review_texts)
            dispatcher.utter_message(text=f"Here are the reviews for '{product_name}':\n\n{formatted_reviews}")

        return []



class ActionRecommendProducts(Action):
    def name(self) -> str:
        return "action_recommend_products_from_db"

    def run(self, dispatcher, tracker, domain):
        # Connect to MongoDB
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client.get_database('recommendation_system_database')
        collection = db['products_information']

        # Get the slots from the tracker
        skin_concern = tracker.get_slot('skin_concern')
        skin_type = tracker.get_slot('skin_type')
        # category = tracker.get_slot('category')  # Category slot
        # price_range = tracker.get_slot('price_range')  # Price range slot

        if not skin_concern or not skin_type:
            dispatcher.utter_message(text="Please specify both your skin concern and skin type so I can recommend the best products.")
            return []

        # Handle multiple skin concerns (split by comma or space)
        skin_concerns = [concern.strip() for concern in skin_concern.split(",")]

        # # Parse the price range if provided
        # min_price, max_price = None, None
        # if price_range:
        #     try:
        #         min_price, max_price = map(int, price_range.split("-"))
        #     except ValueError:
        #         dispatcher.utter_message(text="Invalid price range format. Please use the format 'min-max', e.g., '1000-5000'.")
        #         return []

        # Query MongoDB for matching products
        matching_products = self.get_matching_products(collection, skin_concerns, skin_type, #category, min_price, max_price
        )

        if matching_products:
            # Analyze common ingredients
            common_ingredients = self.get_common_ingredients(matching_products)

            # Sort products by rating (descending)
            matching_products.sort(key=lambda x: x['Product Rating'], reverse=True)

            # Create a response message
            recommendations = ""
            for index, product in enumerate(matching_products, start=1):
                recommendations += (
                    f"{index}. Product: {product['Product Name']}\n"
                    f"   Category: {product['Category']}\n"
                    f"   Ingredients: {product['Ingredients']}\n"
                    f"   Price: {product['price_in_pkr']} PKR\n"
                    f"   Benefits: {product['Benefit']}\n"
                    f"   Rating: {product['Product Rating']}⭐\n"
                    f"   URL: {product['URL']}\n\n"
                )

            # Construct a message with common ingredients and recommendations
            dispatcher.utter_message(
                text=(
                    f"Based on your skin concerns ({', '.join(skin_concerns)}), these ingredients might help:\n"
                    f"{', '.join(common_ingredients)}\n\n"
                    f"Here are some of the best products based on your preferences:\n\n{recommendations}"
                )
            )
        else:
            dispatcher.utter_message(
                text="Sorry, I couldn't find any products matching your preferences."
            )

        return []

    def get_matching_products(self, collection, skin_concerns, skin_type, #category, min_price, max_price
                              ):
        """
        Query the MongoDB collection for products matching the criteria.
        """
        # Build query for skin concerns (OR condition)
        skin_concern_query = {"$or": [{"Benefit": {"$regex": concern, "$options": "i"}} for concern in skin_concerns]}

        # Build query for skin type (Skin Type must match or be 'All')
        skin_type_query = {"$or": [{"Skin Type": {"$regex": skin_type, "$options": "i"}}, {"Skin Type": "All"}]}

        # Optional filters
        # category_query = {"Category": {"$regex": category, "$options": "i"}} if category else {}
        # price_query = {"price_in_pkr": {"$gte": min_price, "$lte": max_price}} if min_price is not None and max_price is not None else {}

        # Combine all queries
        query = {"$and": [skin_concern_query, skin_type_query]}
        # if category_query:
        #     query["$and"].append(category_query)
        # if price_query:
        #     query["$and"].append(price_query)

        # Fetch matching products
        products = collection.find(query)
        return list(products)
    def get_common_ingredients(self, products):
        """
        Analyze the ingredients of the matching products to find the most common ones.
        """
        from collections import Counter

        # Extract all ingredients from the products
        all_ingredients = []
        for product in products:
            ingredients = product.get("Ingredients")
            if isinstance(ingredients, str):  # Ensure 'Ingredients' is a string before splitting
                all_ingredients.extend(ingredients.split(", "))

        # Count the frequency of each ingredient
        ingredient_counts = Counter(all_ingredients)

        # Return the top 5 most common ingredients
        common_ingredients = [ingredient for ingredient, _ in ingredient_counts.most_common(5)]
        return common_ingredients

# class ActionFetchIngredientInfo(Action):
#     def name(self) -> Text:
#         return "action_fetch_ingredient_info"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         ingredient = tracker.get_slot("ingredient")
#         benefits, skin_types = self.get_ingredient_info(ingredient)

#         dispatcher.utter_message(
#             text=f"The ingredient {ingredient} is known for {benefits}. It is suitable for {skin_types} skin types."
#         )
#         return []

#     def get_ingredient_info(self, ingredient):
#         # Replace with actual logic to fetch ingredient details
#         return "hydrating properties", "dry, normal, and combination"


# class ActionSayPhone(Action): # [INFO]: not needed, just for testing
#     def name(self) -> Text:
#         return "action_say_phone"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
#         phone = tracker.get_slot("phone")

#         if not phone :
#             dispatcher.utter_message(text="Sorry i dont know your phone number ")
#         else :
#             dispatcher.utter_message(text=f"Your phone number is {phone} :) ")

#         return []


# class ActionSaySkinConcern(Action):
#     def name(self) -> Text: # tied with domain.yml -> actions
#         return "action_say_skin_concern"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
#         skin_concern = tracker.get_slot("skin_concern")

#         if not skin_concern :
#             dispatcher.utter_message(text="Sorry i dont know your skin concern ")
#         else :
#             dispatcher.utter_message(text=f"Your skin concern is {skin_concern} :) ")

#         return []
    

# class AskForSlotAction(Action):
#     def name(self) -> Text:
#         return "action_ask_skin_concern"

#     def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[EventType]:
#         skin_type = tracker.get_slot("skin_type")
#         dispatcher.utter_message(text=f"So {skin_type}, what is your skin concern ?")
#         return []


# class ActionFallbackToChatGPT(Action): # [ISSUE]: too many requests to OpenAI API, rate limit exceeded -> WHY?
#     def name(self):
#         return "action_fallback_to_chatgpt"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         user_message = tracker.latest_message.get("text")
#         try:
#             client = OpenAI(api_key=OPENAI_API_KEY)
#             response =  client.chat.completions.create(
#                 model="gpt-4o-mini", # others: "gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"
#                 messages=[ # [NOTE]: multiple messages or there structure might be the issue
#                     {"role": "system", "content": "You are a helpful assistant."},
#                     {"role": "user", "content": user_message}
#                 ]
#             )
#             chatgpt_response = response['choices'][0]['message']['content'].strip() # [NOTE]: check for exception safety
#             dispatcher.utter_message(chatgpt_response)
        
#         except openai.OpenAIError as e:
#             dispatcher.utter_message("I'm sorry, I couldn't process your request.")
#             print(f"OpenAI API error: {e}")

#         except openai.APIConnectionError as e:
#             dispatcher.utter_message("I'm sorry, I couldn't connect to the OpenAI API.")
#             print(f"API connection error: {e}")

#         except openai.InvalidRequestError as e:
#             dispatcher.utter_message("I'm sorry, there was an issue with the request to the OpenAI API.")
#             print(f"Invalid request error: {e}")

#         except openai.RateLimitError as e:
#             dispatcher.utter_message("I'm sorry, the OpenAI API rate limit has been exceeded.")
#             print(f"Rate limit error: {e}")

#         except Exception as e:
#             dispatcher.utter_message("An unexpected error occurred.")
#             print(f"Error: {e}")

#         return []


class ActionFallbackToGemini(Action):
    def name(self):
        return "action_fallback_to_gemini"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_message = tracker.latest_message.get("text")
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")

            safety_settings = [ # [INFO]: safety settings for content moderation, optional
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            response = model.generate_content(user_message, safety_settings=safety_settings)
            gemini_response = response.text.strip()
            dispatcher.utter_message(gemini_response)
        
        except google_exceptions.InvalidArgument as e:
            print(f"[Gemini] Invalid argument error: {e}")

        except google_exceptions.PermissionDenied as e:
            print(f"[Gemini] Permission denied: {e}")

        except google_exceptions.NotFound as e:
            print(f"[Gemini] Resource not found: {e}")

        except google_exceptions.GoogleAPICallError as e: # Fallback for other API call errors
            print(f"[Gemini] An API call error occurred: {e}")

        except Exception as e:
            dispatcher.utter_message("An unexpected error occurred.")
            print(f"[Gemini] Error: {e}")


# class ActionFetchProductDetails(Action): # [ISSUE]: improve query (should retrieve info from product description/details if msg isn't clear), old method
#     def name(self) -> str:
#         return "action_fetch_product_details"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         # Connect to MongoDB Atlas
#         client = MongoClient(MONGODB_CONNECTION_STRING)
#         db = client.get_database('recommendation_system_database')
#         collection = db['products']  # Replace with your collection name

#         # Get the user query (you can extract this from the tracker)
#         product_name = tracker.get_slot('product_name')  # Assuming you captured the product name in a slot

#         # Query the MongoDB database
#         product = collection.find_one({"ProductName": product_name})

#         if product:
#             # Respond with product details
#             message = f"Product: {product['ProductName']}\n"
#             message += f"Category: {product['Category']}\n"
#             message += f"Skin Type: {product['SkinType']}\n"
#             message += f"Benefits: {product['Benefits']}\n"
#             message += f"Active Ingredients: {product['ActiveIngredients']}\n"
#             message += f"Sentiment: {product['Sentiment']}\n"
#         else:
#             message = "Sorry, I couldn't find any details about that product."

#         # Send the response back to the user
#         dispatcher.utter_message(text=message)

#         return []
