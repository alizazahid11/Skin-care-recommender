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

from aiogram import Dispatcher
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from pymongo import MongoClient


import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from dotenv import load_dotenv 
from rasa_sdk.events import SlotSet , EventType 
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import  SessionStarted, ActionExecuted

load_dotenv() # [INFO]: load environment variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # [INFO]: default method -> os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")


class ActionResetSlots(Action):
    def name(self) -> str:
        return "action_reset_slots"

    def run(self, dispatcher, tracker, domain):
        # Reset the slots
        dispatcher.utter_message(text="Reset.")
        return [
            SlotSet("skin_type", None),
            SlotSet("skin_concern", None),
            SlotSet("category", None),
            SlotSet("reviews", None),
        ]
    

 
# class ActionSessionStart(Action):
#     def name(self) -> Text:
#         return "action_session_start"

#     async def run(
#         self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message(response="utter_greet")
#         # the session should begin with a `session_started` event and an `action_listen`
#         # as a user message follows
#         return [SessionStarted(), ActionExecuted("action_listen")]



class ActionRecommendProducts(Action):
    def name(self) -> str:
        return "action_recommend_products_from_db"

    def run(self, dispatcher, tracker, domain):
        # Connect to MongoDB
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client.get_database('recommendation_system_database')
        products_collection = db['products_information']
        reviews_collection = db['reviews']

        # Get the slots from the tracker
        skin_concern = tracker.get_slot('skin_concern')
        skin_type = tracker.get_slot('skin_type')
        category = tracker.get_slot('category')
        reviews_choice = tracker.get_slot('reviews')

        if not skin_concern or not skin_type:
            dispatcher.utter_message(text="Please specify both your skin concern and skin type so I can recommend the best products.")
            return []

        # Handle multiple skin concerns (split by comma or space)
        skin_concerns = [concern.strip() for concern in skin_concern.split(",")]

        # Query MongoDB for matching products
        matching_products = self.get_matching_products(products_collection, skin_concerns, skin_type, category)

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
                    f"   URL: {product['URL']}\n"
                )

                # If the user wants reviews, fetch reviews
                if reviews_choice and reviews_choice.lower() == "yes":
                    product_reviews = self.get_reviews_for_product(reviews_collection, product['Product Name'])

                    if product_reviews:
                        recommendations += "   Reviews:\n"
                        for i, review in enumerate(product_reviews[:5], start=1):  # Show max 5 reviews
                            roman_index = self.to_roman(i)
                            recommendations += f"      {roman_index}. {review['ReviewText']} ({review['Rating']}⭐)\n"
                    else:
                        recommendations += "   Reviews: No reviews found.\n"

                recommendations += "\n"  # Add spacing between products

            # Send recommendations to the user
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

    def to_roman(self, number):
        """
        Convert an integer to a Roman numeral.
        """
        roman_numerals = [
            (1, "I"), (4, "IV"), (5, "V"), (9, "IX"), 
            (10, "X"), (40, "XL"), (50, "L"), 
            (90, "XC"), (100, "C"), (400, "CD"), 
            (500, "D"), (900, "CM"), (1000, "M")
        ]
        result = ""
        for value, numeral in reversed(roman_numerals):
            while number >= value:
                result += numeral
                number -= value
        return result

    def get_matching_products(self, collection, skin_concerns, skin_type, category):
        """
        Query the MongoDB collection for products matching the criteria.
        """
        # Build query for skin concerns (OR condition)
        skin_concern_query = {"$or": [{"Benefit": {"$regex": concern, "$options": "i"}} for concern in skin_concerns]}

        # Build query for skin type (Skin Type must match or be 'All')
        skin_type_query = {"$or": [{"Skin Type": {"$regex": skin_type, "$options": "i"}}, {"Skin Type": "All"}]}

        # Base query combining skin concerns and skin type
        query = {"$and": [skin_concern_query, skin_type_query]}

        # Add category filter if provided
        if category and category.lower() != "no":
            query["$and"].append({"Category": {"$regex": category, "$options": "i"}})

 
        # Fetch matching products
        products = collection.find(query)
        return list(products)

    def get_reviews_for_product(self, reviews_collection, product_name):
        """
        Fetch reviews for a specific product from the reviews collection.
        """
        return list(reviews_collection.find({"Name": product_name}))

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
            dispatcher.utter_message("Please give proper input.")
            print(f"[Gemini] Error: {e}")




# class ValidateSkinForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_skin_form"

#     async def extract_category(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> Dict[Text, Any]:
#         # If the user does not mention category, skip it
#         category = tracker.latest_message.get('text', None)
#         return {"category": category if category else None}

#     async def extract_price_range(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> Dict[Text, Any]:
#         # If the user does not mention price range, skip it
#         price_range = tracker.latest_message.get('text', None)
#         return {"price_range": price_range if price_range else None}

#     def validate_category(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#         # Allow user to leave category empty (skip validation)
#         if not slot_value:
#             return {"category": None}
#         return {"category": slot_value}

#     def validate_price_range(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> Dict[Text, Any]:
#         # Allow user to leave price_range empty (skip validation)
#         if not slot_value:
#             return {"price_range": None}
#         # Optional: Add validation for price range format (e.g., "1000-5000")
#         try:
#             low, high = map(int, slot_value.split("-"))
#             if low < high:
#                 return {"price_range": slot_value}
#         except ValueError:
#             dispatcher.utter_message(text="Please provide a valid price range in the format 'min-max'.")
#             return {"price_range": None}

# class ActionRecommendProducts(Action):
#     def name(self) -> str:
#         return "action_recommend_products_from_db"

#     def run(self, dispatcher, tracker, domain):
#         # Connect to MongoDB
#         client = MongoClient(MONGODB_CONNECTION_STRING)
#         db = client.get_database('recommendation_system_database')
#         collection = db['products_information']

#         # Get the slots from the tracker
#         skin_concern = tracker.get_slot('skin_concern')
#         skin_type = tracker.get_slot('skin_type')
#         # category = tracker.get_slot('category')  # Category slot
#         # price_range = tracker.get_slot('price_range')  # Price range slot

#         if not skin_concern or not skin_type:
#             dispatcher.utter_message(text="Please specify both your skin concern and skin type so I can recommend the best products.")
#             return []

#         # Handle multiple skin concerns (split by comma or space)
#         skin_concerns = [concern.strip() for concern in skin_concern.split(",")]

#         # # Parse the price range if provided
#         # min_price, max_price = None, None
#         # if price_range:
#         #     try:
#         #         min_price, max_price = map(int, price_range.split("-"))
#         #     except ValueError:
#         #         dispatcher.utter_message(text="Invalid price range format. Please use the format 'min-max', e.g., '1000-5000'.")
#         #         return []

#         # Query MongoDB for matching products
#         matching_products = self.get_matching_products(collection, skin_concerns, skin_type, #category, min_price, max_price
#         )

#         if matching_products:
#             # Analyze common ingredients
#             common_ingredients = self.get_common_ingredients(matching_products)

#             # Sort products by rating (descending)
#             matching_products.sort(key=lambda x: x['Product Rating'], reverse=True)

#             # Create a response message
#             recommendations = ""
#             for index, product in enumerate(matching_products, start=1):
#                 recommendations += (
#                     f"{index}. Product: {product['Product Name']}\n"
#                     f"   Category: {product['Category']}\n"
#                     f"   Ingredients: {product['Ingredients']}\n"
#                     f"   Price: {product['price_in_pkr']} PKR\n"
#                     f"   Benefits: {product['Benefit']}\n"
#                     f"   Rating: {product['Product Rating']}⭐\n"
#                     f"   URL: {product['URL']}\n\n"
#                 )

#             # Construct a message with common ingredients and recommendations
#             dispatcher.utter_message(
#                 text=(
#                     f"Based on your skin concerns ({', '.join(skin_concerns)}), these ingredients might help:\n"
#                     f"{', '.join(common_ingredients)}\n\n"
#                     f"Here are some of the best products based on your preferences:\n\n{recommendations}"
#                 )
#             )
#         else:
#             dispatcher.utter_message(
#                 text="Sorry, I couldn't find any products matching your preferences."
#             )

#         return []

#     def get_matching_products(self, collection, skin_concerns, skin_type, #category, min_price, max_price
#                               ):
#         """
#         Query the MongoDB collection for products matching the criteria.
#         """
#         # Build query for skin concerns (OR condition)
#         skin_concern_query = {"$or": [{"Benefit": {"$regex": concern, "$options": "i"}} for concern in skin_concerns]}

#         # Build query for skin type (Skin Type must match or be 'All')
#         skin_type_query = {"$or": [{"Skin Type": {"$regex": skin_type, "$options": "i"}}, {"Skin Type": "All"}]}

#         # Optional filters
#         # category_query = {"Category": {"$regex": category, "$options": "i"}} if category else {}
#         # price_query = {"price_in_pkr": {"$gte": min_price, "$lte": max_price}} if min_price is not None and max_price is not None else {}

#         # Combine all queries
#         query = {"$and": [skin_concern_query, skin_type_query]}
#         # if category_query:
#         #     query["$and"].append(category_query)
#         # if price_query:
#         #     query["$and"].append(price_query)

#         # Fetch matching products
#         products = collection.find(query)
#         return list(products)
#     def get_common_ingredients(self, products):
#         """
#         Analyze the ingredients of the matching products to find the most common ones.
#         """
#         from collections import Counter

#         # Extract all ingredients from the products
#         all_ingredients = []
#         for product in products:
#             ingredients = product.get("Ingredients")
#             if isinstance(ingredients, str):  # Ensure 'Ingredients' is a string before splitting
#                 all_ingredients.extend(ingredients.split(", "))

#         # Count the frequency of each ingredient
#         ingredient_counts = Counter(all_ingredients)

#         # Return the top 5 most common ingredients
#         common_ingredients = [ingredient for ingredient, _ in ingredient_counts.most_common(5)]
#         return common_ingredients

# class ActionRecommendProducts(Action):
#     def name(self) -> str:
#         return "action_recommend_products_from_db"

#     def run(self, dispatcher, tracker, domain):
#         # Connect to MongoDB
#         client = MongoClient(MONGODB_CONNECTION_STRING)
#         db = client.get_database('recommendation_system_database')
#         collection = db['products_information']

#         # Get the slots from the tracker
#         skin_concern = tracker.get_slot('skin_concern')
#         skin_type = tracker.get_slot('skin_type')
#         category = tracker.get_slot('category')
#         price_range = tracker.get_slot('price_range')

#         if not skin_concern or not skin_type:
#             dispatcher.utter_message(text="Please specify both your skin concern and skin type so I can recommend the best products.")
#             return []

#         # Handle multiple skin concerns
#         skin_concerns = [concern.strip() for concern in skin_concern.split(",")]

#         # Build query
#         query = self.build_query(skin_concerns, skin_type, category, price_range)

#         # Fetch matching products
#         matching_products = list(collection.find(query))
#         if matching_products:
#             # Analyze and sort products
#             matching_products.sort(key=lambda x: x['Product Rating'], reverse=True)
#             self.send_recommendations(dispatcher, matching_products, skin_concerns)
#         else:
#             dispatcher.utter_message(text="Sorry, I couldn't find any products matching your preferences.")

#         return []

#     def build_query(self, skin_concerns, skin_type, category, price_range):
#         # Build query for skin concerns (OR condition)
#         skin_concern_query = {"$or": [{"Benefit": {"$regex": concern, "$options": "i"}} for concern in skin_concerns]}
#         # Query for skin type
#         skin_type_query = {"$or": [{"Skin Type": {"$regex": skin_type, "$options": "i"}}, {"Skin Type": "All"}]}

#         # Additional filters
#         category_query = {"Category": {"$regex": category, "$options": "i"}} if category else {}
#         price_query = self.build_price_query(price_range)

#         # Combine queries
#         query = {"$and": [skin_concern_query, skin_type_query]}
#         if category_query:
#             query["$and"].append(category_query)
#         if price_query:
#             query["$and"].append(price_query)

#         return query

#     def build_price_query(self, price_range):
#         if price_range:
#             try:
#                 low, high = map(int, price_range.split("-"))
#                 return {"price_in_pkr": {"$gte": low, "$lte": high}}
#             except ValueError:
#                 return {}
#         return {}

#     def send_recommendations(self, dispatcher, matching_products, skin_concerns):
#         recommendations = ""
#         for index, product in enumerate(matching_products, start=1):
#             recommendations += (
#                 f"{index}. Product: {product['Product Name']}\n"
#                 f"   Category: {product['Category']}\n"
#                 f"   Price: {product['price_in_pkr']} PKR\n"
#                 f"   Rating: {product['Product Rating']}⭐\n"
#                 f"   URL: {product['URL']}\n\n"
#             )
#         dispatcher.utter_message(
#             text=(f"Here are some recommended products for {', '.join(skin_concerns)}:\n\n{recommendations}")
#         )

