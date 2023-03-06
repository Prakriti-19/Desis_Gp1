## Donation App

This is a simple donation app that allows users to donate to a charity of their choice. The app is built using the Django framework and uses the Stripe API to process payments.

# Desis_Gp1

## Project Name: 
Hands For Hunger

## Problem Statement:

People dying of hunger exist in this world but very few people take steps to prevent it by feeding the needy. Can we see a world where no one dies of hunger? Then how do we motivate more people to join hands and donate food they have, instead of wasting it? 

## Project Summary:

To solve this problem we bring to you our website that aims at creating a two-way connection between the potential donors and NGOs. Whenever you have leftover food, raise a request in our app through which people from various NGOs would collect the food and send it to food banks to distribute them to the needy.

In case you're wondering…
I’m a NGO. What can I do using this app?
Had days when you needed food urgently for a group of people. Well, our app allows you to raise a request for food through which all the users are alerted and can donate as much as they can if they have food.

Why would I want to use this app and spend time raising requests for a small quantity of food?
There are many people in the world who could live a day more because of the food you donate. This reason isn’t enough?
Also, donating food through our app gives you coins which could help redeem many exciting things and offers.


## Tech Stack Used:
* Frontend: HTML, CSS
* Backend: Django 
* Database: SQL

## Project Features:

* Authentication and Registration: On visiting the site one will be identified as a food donor or an NGO representative(or any social workers attempting to help in the services for needy) and then will be verified in order to get logged in and the login data will be stored in our databases for further hasslefree sign-ins in future.

* Establishing a two-way connection: Our two main end users being donors and NGO representatives would be shown the other’s availability nearest to them i.e,the donors would be shown the window which shows all the available social workers near them and vice-versa.

* Request pushing and pulling: Once an NGO has pushed a request and has achieved the required standards and amount of food, that request will be then deleted.

* GPS location tracking: To locate the donors and NGOs in the same vicinity we’ll be tracking their location.

* Filtration: The food inventory can be filtered depending upon the location, quantity and use-by date of the food.

* Reward based encouragement: Depending on the amount of food donated each user can earn coins and grow their profile. These coins can then be either donated to NGO's or can be redeemed to get goodies

### Installation

1. Clone the repository
2. Create a virtual environment and activate it
3. Install the requirements using `pip install -r requirements.txt`
4. Run the migrations using `python manage.py migrate`
5. Run the start command using `python manage.py runserver`

### Usage

1. Create a Stripe account and get your API keys
2. Create a `.env` file and add your Stripe API keys
3. Run the app using `python manage.py runserver`



