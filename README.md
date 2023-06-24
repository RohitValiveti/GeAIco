
# GeAIco (Geico AI Assistant)

GeAIco is a proof of concept **AI-Powered** assistant for Geico insurance agents. As part of Geico's OpenAI Hackathon, I, along with 5 developers, designed, developed, and presented GeAIco in a week. The goal of GeAIco and the hackathon was to develop an application that reduces time and energy insurance agents spent on common tasks, while maintaining the quality of human agents.

 ## Core Functionalities
- AI Powered Q&A: Answer agent questions
- Email Draft Assistance: Draft an email given the context of the email, the subject line, and the email recipient
- Email Reply Assistance: Generate a draft email response to current email in inbox
- Virtual Chat Summarization: Summarize a chat interaction between a virtual agent and client, given the chat transcript

## Development Process
Using Microsoft's Azure OpenAI service and Cognitive Search Service, we were able to integrate a GPT-3 model and semantic search into the backend of our application. Using Microsoft's API and Python SDK for the OpenAI/CogSearch services, we developed a Flask backend to perform the core functionalities as described above. We utilized a Completions GPT model for our OpenAI needs as the functionalities we developed required a single instance response, as opposed to a conversation-like experience. Utilizing prompt engineering, we customized the responses of the model to be in the context of a Geico insurance agent and provided enough context for each component of the app to generate an appropriate response (Email context & subject line, email to respond to, chat transcript).

For the UI, we used HTML and the Jinja library to display user input prompts and display responses. We also used the win32com library for Python to intrate our app with Microsoft Outlook, so that user emails could be read and so that we could open Outlook's email composition prompt directly from our app.

My individual contribution consisted of developing the Email Reply Assistant, the Virtual Chat Summarization, and refining the UI.


## Video Demonstration
(In Progess)

## Credits
* Liya (Senior Engineer)
* Yuvraj Sreepathi (Software Engineer I)
* Saahil (Software Engineer I)
* Nick Didio (Software Engineer I)
* Min Dong (Software Engineer I)

---

### Get Started
change folder
`cd src`

create environment
`py -m venv venv/geAIco-assistant`

Activate environment
`./venv/geAIco-assistant/Scripts/activate.ps1`


Install required dependencies
`pip install -r requirements.txt`

Run app
`flask run`