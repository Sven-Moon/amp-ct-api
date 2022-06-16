from app import app
from flask import jsonify
from app.models import db, Recipe, RecipeBox, RecipeIngredient, User, Ingredient, Day, Schedule, ShoppingList


@app.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200




# This is your test secret API key.

from flask import Flask, render_template, jsonify, request

import stripe
import json
import os
stripe.api_key = 'sk_test_51LAQTdJvxpEoTgBTUcxBvsb3HLNl7nsVl3r75XEmlzsR3zShyv34m3VtZ2vObJWe9Vkz6kPnwkIknElSssAewlbl00AVuisEhJ'
def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 1400


@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['items']),
            currency='eur',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403
    