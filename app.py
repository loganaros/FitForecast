from flask import Flask, request, render_template, redirect, session, flash
from forms import CustomizeForm, RegisterForm, LoginForm, SaveOutfitForm
from models import connect_db, db, User, Outfit
import requests, openai, re, json
from secret_keys import API_KEY, GPT_KEY, SECRET_KEY, EXTERNAL_URI, INTERNAL_URI

DATABASE_URI = EXTERNAL_URI

app = Flask(__name__)
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = SECRET_KEY

connect_db(app)
db.create_all()

openai.api_key = GPT_KEY

BASE_URL = "http://api.weatherapi.com/v1"

def validate_password(password):
    # Define password criteria
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit"
    return None

def get_outfit_recommendation(location, vibe, gender, will_it_rain, temperature, weather_description):
    # Construct a dynamic prompt
    rain_statement = "It will rain today." if will_it_rain == 1 else "It won't rain today."
    temperature_statement = f"The temperature is {temperature}°F."
    weather_context = f"The weather is described as {weather_description}."
    location_statement = f"The outfit should contextually fit in for the location of {location}."
    vibe_statement = f"The vibe of the outfit should be {vibe}."
    gender_statement = f"The gender of the wearer of the outfit should be {gender}."

    # Complete prompt to send to ChatGPT
    prompt = (
        f"Based on the following weather conditions: {rain_statement} {temperature_statement} {weather_context}. "
        f"{location_statement} {vibe_statement} {gender_statement} "
        "Give me a short and stylish outfit recommendation for the day. Return in JSON format, following the following format and structure: a top level 'outfit' object, with a 'top', 'bottom', 'outerwear', 'footwear', and 'accessories' with each having an 'item' that describes the item and 'description' with a concise but detailed description of the item. *FOR IMAGE GENERATION ONLY*: always use a white background, have the outfit items layed out individually with a headless model/mannequin posing and wearing the outfit"
    )

    # Make a request to OpenAI's API
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative fashion assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=.2,
        response_format={ "type": "json_object" }
    )

    # Generate an image based on the prompt and outfit recommendation
    response_image = openai.images.generate(
        model="dall-e-3",
        prompt=f"prompt:{prompt} and response: {response.choices[0].message.content}",
        size="1024x1024",
        quality="standard",
        n=1,
    )

    # Extract url from response
    image_url = response_image.data[0].url

    # Extract the assistant's message from the response
    outfit_recommendation = response.choices[0].message.content
    return outfit_recommendation, image_url

@app.route("/", methods=["GET", "POST"])
def home():

    # Define an example outfit
    example_outfit = json.loads('{"outfit": {"top": {"item": "Top", "description": "The main shirt of the outfit"}, "bottom": {"item": "Bottom", "description": "The main bottoms of the outfit"}, "outerwear": {"item": "Outerwear", "description": "Outerwear of the outfit"}, "footwear": {"item": "Footwear", "description": "Footwear of the outfit"}, "accessories": {"item": "Accessories", "description": "Any accessories for the outfit."} } }')

    form = CustomizeForm()
    save_outfit_form = SaveOutfitForm()

    outfit_json = None
    image_url = None

    if "user_id" in session:

        user = User.query.get_or_404(session["user_id"])

        outfits = user.outfits
        saved_outfits = []

        for outfit in outfits:
            fit_json = json.loads(outfit.outfit_desc)
            saved_outfits.append(fit_json)

        # print(saved_outfits)

        # Handle form submission
        if form.validate_on_submit():

            # Get input data from form
            location = form.location.data
            vibe = form.vibe.data
            gender = form.gender.data

            # Extract data from response
            forecast_res = requests.get(f"{BASE_URL}/forecast.json", params={"key": API_KEY, "q": location})
            forecast_data = forecast_res.json()
                    
            # Set variables from response data
            temperature = forecast_data["current"]["temp_f"]
            city_name = forecast_data["location"]["name"]
            icon_url = forecast_data["current"]["condition"]["icon"]
            rain_chance = forecast_data["forecast"]["forecastday"][0]["day"]["daily_chance_of_rain"]
            humidity = forecast_data["current"]["humidity"]
            wind_speed = forecast_data["current"]["wind_mph"]
            region = forecast_data["location"]["region"]
            country = forecast_data["location"]["country"]

            # Get image and outfit recommendation in JSON format
            outfit_recommendation, image_url = get_outfit_recommendation(location, vibe, gender, forecast_data["forecast"]["forecastday"][0]["day"]["daily_will_it_rain"], forecast_data["current"]["temp_f"], forecast_data["current"]["condition"]["text"])
            outfit_json = json.loads(outfit_recommendation)

            return render_template("index.html", saved_outfits=saved_outfits, outfit_recommendation=outfit_recommendation, form=form, save_outfit_form=save_outfit_form, image_url=image_url, region=region, country=country, wind_speed=wind_speed, humidity=humidity, temperature=temperature, city_name=city_name, icon_url=icon_url, rain_chance=rain_chance, outfit=outfit_json, show_save_form=True)
        
    return render_template("index.html", form=form, save_outfit_form=save_outfit_form, outfit=example_outfit, region="Somewhere", country="USA", wind_speed=0, humidity=0, temperature=0, city_name="Somewhere", rain_chance=0, icon_url="https://cdn.weatherapi.com/weather/64x64/day/113.png", show_save_form=False)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Registration route

    if "user_id" in session:
        return redirect("/")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        # Validate the password
        password_validation_error = validate_password(pwd)
        if password_validation_error:
            form.password.errors = [password_validation_error]
            return render_template("register.html", form=form)

        # Proceed with registration if the password is valid
        user = User.register(username, pwd)
        try:
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            form.username.errors = ["Username already taken!"]
            return render_template("register.html", form=form)
    
    return render_template("register.html", form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    # login

    if "user_id" in session:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.authenticate(username, pwd)

        if user:
            session["user_id"] = user.id
            return redirect("/")
        
        else:
            form.username.errors = ["Incorrect username/password"]

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    if "user_id" in session:
        session.pop('user_id')
        return redirect("/")
    
    return redirect("/")

@app.route("/users/<int:user_id>/save-outfit", methods=["POST"])
def outfits_add(user_id):

    form = SaveOutfitForm()

    if "user_id" in session and session["user_id"] == user_id:
        user = User.query.get_or_404(user_id)
        
        outfit_data = request.form.get("outfit_data")
        image_url = request.form.get("image_url")

        outfit = Outfit(user_id=user.id,
                        name=form.name.data,
                        outfit_desc=outfit_data,
                        image_url = image_url)
        
        try:
            db.session.add(outfit)
            db.session.commit()
            flash("Outfit saved successfully!", "success")
            print(outfit_data)
        except Exception as e:
            db.session.rollback()
            flash("Error saving outfit. Please try again.", "danger")
            print(f"Error: {e}")

        return redirect("/")
    
    return redirect("/")
