# AI Cold Email Generator

A Streamlit app that scrapes a potential client's website or project brief, uses Groq to draft a personalized freelance pitch, and can send the reviewed email through Gmail OAuth.

## How the pipeline works

`app.py` is the entry point:

1. `scraper.scrape_website(target_url)` fetches the URL and returns `ScrapedData` containing the final URL, visible page text, title, description, and headings.
2. `app.py` combines that data with the freelancer's details, client or company name, and freelance service.
3. `llm.generate_cold_email(...)` sends the combined context to Groq and returns the generated email.
4. After the user reviews or edits the email, `gmail.send_email(...)` authenticates with Google and sends it through the Gmail API.

The client name and freelance service are explicit user inputs. Website scraping supplies real page context, but generic websites do not expose reliable project requirements or client contact details, so the app does not silently guess those values.

Each stage stops with a user-visible error when it fails: fetch/parse errors stop before the LLM call, Groq errors prevent an email from being displayed, and Gmail errors return a failure message instead of claiming delivery.

## Requirements

- Python 3.10 or newer
- A Groq API key
- A Google Cloud OAuth desktop-app credential
- A Gmail account with Gmail API access

## Setup

From this project directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env`, `credentials.json`, or `token.json`; they are ignored by `.gitignore`.

## Groq API setup

1. Create an account at [Groq Console](https://console.groq.com/).
2. Create an API key.
3. Put it in `.env` as `GROQ_API_KEY=...`.
4. The app currently uses the `llama-3.3-70b-versatile` model.

## Gmail OAuth setup

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Enable **Gmail API** under **APIs & Services > Library**.
4. Configure the OAuth consent screen. For a personal project, `External` is usually appropriate. Add your Google account as a test user if the app is still in testing.
5. Under **APIs & Services > Credentials**, choose **Create credentials > OAuth client ID**.
6. Select **Desktop app**, download the JSON file, rename it to `credentials.json`, and place it beside `app.py`.
7. Keep the requested scope as `https://www.googleapis.com/auth/gmail.send`.

The first send opens a browser for consent. Google then writes `token.json` beside `app.py`; later sends reuse that token. Delete `token.json` if you revoke access or change the Gmail scope and need to authorize again.

## Run end-to-end

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

In the browser:

1. Enter freelancer background, skills, and services.
2. Enter the client or company name, freelance service, and a public company website or project brief URL.
3. Choose tone and length, then select **Generate Cold Email**.
4. Review and edit the generated message.
5. Enter the recipient and subject, then select **Send Email**.
6. Complete Gmail consent in the browser on the first send.

Use a public URL that allows automated requests. Some sites block scraping, require JavaScript, or disallow automated access; in that case the app reports a scraping failure and does not call the LLM.

## Troubleshooting

- `GROQ_API_KEY is not set`: check the `.env` filename and that Streamlit is running from this project directory.
- `credentials.json is missing`: place the downloaded desktop OAuth JSON beside `app.py`.
- Google `access_denied`: verify the account is an OAuth test user and that Gmail API is enabled.
- Scraping failures: try the client's public project brief or company page and confirm it loads without a login.
- Import errors: activate `.venv` and run `pip install -r requirements.txt` again.
