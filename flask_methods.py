'''
Methods for connecting with flask server

author: Jay White
'''

import flask
import urllib.parse
import random
import re
import requests as req
import server_api
from google.oauth2 import id_token
from google.auth.transport import requests
import string

#from temp_pred import main as predict

#-----------------------------------------------------------------------

app = flask.Flask(__name__)

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    '''initial index page'''
    html_code = flask.render_template("index.html")
    response = flask.make_response(html_code)
    return response

@app.route('/auth', methods=['POST'])
def auth():
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        #token = flask.request.get_data().decode('utf-8').split("&")[0].split("=")[1]
        credential = urllib.parse.parse_qs(flask.request.get_data().decode('utf-8'))
        token = dict(credential).get('credential')[0]
        #print(token)
        id_info = id_token.verify_oauth2_token(token, requests.Request(), '492185340356-n66a7tlk0efi4ccds9pbfmo77rs5mjdq.apps.googleusercontent.com')
        #print("THERE")
        # ID token is valid. Get the user's Google Account ID from the decoded token.
        user_id = str(id_info['sub'])
        email = id_info['email']
        name = id_info['name']

        args_dict = {}

        args_dict['email'] = email
        args_dict['user_id'] = user_id
        args_dict['institution'] = ""
        args_dict['postition'] = ""
        args_dict['name'] = name
        args_dict['ip_address'] = ""

        if server_api.confirm_user(user_id):
            pass
        else:
            server_api.add_account(args_dict)
        
        return flask.redirect(flask.url_for("account", user_id=user_id))

    except ValueError:
        # Invalid token
        pass

@app.route('/account/<user_id>', methods=['GET', 'POST'])
def account(user_id):
    '''account landing page'''

        # text_array of dicts where each dict is a row of a text query
        # Each row/dict has keys: "text_id", "user_id", "text_name", "uploaded" (text), "save_time"
    if server_api.confirm_user(user_id):
        text_array = server_api.get_text(user_id)
    else:
        text_array= []
    # if (text_array == None):
    #     text_array = []
    # text_array = []
    
    user_id = flask.request.path.split("/")[2]
    user_array = server_api.get_user(user_id)
    user_first_name = user_array["name"].split(" ")[0]
    #text_array = temporary_saved_projects()
    html_code = flask.render_template("account.html", user_id=user_id, text_array=text_array, user_first_name=user_first_name)

    response = flask.make_response(html_code)

    return response

#-----------------------------------------------------------------------
# Temporary methods for local testing without the model being hosted
#-----------------------------------------------------------------------
greek_words = ["μῆνιν", "ἄειδε", "θεὰ", "Πηληϊάδεω", "Ἀχιλῆοςοὐλομένην", "ἣ", "μυρί᾽", "Ἀχαιοῖς", "ἄλγε᾽", "ἔθηκεπολλὰς", "δ᾽", "ἰφθίμους", "ψυχὰς", "Ἄϊδι", "προΐαψενἡρώων", "αὐτοὺς", "δὲ", "ἑλώρια", "τεῦχε", "κύνεσσινοἰωνοῖσί", "τε", "πᾶσι", "Διὸς", "δ᾽", "ἐτελείετο", "βουλήἐξ", "οὗ", "δὴ", "τὰ", "πρῶτα", "διαστήτην", "ἐρίσαντεἈτρεΐδης", "τε", "ἄναξ", "ἀνδρῶν", "καὶ", "δῖος", "Ἀχιλλεύςτίς", "τ᾽", "ἄρ", "σφωε", "θεῶν", "ἔριδι", "ξυνέηκε", "μάχεσθαιΛητοῦς", "καὶ", "Διὸς", "υἱός:", "ὃ", "γὰρ", "βασιλῆϊ", "χολωθεὶςνοῦσον", "ἀνὰ", "στρατὸν", "ὄρσε", "κακήν", "ὀλέκοντο", "δὲ", "λαοίοὕνεκα", "τὸν", "Χρύσην", "ἠτίμασεν", "ἀρητῆραἈτρεΐδης:", "ὃ", "γὰρ", "ἦλθε", "θοὰς", "ἐπὶ", "νῆας", "Ἀχαιῶνλυσόμενός", "τε", "θύγατρα", "φέρων", "τ᾽", "ἀπερείσι᾽", "ἄποιναστέμματ᾽", "ἔχων", "ἐν", "χερσὶν", "ἑκηβόλου", "Ἀπόλλωνοςχρυσέῳ", "ἀνὰ", "σκήπτρῳ", "καὶ", "λίσσετο", "πάντας", "ἈχαιούςἈτρεΐδα", "δὲ", "μάλιστα", "δύω", "κοσμήτορε", "λαῶν:Ἀτρεΐδαι", "τε", "καὶ", "ἄλλοι", "ἐϋκνήμιδες", "Ἀχαιοίὑμῖν", "μὲν", "θεοὶ", "δοῖεν", "Ὀλύμπια", "δώματ᾽", "ἔχοντεςἐκπέρσαι", "Πριάμοιο", "πόλιν", "εὖ", "δ᾽", "οἴκαδ᾽", "ἱκέσθαι:παῖδα", "δ᾽", "ἐμοὶ", "λύσαιτε", "φίλην", "τὰ", "δ᾽", "ἄποινα", "δέχεσθαιἁζόμενοι", "Διὸς", "υἱὸν", "ἑκηβόλον", "Ἀπόλλωναἔνθ᾽", "ἄλλοι", "μὲν", "πάντες", "ἐπευφήμησαν", "Ἀχαιοὶαἰδεῖσθαί", "θ᾽", "ἱερῆα", "καὶ", "ἀγλαὰ", "δέχθαι", "ἄποινα:ἀλλ᾽", "οὐκ", "Ἀτρεΐδῃ", "Ἀγαμέμνονι", "ἥνδανε", "θυμῷἀλλὰ", "κακῶς", "ἀφίει", "κρατερὸν", "δ᾽", "ἐπὶ", "μῦθον", "ἔτελλε:μή", "σε", "γέρον", "κοίλῃσιν", "ἐγὼ", "παρὰ", "νηυσὶ", "κιχείωἢ", "νῦν", "δηθύνοντ᾽", "ἢ", "ὕστερον", "αὖτις", "ἰόνταμή", "νύ", "τοι", "οὐ", "χραίσμῃ", "σκῆπτρον", "καὶ", "στέμμα", "θεοῖο:τὴν", "δ᾽", "ἐγὼ", "οὐ", "λύσω:", "πρίν", "μιν", "καὶ", "γῆρας", "ἔπεισινἡμετέρῳ", "ἐνὶ", "οἴκῳ", "ἐν", "Ἄργεϊ", "τηλόθι", "πάτρηςἱστὸν", "ἐποιχομένην", "καὶ", "ἐμὸν", "λέχος", "ἀντιόωσαν:ἀλλ᾽", "ἴθι", "μή", "μ᾽", "ἐρέθιζε", "σαώτερος", "ὥς", "κε", "νέηαι"]
def temporary_prediction(text: str, parameters: dict):
    num_predictions = random.randrange(3, 20)
    output = []
    cum_prob  = 0
    for i in range(num_predictions):
        prob = random.uniform(0, 1 - cum_prob)
        if (round(prob, 5) < 0.00009):
            continue
        temp = []
        word1 = greek_words[random.randrange(0, len(greek_words))]
        word2 = greek_words[random.randrange(0, len(greek_words))]
        temp.append(word1)
        temp.append(word2)
        ret = [temp]
        ret.append(round(prob * 100, 2))
        output.append(ret)
        cum_prob += prob
    output.sort(key= lambda x: -x[1])
    return output

def temporary_saved_projects():
    projects = []
    for i in range(10):
        temp = {}
        temp['user_id'] = 1
        temp['text_name'] = 'test'
        temp['text_id'] = 1
        projects.append(temp)
    return projects

#-----------------------------------------------------------------------
@app.route('/project/<user_id>/<text_id>', methods=['GET'])
def project(user_id, text_id):
    '''Page containing main project interface'''
    text_name=""
    uploaded = ""
    prediction_array = []
    if text_id != "newProject":
        texts = server_api.get_text(user_id)
        for row in texts:
            if str(row.get("text_id")) == str(text_id):
                text_name = row.get("text_name")
                uploaded = row.get("uploaded")
                uploaded = urllib.parse.unquote(uploaded)
                uploaded = urllib.parse.unquote_plus(uploaded)

        # prediction_array of returns arrays of dicts where each dict is a row of prediction query
        # Each row/dict has keys: "textid", "prediction_name", "token_number", "prediction_output" (text)
        prediction_array = server_api.get_predictions(text_id=text_id)
        print("ARRAY:", prediction_array)
        #prediction_array = [{'prediction_name': 'Ajax', 'prediction': 'Αἴας'}]

    html_code = flask.render_template("project.html", text_name=text_name, uploaded=uploaded,
                                      prediction_array=prediction_array, user_id = user_id)
    response = flask.make_response(html_code)

    return response

@app.route('/predict', methods=['POST'])
def predict():
    data = urllib.parse.unquote(flask.request.get_data())
    data = urllib.parse.unquote_plus(data)
    data = urllib.parse.parse_qs(data)
    text = data['text'][0]
    prefix = data.get('prefix', "")
    if (prefix != ""):
        prefix = prefix[0]
    suffix = data.get('suffix', "")
    if (suffix != ""):
        suffix = suffix[0]
    num_tokens = data.get('num_tokens', 2)
    text = text.replace("-\n", "")
    text = re.sub(r'\s+', ' ', text)
    temp = req.post('https://classics-prediction-xkmqmbb5uq-uc.a.run.app', json={'text': text, 'prefix': "", 'suffix': "", 'num_pred': 7})
    #print("TEMP:", temp.json())
    #ret = temporary_prediction(text, num_tokens)
    temp = temp.json()
    for pred in temp:
        temp_string = ''
        for i in pred[0]:
            if '##' in i:
                temp_string = temp_string[:-1]
                temp_string += i.replace('##', '')
                temp_string += ' '
            elif i == '.':
                temp_string = temp_string[:-1]
                temp_string += '.'
                temp_string += ' '
            elif i == '-':
                temp_string = temp_string[:-1]
                temp_string += '-'
            elif i == ',':
                temp_string = temp_string[:-1]
                temp_string += ','
                temp_string += ' '
            else:
                temp_string += i
                temp_string += ' '
        pred[0] = temp_string
    template = flask.render_template("prediction.html", predictions=temp)
    response = flask.make_response(template)
    print("HERE")
    return response

@app.route('/saveProject', methods=['POST'])
def save_project():
    data = urllib.parse.unquote(flask.request.get_data().decode('utf-8'))
    data = urllib.parse.unquote_plus(data)
    data = urllib.parse.parse_qs(data)
    text_name = data['text_name'][0]
    user_id = data['user_id'][0]
    is_new = data.get("new", "false")
    if (is_new != "false"):
        print("HI")
        text = data['text'][0]
        text = urllib.parse.quote(text)
        time = data['time'][0]
        server_api.upload_text(text, text_name, user_id, time)
        text_id = server_api.get_text_id(user_id, text_name)
        return str(text_id)


    # checking if text_name already exists in the database
    if not server_api.confirm_text(text_name, user_id):
        text = data['text'][0]
        text = urllib.parse.quote(text)
        time = data['time'][0]
        server_api.upload_text(text, text_name, user_id, time)
        return ""
    else:
        dict = {}
        if data.get("text"):
            temp_text = urllib.parse.quote(data.get('text')[0])
            dict['uploaded'] = temp_text
        if data.get("text_name"):
            dict['text_name'] = data.get("text_name")[0]
        if data.get("time"):
            dict['save_time'] = data.get("time")[0]
        text_id = 0
        for row in server_api.get_text(data['user_id'][0]):
            if row['text_name'] == data['text_name'][0]:
                text_id = row['text_id']
        server_api.update_text(dict, text_id)
        return ""

@app.route('/savePrediction', methods=['POST'])
def save_prediction():
    data = urllib.parse.unquote(flask.request.get_data().decode('utf-8'))
    data = urllib.parse.unquote_plus(data)
    data = urllib.parse.parse_qs(data)
    prediction_name = data['prediction_name'][0]
    text_id = data['text_id'][0]
    
    # checking if prediction_name already exists in the database
    if server_api.confirm_prediction(prediction_name, text_id):
        update_dict = {}
        if data.get("prediction"):
            update_dict['prediction'] = data.get("prediction")[0]
        if data.get("text_id"):
            update_dict['text_id'] = data.get("text_id")[0]
        if data.get("token_number"):
            update_dict['token_number'] = data.get("token_number")[0]
        if data.get("save_time"):
            update_dict['save_time'] = data.get('save_time')[0]
        if data.get("prediction_blob"):
            prediction_blob = bytes(data.get("prediction_blob")[0], 'utf-8')
            update_dict['prediction_blob'] = prediction_blob
        print("BLOB:", prediction_blob)

        prediction_id = 0
        for row in server_api.get_predictions(data['text_id'][0]):
            if row['prediction_name'] == data['prediction_name'][0]:
                prediction_id = row['prediction_id']

        server_api.update_text(update_dict, prediction_id)
        if (data.get('redirect', 'false') != 'false'):
            print("URL--------------------------------------")
            print(flask.url_for('project', user_id = data['user_id'][0], text_id= text_id))
            print("------------------------------------------")
            return flask.url_for('project', user_id = data['user_id'][0], text_id= text_id)
        else:
            print("WHY HERE AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaa")
            return flask.make_response(flask.render_template('saved-predictions.html', prediction_array=server_api.get_predictions(text_id)))
    else:
        prediction = data['prediction'][0]
        token_number = data['token_number'][0]
        save_time = data['save_time'][0]
        prediction_blob = bytes(data['prediction_blob'][0], 'utf-8')
        
        server_api.upload_prediction(prediction, text_id, token_number, prediction_name,
                      save_time, prediction_blob)
        if (data.get('redirect', 'false') != 'false'):
            print("URL--------------------------------------")
            print(flask.url_for('project', user_id = data['user_id'][0], text_id= text_id))
            print("------------------------------------------")
            return flask.url_for('project', user_id = data['user_id'][0], text_id= text_id)
        else:
            print("WHY HERE AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaa")
            return flask.make_response(flask.render_template('saved-predictions.html', prediction_array=server_api.get_predictions(text_id)))
        # return flask.make_response(flask.render_template('saved-predictions.html', prediction_array=server_api.get_predictions(text_id)))

@app.route('/register/<user_id>', methods=['POST'])
def register_user(user_id):
    args_dict = {}
    # decodes instituion and position
    data = urllib.parse.unquote(flask.request.get_data().decode('utf-8'))
    data = urllib.parse.unquote_plus(data)
    data = urllib.parse.parse_qs(data)
    institution = data['institution'][0]
    position = data['position'][0]
    args_dict['institution'] = institution if institution else ""
    args_dict['postition'] = position if position else ""
    server_api.update_account(parameter_to_update=args_dict, userid=user_id)
    return flask.redirect(flask.url_for("account", userid=user_id))

@app.route('/deleteProject', methods=['POST'])
def delete_project():
    data = urllib.parse.unquote(flask.request.get_data().decode('utf-8'))
    data = urllib.parse.unquote_plus(data)
    data = urllib.parse.parse_qs(data)
    text_name = data['text_name'][0]
    user_id = data['user_id'][0]
    server_api.delete_text(text_name=text_name, user_id=user_id)
    return ""