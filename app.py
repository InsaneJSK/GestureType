import os
import cv2
import mediapipe as mp
import numpy as np
import asyncio
import threading
import smtplib
from email.mime.text import MIMEText
from groq import Groq
import json
from dotenv import load_dotenv

load_dotenv()
# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

groq_api_key = os.getenv("groq_api_key")

# Initialize Groq API
client = Groq(api_key=groq_api_key)

# System Prompt for Groq API
system_prompt = "You are a helpful follow-up word generator which provides the next most relevant words."
with open("default_prompt.txt", "r") as f:
    default_prompt = f.read()
# Global Variables
context = ""  # Stores the sentence being built
word_list = ["I", "What", "We", "Hello", "Yes", "No", "Help", "Stop", "Go", "Thank", "Please", "Need", "Want"]
current_words = ["", "", ""]  # Words currently displayed
word_index = 0  # Keeps track of cycling words
selected_word = None  # Stores the last selected word
last_selected_word = None  # Stores the previously selected word
mouth_open = False  # Track mouth open state

# Email Configuration
SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = "jaspreet.jsk.kohli@gmail.com"  

def send_email():
    """Send an email when mouth is opened."""
    global context
    try:
        msg = MIMEText(f"New Message: {context}")
        msg["Subject"] = "New Communication Message"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)

def fetch_new_words():
    """Fetch new word suggestions from Groq API based on current context."""
    global word_list
    if not context.strip():  # If context is empty, use the default word list
        word_list = ["I", "What", "We", "Hello", "Yes", "No", "Help", "Stop", "Go", "Thank", "Please", "Need", "Want"]
        return

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""{default_prompt}
                                <Context Starts>
                                {context}
                                <Context Ends>
"""}
            ],
            model="llama3-8b-8192",
            stream=False,
            response_format={"type": "json_object"},
        )
        response = chat_completion.choices[0].message.content
        data = json.loads(response)
        word_list = data.get("options", word_list)  # Default if API fails
        print(word_list)
    except Exception as e:
        print("Error fetching words:", e)

# Async function to cycle words every 7 seconds
async def cycle_words():
    """Cycle through word choices every 7 seconds."""
    global word_index, current_words
    while True:
        current_words = word_list[word_index: word_index + 3]
        if len(current_words) < 3:
            current_words += word_list[: 3 - len(current_words)]  # Wrap around
        word_index = (word_index + 3) % len(word_list)  # Move index forward
        await asyncio.sleep(7)  # Wait for 7 seconds

# Start async loop in a separate thread
def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cycle_words())

threading.Thread(target=start_async_loop, daemon=True).start()

# OpenCV Video Processing
def process_video():
    """Process video stream and detect head tilts & mouth opening."""
    global context, selected_word, last_selected_word, mouth_open
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb_frame)

        frame_height, frame_width, _ = frame.shape
        direction = "Center"
        head_bowed = False

        if result.multi_face_landmarks:
            for landmarks in result.multi_face_landmarks:
                left_eye = landmarks.landmark[33]
                right_eye = landmarks.landmark[263]
                nose_tip = landmarks.landmark[1]
                chin = landmarks.landmark[152]
                upper_lip = landmarks.landmark[13]
                lower_lip = landmarks.landmark[14]

                left_eye_coords = np.array([int(left_eye.x * frame_width), int(left_eye.y * frame_height)])
                right_eye_coords = np.array([int(right_eye.x * frame_width), int(right_eye.y * frame_height)])
                nose_y = int(nose_tip.y * frame_height)
                chin_y = int(chin.y * frame_height)
                eye_level = (left_eye_coords[1] + right_eye_coords[1]) // 2
                mouth_distance = abs(int(upper_lip.y * frame_height) - int(lower_lip.y * frame_height))

                delta_x = right_eye_coords[0] - left_eye_coords[0]
                delta_y = right_eye_coords[1] - left_eye_coords[1]
                tilt_angle = np.degrees(np.arctan2(delta_y, delta_x))

                if tilt_angle > 10:
                    direction = "Left Tilt"
                elif tilt_angle < -10:
                    direction = "Right Tilt"

                if nose_y > eye_level + 50:
                    head_bowed = True

                if mouth_distance > 15:
                    if not mouth_open:
                        send_email()
                        context = ""
                        mouth_open = True
                else:
                    mouth_open = False

        if direction == "Left Tilt":
            selected_word = current_words[2]
        elif direction == "Right Tilt":
            selected_word = current_words[0]
        elif head_bowed:
            selected_word = current_words[1]

        if selected_word and selected_word != last_selected_word:
            context += " " + selected_word
            last_selected_word = selected_word
            print(f"Updated Context: {context}")
            fetch_new_words()
            selected_word = None

        # Display overlay text
        cv2.putText(frame, f"Sentence: {context}", (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Display word choices
        cv2.putText(frame, current_words[0], (100, frame_height - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, current_words[1], (frame_width // 2 - 50, frame_height - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, current_words[2], (frame_width - 200, frame_height - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, RECIPIENT_EMAIL, (100, frame_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow("Head Tilt Word Selection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    fetch_new_words()
    process_video()
