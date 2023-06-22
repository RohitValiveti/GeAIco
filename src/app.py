import os
import pythoncom
import openai
import win32com.client
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, session)
from askQuestion import process_question


app = Flask(__name__)
api_key = os.environ["AZUREOPENAPIKEY"]
openai.api_type = "azure"
openai.api_base = "https://geicohackopenai8.openai.azure.com/"
openai.api_version = "2022-12-01"
openai.api_key = api_key
app.secret_key = "super secret key"


@app.route("/")
def index():
    print("Request for index page received")
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )

@app.route("/search", methods=["GET","POST"])
def search():
    if request.method == "POST":
        question = request.form.get("question")
        answer = process_question(question)
        return render_template("search.html", question=question, answer=answer)
    return render_template("search.html")

# Outputs the form to figure out who to send to
@app.route('/draft', methods=["GET","POST"])
def draftEmail():
    return render_template("email_draft.html")


# Sends the email and shows the success page
@app.route('/send', methods=["GET","POST"])
def sendEmail():
    recipient = request.form["recipient"]
    # subject = request.form["subject"]
    context = request.form["body"]

    # Open AI request to draft email
    prompt = "Act as an associate in Geico's Claims department and draft a professional email using the context provided.\n"
    full_query = prompt + context
    answer = openai.Completion.create(
        engine= "hackgroup37textdavinci003",
        prompt=full_query,
        temperature=0.3,
        max_tokens=350,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    
    # Logic to capture information from response
    # Formats subject and body
    final_response = answer.choices[0].text
    response_array = final_response.split("\n", 4)
    subject = response_array[2].split(": ")[1]
    body = "".join(response_array[3:])
    draft_helper(recipient, subject, body)
    # return render_template("email_sent.html", recipient=recipient)
    return redirect(url_for("draftEmail"))
    
@app.route('/emails')
def get_emails():
    """
    View subject lines of 10 most recent emails.
    """
    num_emails = 10
    msgs = inbox_items()
    subject_lines = []

    count = 1
    for msg in msgs:
        subject_lines.append(msg.Subject)
        count+=1
        if count == num_emails+1:
            break

    return render_template('emails.html', subjs=subject_lines)

import textwrap

@app.route('/reply', methods=['POST'])
def compose_reply():
    """
    Compose a reply to the idx-th most recent email.
    Request should cointain "selected-email" corresponding to the index of the email.
    """
    pythoncom.CoInitialize()
    subject = request.form['subjectoption']
    tone = request.form['tone']
    msgs = inbox_items()
    subjects = [subject.Subject for subject in msgs]
    idx = subjects.index(subject)
    email = msgs[idx]
    body = email.Body
    #Efficiently trim body to 2500 characters
    trimmed_body = textwrap.shorten(body, width=2500, placeholder="...")

    prompt = f"You are a helpful insurance agent in the claims deperatment at GEICO. Draft a {tone} email response to the following email in html format: \n"
    
    prompt+= trimmed_body
    response = openai.Completion.create(
        engine= "hackgroup37textdavinci003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=1000, 
        top_p=1,
    )
    reply_text=response.choices[0].text

    try:        
        reply = email.Reply()
        reply.HTMLBody = reply_text + "</br></br>" + format_email_chain(email)
        reply.Display()

        # to emails
        return redirect(url_for("get_emails"))

    except Exception as e:
        return {"status":"error", "message": str(e)}, 500

@app.route('/chatSummary', methods = ['GET', 'POST'])
def chat_summary():
   if request.method == 'POST':
        try:
            chatUpload = request.files['file']
            uploadData = chatUpload.readline().decode()
            prompt = "You are a helpful insurance agent assistant in the claims deperatment at GEICO. Summarize a chat interaction between a GEICO chatbot and user using the context provided.\n"
            full_query = prompt + uploadData
            answer = openai.Completion.create(
                engine= "hackgroup37textdavinci003",
                prompt=full_query,
                temperature=0.3,
                max_tokens=350,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
            return render_template("chat_summary.html", summary=answer.choices[0].text)
        except Exception as e:
            return {"status":"error", "message": str(e)}, 500
   else:
        return render_template("chat_summary.html")

def inbox_items():
    """
    Returns an array of Outlook mail objects corresponding
    to the user's outlook. Sorted in most recent to least
    recent order. Only returns 10 most recent emails.
    """
    pythoncom.CoInitialize()

    outlook_app=win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook_app.GetDefaultFolder(6) #inbox

    msgs = inbox.Items
    msgs.Sort("[ReceivedTime]",True)
    return msgs

# Helper function to open Outlook and allow user to send the email through Outlook GUI
def draft_helper(recipient, subject, answer):
        pythoncom.CoInitialize()
        olMailItem = 0x0
        obj = win32com.client.Dispatch("Outlook.Application")
        newMail = obj.CreateItem(olMailItem)
        newMail.Subject = subject
        newMail.Body = answer
        newMail.To = recipient
        newMail.display(True)

def format_email_chain(email):
    email_chain = """
    <hr>
    <b>From:</b> {sender}<br>
    <b>Sent:</b> {sent}<br>
    <b>To:</b> {to}<br>
    <b>Subject:</b> {subject}<br>
    {body}""".format(sender=email.Sender, sent=email.SentOn, to=email.To, subject=email.Subject, body=email.HTMLBody )
    
    return email_chain

if __name__ == '__main__':
   app.run()