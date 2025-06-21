![logo](https://github.com/user-attachments/assets/eaca9fab-44c9-42f6-aaa8-491db4724966)

# Description
Effortless article saving, smart categorization, and reading progress tracking — directly from your Telegram.

<img src="https://github.com/user-attachments/assets/8f5559b6-6a89-4480-b772-e8eb07c4317e" width="900"/>


# Motivation
Like many others, I often come across insightful articles I want to read later. Initially, I saved these links to Telegram Saved Messages, but as the list grew, I lost track of what I had saved, what I had read, and what still needed attention.

I tried apps like GoodLinks, which let you organize and tag articles manually — but this added friction. I wanted a workflow that felt natural and invisible.

That's why I built MessageMind.


# How It Works

https://github.com/user-attachments/assets/3844f958-b81d-4ce2-a250-06d2807cc046



### 1. Save as Usual
When I find an interesting article, I save it to my Telegram Saved Messages — no need to change habits.

<img src="https://github.com/user-attachments/assets/0761f914-9de8-47b4-8f25-c96f39e60569" width="100"/>

### 2. Automated CI Pipeline (GitHub Actions)
Every hour, a GitHub Actions workflow runs. 
- It fetches new messages from Telegram Saved Messages using the Telegram API.
- New article links are stored in a MongoDB database.

<img src="https://github.com/user-attachments/assets/08488b43-212a-435f-82c7-82fb4934c7a3" width="100"/>

### 3. LangGraph + LLM Magic
For each new article, a LangGraph workflow is triggered.

The article is:
- Summarized
- Categorized using an LLM

These metadata are also stored in MongoDB.

<img src="https://github.com/user-attachments/assets/36f5e021-c3ec-4c1a-a53b-543f4f216bcb" width="200"/>

<img src="https://github.com/user-attachments/assets/1f5af40e-0f5a-4505-a736-18304b612128" width="200"/>


### 4. Reading Dashboard (Next.js Frontend)
Built with React + Next.js.

Connects to the MongoDB to display:
- A list of all saved articles
- Read vs unread status
- Summaries and tags
- Progress tracking (e.g., how many articles you've read vs what's pending)

The frontend repo is located in https://github.com/Joanna-Khek/message-mind-ui

<img src="https://github.com/user-attachments/assets/0dc8ed2b-6dbb-4446-8a2b-2e84e92e0b69" width="100"/>

<img src="https://github.com/user-attachments/assets/e61b0689-5547-4b7f-863b-7d199083f0b2" width="100"/>

### 5. Telegram Notification
Everytime a message gets successfully saved in the database, I'll be notified by a telegram notification via a Bot.
Information such as the saved article, category, summary and the LLM cost are provided in the details.

<img src="https://github.com/user-attachments/assets/acfe34cb-3978-4b59-9088-236876df2f06" width="500"/>


# Features
- Ability to edit the content in case the category or summary is incorrect
- Continuous refinement to the prediction of categories


# Tech Stack
| Layer  | Technology |
| ------------- | ------------- |
| Messaging  | Telegram Bot API  |
| Backend Jobs  | Github Actions CI/CD  |
| Processing  | LangGraph + LLM (OpenAI)  |
| Database  | MongoDB Atlas  |
| Frontend  | React + NextJS  |
