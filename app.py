import numpy as np
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyrebase
from keras.models import load_model
import pickle
import binascii
from datetime import datetime
import datetime
import json
from functools import wraps
import re
import os
from dotenv import load_dotenv
import openai
from helper.openai_api import text_complition
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from django.conf import settings
# from django.conf.urls.static import static

# if settings.DEBUG:
#   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
app = Flask(__name__)
app.secret_key = '1234'


openai.api_key = "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"
'''config = {
    "apiKey": os.getenv("apiKey"),
    "authDomain": os.getenv("authDomain"),
    "databaseURL": os.getenv("databaseURL"),
    "projectId": os.getenv("projectId"),
    "storageBucket": os.getenv("storageBucket"),
    "messagingSenderId": os.getenv("messagingSenderId"),
    "appId": os.getenv("appId"),
    "measurementId": os.getenv("measurementId")
}'''
config = {
    "apiKey": "AIzaSyAvYvSqBoQzCUDK2oloq79JhPJGTw1DIUk",
    "authDomain": "dashboard-50078.firebaseapp.com",
    "databaseURL": "https://dashboard-50078-default-rtdb.firebaseio.com",
    "projectId": "dashboard-50078",
    "storageBucket": "dashboard-50078.appspot.com",
    "messagingSenderId": "475329238769",
    "appId": "1:475329238769:web:7ccdb82a47b7c06ea27b50",
    "measurementId": "G-L0PKH3JBR3",
}


class Diary(FlaskForm):
    title = StringField('Title', validators=[
                        DataRequired(), Length(min=3, max=200)])
    note = StringField('Note',
                       validators=[DataRequired(), Length(min=3, max=2000)], widget=TextArea())
    submit = SubmitField('Submit')


firebase = pyrebase.initialize_app(config)
db = firebase.database()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

########################


@app.route("/login")
def loginn():
    return render_template("login.html")


@app.route("/log", methods=["GET", "POST"])
def login():
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["user"] = re.search(
                r"'idToken': '(.*?)'", str(user)).group(1)
            print(session["user"])
            # Extracting the email using regular expression
            email = re.search(r"'email': '(.*?)'", str(user)).group(1)
            print("this is the email after login : ", email)
            session["email"] = email
            print("this is the session email : ", session["email"])
            return render_template('index.html', username=email, login=True)
        except:
            error = "Invalid credentials. Please try again."
            print(error)
            return render_template("login.html", error=error)


@app.route("/register")
def registerr():
    return render_template("register.html")


@app.route('/diary', methods=["POST", "GET"])
def diary():
    username = "shahrukh"
    forms = Diary()
    if forms.validate_on_submit():
        title = forms.title.data
        note = forms.note.data
        # Replace with the actual username
        entry_key = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Store the entry in Firebase Realtime Database
        db.child("Diary").child(username).push(
            {"title": title, "note": note, "date": date})

        flash('Successfully inserted your note!', 'success')
        return redirect(url_for('diary'))

    # Retrieve diary entries from Firebase
    diary_data = db.child("Diary").child(username).get().val()

    # Convert the diary_data dictionary into a list of entries
    entries = []
    if diary_data:
        for entry_key, entry_value in diary_data.items():
            if "date" in entry_value:
                entry = {"key": entry_key, "title": entry_value["title"], "note": entry_value["note"],
                         "date": entry_value["date"]}
                entries.append(entry)

    return render_template('diary.html', form=forms, entries=entries)


@app.route("/regis", methods=["GET", "POST"])
def register():
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user["idToken"])
            idToken = re.search(r"'idToken': '(.*?)'", str(user)).group(1)
            session["user"] = idToken
            session["email"] = re.search(
                r"'email': '(.*?)'", str(user)).group(1)
            return redirect("/")
        except Exception as e:
            error = "Registration failed. Error: " + str(e)
            print(error)
            return render_template("register.html", error=error)
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("email", None)
    return redirect("/")


########################


@app.route("/")
@app.route("/home")
def home():
    if "user" in session:
        username = session["email"]
        return render_template('index.html', title='Guide to Mental WellBeing', username=username, login=True)
    else:
        username = None
        return render_template('index.html', title='Guide to Mental WellBeing', username=username, login=False)


@app.route("/exercise")
def exercise():
    return render_template('exercise.html', title='Exercises to improve you mental health')


@app.route('/therapy')
def therapy():
    return render_template('bot.html')


@app.route('/map')
def map():
    return render_template('map.html')


messages = [
    {"role": "system", "content": "You are a kind helpful assistant for assisting people for mental fitnesss and mental health."},
]


@app.route('/runbook', methods=['POST'])
def runbook():
    message = request.form['message']
    command = message
    if 'play' in command:
        words_to_replace = ["play", "music",
                            'song', 'play the song', 'hello', 'hi']
        for word in words_to_replace:
            command = command.replace(word, "")
        response_message = "ok,playing the song for you on youtube"
#         pywhatkit.playonyt(command)
        return jsonify(response_message)

    elif 'time' in command:
        now = datetime.datetime.now()
        day_name = now.strftime("%A")
        day_num = now.strftime("%d")
        month = now.strftime("%B")
        hour = now.strftime("%H")
        minute = now.strftime("%M")
        response_message = "Today is " + day_name + " " + day_num + \
            " " + month + " and the time is " + hour + ":" + minute
        return jsonify(response_message)

    elif 'quit' in command or "end" in command:
        response_message = "Thankyou"
        return jsonify(response_message)

    else:
        message = command
        if message:
            try:
                if len(message.split()) > 80:
                    raise ValueError(
                        "Input contains more than 45 words. Please try again.")
                messages.append({"role": "user", "content": message})
                chat = openai.Completion.create(
                    model="text-davinci-002", prompt=f"{messages[-1]['content']} Assistant: ", max_tokens=1024
                )
            except ValueError as e:
                print(f"Error: {e}")
        reply = chat.choices[0].text
        response_message = f"{reply}"
        messages.append({"role": "assistant", "content": reply})
        return jsonify(response_message)


@app.route('/dialogflow/es/receiveMessage', methods=['POST'])
def esReceiveMessage():
    try:
        data = request.get_json()
        query_text = data['queryResult']['queryText']

        result = text_complition(query_text)

        if result['status'] == 1:
            return jsonify(
                {
                    'fulfillmentText': result['response']
                }
            )
    except:
        pass
    return jsonify(
        {
            'fulfillmentText': 'Something went wrong.'
        }
    )


@app.route('/dialogflow/cx/receiveMessage', methods=['POST'])
def cxReceiveMessage():
    try:
        data = request.get_json()
        query_text = data['text']

        result = text_complition(query_text)

        if result['status'] == 1:
            return jsonify(
                {
                    'fulfillment_response': {
                        'messages': [
                            {
                                'text': {
                                    'text': [result['response']],
                                    'redactedText': [result['response']]
                                },
                                'responseType': 'HANDLER_PROMPT',
                                'source': 'VIRTUAL_AGENT'
                            }
                        ]
                    }
                }
            )
    except:
        pass
    return jsonify(
        {
            'fulfillment_response': {
                'messages': [
                    {
                        'text': {
                            'text': ['Something went wrong.'],
                            'redactedText': ['Something went wrong.']
                        },
                        'responseType': 'HANDLER_PROMPT',
                        'source': 'VIRTUAL_AGENT'
                    }
                ]
            }
        }
    )


@app.route('/user_dashboard')
def user_dashboard():
    # if not session.get("user_id"):
    #     flash("you must be logged in", "error")
    #     return redirect(url_for("login"))
    return render_template('user_dashboard.html')


@app.route('/diet')
def diet():
    # if not session.get("user_id"):
    #     flash("you must be logged in", "error")
    #     return redirect(url_for("login"))
    return render_template('diet.html')


# Load the Keras model
model = load_model('best_symptom_model.h5')
diseases_names = pickle.load(open('diseases_names.pkl', 'rb'))


@app.route('/predict1', methods=['POST'])
def predict():
    print(request.get_json())
    symptoms = request.get_json()['symptoms']
    symp = np.zeros(489, dtype=int)
    for i in symptoms:
        symp[i] = 1
    symptoms_arr = symp.reshape(1, -1)
    probabilities = model.predict(symptoms_arr)
    predicted_class = np.argmax(probabilities, axis=-1)
    predicted_class = predicted_class.reshape(-1, 1)
    disease = diseases_names[predicted_class[0][0]]
    # predicted_class=predicted_class.tolist()

    print(disease)
    message = "you are a helpful doctor to help the patients in their mental fitness journey, tell the treatments, causes of the desease : " + \
        disease + " along with safety measures , also tell some jokes to relax the user and tell the user not to worry and just be happy and relax"
    if message:
        try:
            if len(message.split()) > 80:
                raise ValueError(
                    "Input contains more than 45 words. Please try again.")
            chat = openai.Completion.create(
                engine="text-davinci-003", prompt=message, max_tokens=3896, temperature=0.2)
        except ValueError as e:
            print(f"Error: {e}")
    reply = chat.choices[0].text
    response_message = f"{reply}"
    print(response_message)
    response_data = {"disease": disease, "message": response_message}
    return jsonify(response_data)


@app.route('/serious', methods=['POST', "GET"])
def serious():
    return render_template("serious.html")


@app.route('/comedy', methods=['POST', "GET"])
def comedy():
    return render_template("comedy.html")


@app.route('/community', methods=["POST", "GET"])
def community():

    if request.method == "POST":
        section = request.form['section']
        messages = get_section_messages(section)
        return jsonify(messages=messages)
    else:
        sections = ['discussion_forum', 'creative_corner',
                    'wellness_tips', 'selfcare_challenges', 'inspiration_corner']
        return render_template('home.html', sections=sections)


def get_section_messages(section):
    messages = db.child(section).get().val()
    message_list = list(messages.values()) if messages else []
    return message_list


@app.route('/section', methods=["POST", "GET"])
def section():

    if request.method == "POST":
        section = request.args.get('section')
        username = 'sharukhali'
        message = request.form['message']
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.child(section).push({
            "username": username,
            "message": message,
            "timestamp": timestamp
        })
        messages = get_section_messages(section)
        return jsonify(messages=messages)
    else:
        section = request.args.get('section')
        messages = get_section_messages(section)
        return jsonify(messages=messages)


if __name__ == '__main__':
    app.run(debug=True)
