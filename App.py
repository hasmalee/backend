from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
import hashlib
import secrets
from flask_mail import Mail, Message
from untitled1 import locationbased
from untitled1 import longrestauranttypebased
from untitled1 import longfamouscusinebasedd
from untitled1 import longfamouscusinebasedddd
from untitled1 import longfamouscusinebaseddddd
from untitled1 import longfamouscusinebasedddddd

# Define a global variable to store the user's location
user_location = None
restaurant_type = None
cuisine_type = None
cost_person = None
allergy_food = None
addition_rec = None
user_choice = None

app = Flask(__name__)
CORS(app)

# MySQL configuration
app.config['MYSQL_HOST'] = 'basi1pxl4ntjssrgwz1j-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'utoorzpftuwjs2pf'
app.config['MYSQL_PASSWORD'] = '3UmnNar6UTbSV6K8dtZm'
app.config['MYSQL_DB'] = 'basi1pxl4ntjssrgwz1j'

mysql = MySQL(app) 


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        hashed_password_input = hash_password(password)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            # Extract the hashed password from the database
            hashed_password_db = user[3]  # Assuming password is stored at index 2
            if hashed_password_db == hashed_password_input:
                return jsonify({'message': 'Login successful'}), 200
            else:
                return jsonify({'error': 'Login unsuccessful: Incorrect email or password'}), 401
        else:
            return jsonify({'error': 'Login unsuccessful: Incorrect email or password'}), 401

    except Exception as e:
        return jsonify({'error': 'Failed to login: ' + str(e)}), 500
################################
#forgot password

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hasmaleevidanya@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = 'hasmaleevidanya@gmail.com'
mail = Mail(app)

# Dictionary to store password reset tokens (use a database in production)
password_reset_tokens = {}

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    try:
        email = request.json.get('email')
        if email:
            # Generate a unique token for password reset
            token = secrets.token_hex(16)
            # Store the token with the email address (should be stored securely in production)
            password_reset_tokens[email] = token
            # Send a password reset email
            msg = Message('Password Reset', recipients=[email])
            msg.body = f'Click the following link to reset your password: {request.url_root}reset_password/{token}'
            mail.send(msg)
            return jsonify({'message': 'Password reset instructions sent to your email'}), 200
        else:
            return jsonify({'error': 'Email address not provided'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to process request: ' + str(e)}), 500

@app.route('/api/reset_password/<token>', methods=['POST'])
def reset_password(token): 
    try:
        password = request.json.get('password')
        email = get_email_for_token(token)
        if email:
            # Update password in the database (replace this with your database logic)
            # After updating the password, remove the token from the dictionary
            del password_reset_tokens[email]
            return jsonify({'message': 'Password successfully reset'}), 200
        else:
            return jsonify({'error': 'Invalid or expired token'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to process request: ' + str(e)}), 500

def get_email_for_token(token):
    # Find the email associated with the token
    for email, stored_token in password_reset_tokens.items():
        if token == stored_token:
            return email
    return None


# Signup route


@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        hashed_password = hash_password(password)  # Hash the password

        # Check if email already exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            return jsonify({'error': 'Email already exists. Please use a different email.'}), 400

        # Insert the new user into the database with hashed password
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Signup successful'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to sign up: ' + str(e)}), 500

@app.route('/api/choice', methods=['GET'])
def choice():
    return jsonify({'question': "Hey there, Food Lover!☕ 🍽️ I am happy to assist you with the best restaurant to get a quality dining experience with a mix of taste, culture, ambience in a specific location .Apart from this, i can help you choose tailored recommendations according to allergy or dietary restrictions☕ 🍽️"})



# Define a route to send the location question to the frontend
@app.route('/api/get-location', methods=['GET'])
def get_location_question():
    return jsonify({'question': 'What is your location?'})
pass

# Define a function to handle user input and return the appropriate response
@app.route('/api/handle-input', methods=['POST'])
def handle_input():
    global user_location

    try:
        user_input = request.json.get('input')

        while True:
            if user_location is None:
                user_location = user_input
            else:
                user_location = request.json.get('input')

            # Call the location-based restaurant recommendation function
            response = locationbased(user_location)

            if response:
                # Assuming response is a list of restaurants
                recommendation_text = ""
                for restaurant in response:
                    recommendation_text += f"Restaurant Name: {restaurant['Restaurant_Name']}\nDescription: {restaurant['Restaurant_description']}\n"
                return jsonify({'response': recommendation_text, 'next_question': 'What is your preferred restauarnt type?'}), 200
            else:
                # Prompt the user to enter the location again
                return jsonify({'response': 'Please enter a valid location.'}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to handle input: ' + str(e)}), 500
    
# Define a route to send the restaurant type question to the frontend
@app.route('/api/get-type', methods=['GET'])
def get_restaurant_type_question():
    return jsonify({'question': 'What is your preferred restaurant type?'})
pass
# Define a route to handle the preferred restaurant type and return recommendations
@app.route('/api/handle-type', methods=['POST'])
def handle_type():
    global user_location
    global restaurant_type
    global cuisine_type

    try:
        user_input = request.json.get('input')

        if user_location is not None:  # Ensure user_location is set
            restaurant_type = user_input
            response = longrestauranttypebased(user_location, restaurant_type)

            if response:
                # Assuming response is a list of dictionaries representing recommendations
                recommendation_text = ""
                for restaurant in response:
                    recommendation_text += f"{restaurant['Restaurant_Name']}\nDescription: {restaurant['Restaurant_description']}\nType: {restaurant['Restaurant_type']}\n\n"
                
                # Setting cuisine type question after handling restaurant type
                return jsonify({'response': recommendation_text, 'next_question': 'What is your preferred cuisine type?'}), 200
            else:
                return jsonify({'response': 'No restaurants of this type in this location.'}), 404
        else:
            return jsonify({'error': 'User location is not set. Please provide the location first.'}), 400
            
    except Exception as e:
        return jsonify({'error': 'Failed to handle input: ' + str(e)}), 500
pass
@app.route('/api/get-cusinetype', methods=['GET'])
def get_cuisine_type_question():
    return jsonify({'question': 'What is your preferred cuisine type?'})
pass
@app.route('/api/handle-restaurant-type', methods=['POST'])
def handle_restaurant_type():
    global user_location
    global restaurant_type
    global cuisine_type

    try:
        user_input = request.json.get('input')
        print("Received input:", user_input)  # Log the received input

        if user_location is None or restaurant_type is None:
            return jsonify({'error': 'User location and restaurant type must be set before handling cuisine type.'}), 400
        
        # Set cuisine type based on user input
        cuisine_type = user_input
        
        # Call function to get restaurant recommendations
        response = longfamouscusinebasedd(user_location, restaurant_type, cuisine_type)

        if response:
            # Format response as recommendation text
            recommendation_text = ""
            for restaurant in response:
                recommendation_text += f"{restaurant['Restaurant_Name']}\nDescription: {restaurant['Restaurant_Description']}\nType: {restaurant['Restaurant_Type']}\n\n"
            
            # Return response along with the next question
            return jsonify({'response': recommendation_text, 'next_question': 'What is your preferred cuisine type?'}), 200
        else:
            return jsonify({'response': 'No restaurants of this type in this location.'}), 404
    
    except Exception as e:
        # Log detailed error message
        print("Error handling restaurant type:", str(e))
        return jsonify({'error': 'Failed to handle input: ' + str(e)}), 500
pass    

@app.route('/api/get-costPerson', methods=['GET'])
def get_cost_person():
    return jsonify({'question': 'What is your preferred cost per person?'})
pass    
@app.route('/api/handle-costPerson', methods=['POST'])
def handle_costPerson():
    global user_location
    global restaurant_type
    global cuisine_type
    global cost_person

    try:
        user_input = request.json.get('input')
        print("Received input:", user_input)  # Log the received input

        if user_location is None or restaurant_type is None or cuisine_type is None:
            return jsonify({'error': 'User location and restaurant type must be set before handling cuisine type.'}), 400
        
        # Set cuisine type based on user input
        cost_person = user_input
        
        # Call function to get restaurant recommendations
        response = longfamouscusinebasedddd(user_location, restaurant_type, cuisine_type,cost_person)

        if response:
            # Format response as recommendation text
            recommendation_text = ""
            for restaurant in response:
                recommendation_text += f"{restaurant['Restaurant_Name']}\nDescription: {restaurant['Restaurant_Description']}\nType: {restaurant['Restaurant_Type']}\n\n"
            
            # Return response along with the next question
            return jsonify({'response': recommendation_text, 'next_question': 'What is your budget for the meal?'}), 200
        else:
            return jsonify({'response': 'No restaurants of this type in this location.'}), 404
    
    except Exception as e:
        # Log detailed error message
        print("Error handling restaurant type:", str(e))
        return jsonify({'error': 'Failed to handle input: ' + str(e)}), 500
pass
@app.route('/api/get-allergy', methods=['GET'])
def get_allergy_question():
    return jsonify({'question': 'Do you have allergies or dietary restrictions?'})
pass
@app.route('/api/handle-allergy', methods=['POST'])
def handle_allergies():
    global user_location
    global restaurant_type
    global cuisine_type
    global cost_person
    global allergy_food

    try:
        user_input = request.json.get('input')
        print("Received input:", user_input)  # Log the received input

        if user_location is None or restaurant_type is None or cuisine_type is None or cost_person is None:
            return jsonify({'error': 'User location, restaurant type, cuisine type, and cost per person must be set before handling allergies.'}), 400
        
        # Set allergy food based on user input
        allergy_food = user_input
        
        # Call function to get restaurant recommendations
        result_df = longfamouscusinebaseddddd(user_location, restaurant_type, cuisine_type, allergy_food, cost_person)

        if not result_df.empty:
            # Format response as recommendation text
            recommendation_text = ""
            for index, row in result_df.iterrows():
                recommendation_text += f"Restaurant Name: {row['Restaurant_Name']}\nDescription: {row['Restaurant_description']}\nType: {row['Restaurant_type']}\nRecommended Dishes: {row['recommended_dishes']}\nMenu with allergies: {row['menu_with_allergy']}\nMenu without allergies: {row['menu_without_allergy']}\nAllergy food product: {row['allergy_food_product']}\nCost per person: {row['Cost_per_person']}\nReviews: {row['reviews']}"
            
            # Return response along with the next question
            return jsonify({'response': recommendation_text,'next_question': 'Any other?'}), 200
        else:
            return jsonify({'response': 'No restaurants of this type in this location.'}), 404
    
    except Exception as e:
        # Log detailed error message
        print("Error handling allergies:", str(e))
        return jsonify({'error': 'Failed to handle allergies: ' + str(e)}), 500 
pass
@app.route('/api/get-addition', methods=['GET'])
def get_addition_question():  
    return jsonify({'question': 'How can I help you to recommend the best restaurant in your area?'})
pass
@app.route('/api/handle-addition', methods=['POST'])
def handle_addition_question():
    global user_location
    global restaurant_type
    global cuisine_type
    global cost_person
    global allergy_food
    global addition_rec

    try:
        user_input = request.json.get('input')
        print("Received input:", user_input)  # Log the received input

        # if user_location is None or restaurant_type is None or cuisine_type is None or cost_person is None:
        #     return jsonify({'error': 'User location, restaurant type, cuisine type, and cost per person must be set before handling allergies.'}), 400
        
        # Set allergy food based on user input
        addition_rec = user_input
        
        # Call function to get restaurant recommendations
        result_df = longfamouscusinebasedddddd(addition_rec)

        if not result_df.empty:
            # Format response as recommendation text
            recommendation_text = ""
            for index, row in result_df.iterrows():
                recommendation_text += f"Restaurant Name: {row['Restaurant_Name']}\nDescription: {row['Restaurant_description']}\nType: {row['Restaurant_type']}\nRecommended Dishes: {row['recommended_dishes']}\nMenu with allergies: {row['menu_with_allergy']}\nMenu without allergies: {row['menu_without_allergy']}\nAllergy food product: {row['allergy_food_product']}\nCost per person: {row['Cost_per_person']}\nReviews: {row['reviews']}"
            
            # Return response along with the next question
            return jsonify({'response': recommendation_text}), 200
        else:
            return jsonify({'response': 'No restaurants of this type in this location.'}), 404
    
    except Exception as e:
        # Log detailed error message
        print("Error handling allergies:", str(e))
        return jsonify({'error': 'Failed to handle allergies: ' + str(e)}), 500 
pass


    


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)