import cv2
import mediapipe as mp
import time
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# ==========================================
# 1. ΡΥΘΜΙΣΗ HARDWARE (ΣΕΡΒΟΚΙΝΗΤΗΡΕΣ)
# ==========================================
factory = PiGPIOFactory()
SERVO_PINS =   # GPIO Pins στο Raspberry Pi
servos = [Servo(pin, pin_factory=factory) for pin in SERVO_PINS]

PIN_DOWN = -0.6  
PIN_UP = 0.6     

def drive_servos(braille_state):
    for i in range(6):
        if braille_state[i] == 1:
            servos[i].value = PIN_UP
        else:
            servos[i].value = PIN_DOWN

# ==========================================
# 2. ΛΕΞΙΚΟ ΜΕΤΑΦΡΑΣΗΣ BRAILLE ΣΕ ΚΕΙΜΕΝΟ
# ==========================================
# Κλειδί είναι η πλειάδα (tuple) των 6 ακίδων και τιμή το γράμμα.
# Μπορείτε να προσθέσετε όλο το ελληνικό αλφάβητο Braille εδώ.
REVERSE_BRAILLE_MAP = {
    (1, 0, 0, 0, 0, 0): "Α",
    (1, 1, 0, 0, 0, 0): "Β",
    (1, 0, 0, 1, 0, 0): "Γ",  # Στο διεθνές είναι το C
    (1, 0, 0, 1, 1, 0): "Δ",
    (1, 0, 0, 0, 1, 0): "Ε",
    (1, 1, 0, 1, 0, 0): "Φ",
    (1, 1, 0, 1, 1, 0): "Γ",
    (1, 1, 0, 0, 1, 0): "Η",
    (0, 1, 0, 1, 0, 0): "Ι",
    (1, 0, 1, 0, 0, 0): "Κ",
    (1, 1, 1, 0, 0, 0): "Λ",
    (1, 0, 1, 1, 0, 0): "Μ",
    (1, 0, 1, 1, 1, 0): "Ν",
    (1, 0, 1, 0, 1, 0): "Ξ",
    (1, 1, 1, 1, 0, 0): "Π",
    (1, 1, 1, 0, 1, 0): "Ρ",
    (0, 1, 1, 1, 0, 0): "Σ",
    (0, 1, 1, 1, 1, 0): "Τ",
    (1, 0, 1, 0, 0, 1): "Υ",
    (0, 1, 0, 1, 1, 0): "Ω",
    (0, 0, 0, 0, 0, 0): "[Κενό / Αναμονή]"
}

def translate_braille_to_text(braille_state):
    """Μετατρέπει τη λίστα 6 στοιχείων στο αντίστοιχο γράμμα"""
    braille_tuple = tuple(braille_state) # Μετατροπή σε tuple για χρήση ως κλειδί
    return REVERSE_BRAILLE_MAP.get(braille_tuple, "Άγνωστος Συνδυασμός")

# ==========================================
# 3. ΡΥΘΜΙΣΗ AI (MEDIAPIPE)
# ==========================================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

def check_finger_up(hand_landmarks, tip_id, pip_id):
    return 1 if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[pip_id].y else 0

# ==========================================
# 4. ΚΥΡΙΟΣ ΒΡΟΧΟΣ ΕΠΕΞΕΡΓΑΣΙΑΣ
# ==========================================
cap = cv2.VideoCapture(0)
FINGER_TIPS = 
FINGER_PIPS = 

print("Το σύστημα μετάφρασης ξεκίνησε!")

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # 1. Αντίληψη των χειρονομιών και χαρτογράφηση σε 6-bit Braille
        current_braille_state = 

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                hand_label = handedness.classification.label
                f1 = check_finger_up(hand_landmarks, FINGER_TIPS, FINGER_PIPS)
                f2 = check_finger_up(hand_landmarks, FINGER_TIPS, FINGER_PIPS)
                f3 = check_finger_up(hand_landmarks, FINGER_TIPS, FINGER_PIPS)

                if hand_label == "Left":
                    current_braille_state = f1
                    current_braille_state = f2
                    current_braille_state = f3
                elif hand_label == "Right":
                    current_braille_state = f1
                    current_braille_state = f2
                    current_braille_state = f3

        # 2. Κίνηση του Hardware
        drive_servos(current_braille_state)

        # 3. ΝΕΟ: Μετάφραση του συνδυασμού σε γράμμα κειμένου
        detected_letter = translate_braille_to_text(current_braille_state)

        # 4. Οπτική απεικόνιση στην οθόνη για την παρουσίαση
        cv2.putText(frame, f"Γράμμα: {detected_letter}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        
        cv2.putText(frame, f"Δυαδικό: {current_braille_state}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Σχεδίαση των 6 εικονικών κουκκίδων Braille στην οθόνη
        for idx, state in enumerate(current_braille_state):
            color = (0, 255, 0) if state == 1 else (0, 0, 255)
            cx = 50 if idx < 3 else 110
            cy = 150 + (idx % 3) * 40
            cv2.circle(frame, (cx, cy), 12, color, -1)
            cv2.putText(frame, str(idx+1), (cx-5, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)

        cv2.imshow('ELLAK 2026 - Sign to Braille Translator', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("Το σύστημα έκλεισε ομαλά.")
