# GestureType (Hackathon Prototype)

This is a **real-time, hands-free communication tool** designed for individuals with mobility challenges.  
Built during a hackathon, this project enables a user to **select words using head tilts** and **send messages using mouth movement** — all powered by a webcam.

---

## Features

- **Head-controlled word selection**  
  - Tilt **right** → Select left word  
  - Tilt **left** → Select right word  
  - **Bow** head → Select center word

- **Next word prediction** using [Groq's LLM API]  
  - Suggests 3 words every 7 seconds based on the sentence being built.

- **Mouth opening triggers message send**  
  - Automatically sends the built sentence via email when mouth opens.

- **Email integration** with Gmail using environment variables.

- **MediaPipe + OpenCV for face and mouth tracking**

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/InsaneJSK/GestureType.git
cd GestureType
```

### 2. Set up Python environment (optional)

```bash
python -m venv .venv
.venv\Scripts\activate # or source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Create .env file

Create a .env file in the project root, same as the .env.dist file:

```bash
groq_api_key=your_groq_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=Services_account_email_password
```

Important note, this is the sender email and not reciever, to edit reciever email, change the "RECIPIENT_EMAIL" variable in app.py

## 🚀 Running the App

```bash
python app.py
```

- A webcam window will open.
- 3 predicted words will be shown at the bottom.
- Use head gestures to build your sentence.
- Mouth opening will send the message to a predefined email.

## 📁 File Overview

| File                 | Description                                      |
| -------------------- | ------------------------------------------------ |
| `app.py`             | Main script (MediaPipe + Groq + OpenCV)          |
| `default_prompt.txt` | Prompt sent to LLM for context-based predictions |
| `.env`               | Store your private keys (excluded from Git)      |
| `.env.dist`          | Template for the private keys                    |
| `requirements.txt`   | Python dependencies                              |

## 📌 Limitations & TODOs

- Word cycling UI needs visual polish
- Current email recipient is hardcoded
- No error feedback to user if email sending fails
- LLM output depends on consistent formatting of default prompt

## 💡 Why This Matters

This was built during a 24-hour hackathon, inspired by the goal to help users with limited physical mobility communicate using minimal gestures.

## 📜 License

MIT — use it freely, modify it, and build on top of it.

## 🙋‍♂️ Author

Jaspreet Singh: [Linkedin](https://www.linkedin.com/in/jaspreet-singh-jsk/)
