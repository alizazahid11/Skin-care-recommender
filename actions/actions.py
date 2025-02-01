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
        #dispatcher.utter_message(text="Reset.")
        return [
            SlotSet("skin_type", None),
            SlotSet("skin_concern", None),
            SlotSet("category", None),
            SlotSet("review_sentiment", None),
            SlotSet("sentiment_score", None),
        ]

class ValidateSkinForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_skin_form"

    def validate_skin_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """
        Validate the 'skin_type' slot.
        Ensures the user enters a valid skin type from the provided list.
        """

        # ✅ Full list of allowed skin types from your data
        allowed_skin_types = {
            "oily", "dry", "combination", "sensitive", "normal", "all", "acne prone",
            "acne-prone", "acne prone/blemish", "acne prone, blemish", "acne prone/oily",
            "acne-prone/inflammed/irritated", "aged/all", "aging", "aging/all", "aging/uneven",
            "balanced/dry", "balanced/oily", "bumpy", "bumpy/dry", "combination/all",
            "combination/sensitive/normal", "combination/oily", "damaged",
            "damaged/dullrough/dehydrated/irritated", "dehydrated/acne prone/pigmented",
            "dehydrated/dry/all", "dry/sensitive", "dry/aging", "dry/all",
            "dry/damaged skin", "dry/dehydrated/damaged", "dry/flaky",
            "dry/itchy", "dry/oily/sensitive", "dry/rough", "dry/rough lips",
            "dry/uneven", "dry/very dry", "dull/aging", "dull/dry",
            "dull/uneven/aging", "flared/irritated skin", "hair/all",
            "healthy/aging", "inflammed/acne prone/fungal", "inflammed/all",
            "mature/aging", "normal/dry", "normal/dry/sensitive", "normal/extra dry",
            "normal/oily", "normal/sensitive", "oily/acne prone", "oily/acne prone/bumpy",
            "oily/acne prone/dull", "oily/combination", "oily/combination/acne prone",
            "oily/combination/textured", "oily/sensitive", "rough/bumpy",
            "rough/dry", "rough/oily", "sensitive skin", "sensitive/dry",
            "sensitive/acne prone", "sensitive/all", "uneven/dull/tanned",
            "very dry", "clogged/oily/acne prone"
        }

        # ✅ Normalize input: Convert to lowercase, remove extra spaces
        normalized_input = slot_value.lower().strip()

        # ✅ Replace variations: Convert `/` and `,` into spaces for better matching
        normalized_input = normalized_input.replace("/", " ").replace(",", " ")

        # ✅ Final Check: See if the normalized input matches an allowed type
        if normalized_input in allowed_skin_types:
            return {"skin_type": normalized_input}  # ✅ Valid skin type

        else:
            dispatcher.utter_message(
                text=f"Invalid skin type. Please enter one of the following: {', '.join(sorted(allowed_skin_types))}."
            )
            return {"skin_type": None}  # ❌ Re-ask for valid input
        

    def validate_review_sentiment(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """
        Validate the 'review_sentiment' slot.
        Ensures user enters only 'positive', 'negative', 'neutral','all' or 'no'.
        """
        allowed_values = ["positive", "negative", "neutral", "no" , "all"]
        selected_values = [val.strip().lower() for val in slot_value.split(",")]

        # Check if user entered 'no' (skip reviews)
        if "no" in selected_values:
            return {"review_sentiment": "no"}

        # Filter valid sentiments
        valid_sentiments = [sent for sent in selected_values if sent in allowed_values]

        if valid_sentiments:
            return {"review_sentiment": valid_sentiments}  # Store valid sentiments
        else:
            dispatcher.utter_message(
                text="Invalid input. Please enter one or more of: 'positive', 'negative', 'neutral', or 'no'."
            )
            return {"review_sentiment": None}  # Re-ask for valid input




class ActionRecommendProducts(Action):
    def name(self) -> str:
        return "action_recommend_products_from_db"

    def run(self, dispatcher, tracker, domain):
        # Connect to MongoDB
        client = MongoClient(MONGODB_CONNECTION_STRING)
        db = client.get_database('final_database')
        products_collection = db['products']
        reviews_collection = db['reviews']

        # Get slots from tracker
        skin_concern = tracker.get_slot('skin_concern')
        skin_type = tracker.get_slot('skin_type')
        category = tracker.get_slot('category')
        review_sentiments = tracker.get_slot('review_sentiment')
        sentiment_score_choice = tracker.get_slot('sentiment_score')  # New slot for sentiment analysis

        if not skin_concern or not skin_type:
            dispatcher.utter_message(text="Please specify both your skin concern and skin type so I can recommend the best products.")
            return []

        # Handle multiple skin concerns
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
                  
                )

                # **Sentiment Analysis for the Product**
                if sentiment_score_choice and sentiment_score_choice.lower() == "yes":
                    sentiment_summary = self.get_sentiment_summary(reviews_collection, product["_id"])
                    recommendations += sentiment_summary  # Append sentiment summary to the response

                # **Fetch and format reviews if the user selected sentiment categories**
                if review_sentiments and review_sentiments != "no":
                    # If "all" is selected, fetch all review types
                    if "all" in review_sentiments:
                        selected_sentiments = ["positive", "neutral", "negative"]
                    else:
                        selected_sentiments = [s.strip().lower() for s in review_sentiments]

                    # Fetch reviews for the product
                    product_reviews = self.get_reviews_for_product(reviews_collection, product["_id"], selected_sentiments)

                    if product_reviews:
                        recommendations += "\n"

                        # Organizing reviews by sentiment category
                        grouped_reviews = {"positive": [], "neutral": [], "negative": []}
                        for review in product_reviews:
                            sentiment = review["Sentiment"].lower()
                            if sentiment in grouped_reviews:
                                grouped_reviews[sentiment].append(review)

                        # Add reviews to response in categorized manner
                        for sentiment, reviews in grouped_reviews.items():
                            if reviews:
                                sentiment_title = sentiment.capitalize()  # E.g., "Positive", "Neutral", "Negative"
                                recommendations += f"      {sentiment_title} Reviews:\n"
                                for i, review in enumerate(reviews[:5], start=1):  # Show max 5 reviews per category
                                    roman_index = self.to_roman(i)
                                    recommendations += f"         {roman_index}. {review['ReviewText']} ({review['Rating']}⭐)\n"

                    else:
                        recommendations += "   Reviews: No matching reviews found.\n"

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
        """Convert an integer to a Roman numeral."""
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

    def get_sentiment_summary(self, reviews_collection, product_id):
        """
        Fetch sentiment statistics for a product:
        - Count how many reviews are positive, neutral, and negative.
        - Calculate percentage distribution.
        - Compute average confidence scores.
        """

        # Fetch all reviews for this product
        reviews = list(reviews_collection.find({"product_id": product_id}))

        if not reviews:
            return "   Sentiment Analysis: No reviews available for this product.\n"

        # Initialize counters
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        confidence_scores = {"positive": [], "neutral": [], "negative": []}

        # Count sentiments and collect confidence scores
        for review in reviews:
            sentiment = review["Sentiment"].lower()
            confidence = review["Confidence_score"]

            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
                confidence_scores[sentiment].append(confidence)

        # Compute percentages
        total_reviews = sum(sentiment_counts.values())
        sentiment_percentages = {
            sentiment: (count / total_reviews) * 100 if total_reviews > 0 else 0
            for sentiment, count in sentiment_counts.items()
        }

        # Compute average confidence scores
        average_confidence = {
            sentiment: (sum(scores) / len(scores) * 100 if scores else 0)
            for sentiment, scores in confidence_scores.items()
        }

        # Format the sentiment summary
        sentiment_summary = "   Sentiment Analysis:\n"
        for sentiment, percentage in sentiment_percentages.items():
            sentiment_summary += (
                f"      {sentiment.capitalize()} Sentiment: {percentage:.1f}% "
                f"(Avg. Confidence: {average_confidence[sentiment]:.1f}%)\n"
            )

        return sentiment_summary

    def get_matching_products(self, collection, skin_concerns, skin_type, category):
        """Query MongoDB for products matching the criteria."""
        skin_concern_query = {"$or": [{"Benefit": {"$regex": concern, "$options": "i"}} for concern in skin_concerns]}
        skin_type_query = {"$or": [{"Skin Type": {"$regex": skin_type, "$options": "i"}}, {"Skin Type": "All"}]}
        query = {"$and": [skin_concern_query, skin_type_query]}

        if category and category.lower() != "no":
            query["$and"].append({"Category": {"$regex": category, "$options": "i"}})

        return list(collection.find(query))
 
    def get_reviews_for_product(self, reviews_collection, product_id, sentiments):
        """Fetch reviews for a specific product based on sentiment selection."""
        if "all" in sentiments:
            # Retrieve all sentiment types
            return list(reviews_collection.find({"product_id": product_id}))
        else:
            sentiment_filters = [{"Sentiment": sentiment} for sentiment in sentiments]
            query = {"$and": [{"product_id": product_id}, {"$or": sentiment_filters}]}
            return list(reviews_collection.find(query))
  
    
    def get_common_ingredients(self, products):
        """Analyze the ingredients of the matching products to find the most common ones."""
        from collections import Counter
        all_ingredients = []
        for product in products:
            ingredients = product.get("Ingredients")
            if isinstance(ingredients, str):
                all_ingredients.extend(ingredients.split(", "))

        ingredient_counts = Counter(all_ingredients)
        return [ingredient for ingredient, _ in ingredient_counts.most_common(5)]






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

