from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import re

app = FastAPI(title="Customer Support AI Service")

# =====================================================
# MODELS
# =====================================================

intent_model = pipeline(
    "text-classification",
    model="./intent_model",
    tokenizer="./intent_model",
    return_all_scores=True
)

emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1
)

# =====================================================
# IN-MEMORY SESSION STORE
# =====================================================

conversation_memory = {}

# =====================================================
# INTENT LABELS
# =====================================================

INTENT_LABELS = {
    0: "cancel_order",
    1: "change_order",
    2: "change_shipping_address",
    3: "check_cancellation_fee",
    4: "check_invoice",
    5: "check_payment_methods",
    6: "return_policy",
    7: "complaint",
    8: "contact_customer_service",
    9: "contact_human_agent",
    10: "create_account",
    11: "delete_account",
    12: "delivery_options",
    13: "delivery_period",
    14: "edit_account",
    15: "get_invoice",
    16: "return_request",
    17: "newsletter_subscription",
    18: "payment_issue",
    19: "place_order",
    20: "recover_password",
    21: "registration_problems",
    22: "review",
    23: "set_up_shipping_address",
    24: "switch_account",
    25: "track_order",
    26: "track_refund",
    27: "replacement_request"
}

# =====================================================
# KEYWORD OVERRIDE (HIGHEST PRIORITY)
# =====================================================

KEYWORD_INTENT_MAP = {
    "replacement_request": ["replace", "replacement", "exchange"],
    "return_request": ["return", "defective", "damaged", "broken"],
    "return_policy": ["return policy", "how do i return"],
    "track_order": ["track", "where is my order", "order status"],
    "cancel_order": ["cancel", "stop order"]
}

# =====================================================
# INTENT RESPONSES
# =====================================================

INTENT_RESPONSES = {
    "track_order": "Please share your order ID so I can track it.",
    "cancel_order": "Please provide your order ID to cancel the order.",
    "replacement_request": "Please provide your order ID and reason for replacement.",
    "return_request": "Please provide your order ID and reason for return.",
    "return_policy": "You can return items within 7 days of delivery.",
    "track_refund": "Please share your order or refund ID.",
    "contact_human_agent": "Connecting you to a human support agent."
}

# =====================================================
# REQUEST SCHEMA
# =====================================================

class ChatRequest(BaseModel):
    session_id: str
    message: str

# =====================================================
# UTILITIES
# =====================================================

def extract_order_id(text: str):
    patterns = [
        r"\bORD\d+\b",
        r"\bORDER[-_]?\d+\b",
        r"#\d+",
        r"\b\d{5,}\b"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group()
    return None


def keyword_override(text: str):
    text = text.lower()
    for intent, kws in KEYWORD_INTENT_MAP.items():
        for kw in kws:
            if kw in text:
                return intent
    return None


def best_model_intent(scores):
    best = max(scores, key=lambda x: x["score"])
    label_id = int(best["label"].replace("LABEL_", ""))
    return INTENT_LABELS.get(label_id, "unknown"), best["score"]

# =====================================================
# ROUTES
# =====================================================

@app.post("/predict")
def predict(req: ChatRequest):

    session_id = req.session_id
    text = req.message.strip()

    # -------------------------------------------------
    # INIT MEMORY
    # -------------------------------------------------
    if session_id not in conversation_memory:
        conversation_memory[session_id] = {
            "intent": None,
            "order_id": None,
            "awaiting": None,
            "frustration_count": 0,
            "escalate": False,
            "completed": False
        }

    memory = conversation_memory[session_id]

    # -------------------------------------------------
    # EMOTION FIRST (ALWAYS)
    # -------------------------------------------------
    emotion = emotion_model(text)[0][0]["label"]

    if emotion in {"anger", "frustration", "disgust"}:
        memory["frustration_count"] += 1

    if memory["frustration_count"] >= 2:
        memory["escalate"] = True

    # -------------------------------------------------
    # ESCALATION
    # -------------------------------------------------
    if memory["escalate"]:
        return {
            "session_id": session_id,
            "intent": "contact_human_agent",
            "confidence": 1.0,
            "emotion": emotion,
            "action": "escalate_to_human",
            "memory": memory,
            "bot_reply": (
                "I’m really sorry you’re feeling this way. "
                "I’m connecting you to a human support agent now."
            )
        }

    # -------------------------------------------------
    # SLOT HANDLING (ORDER ID ONLY MESSAGE)
    # -------------------------------------------------
    order_id = extract_order_id(text)
    if order_id:
        memory["order_id"] = order_id

        if memory["intent"] in {
            "track_order", "cancel_order",
            "return_request", "replacement_request",
            "track_refund"
        }:
            memory["completed"] = True
            return {
                "session_id": session_id,
                "intent": memory["intent"],
                "confidence": 1.0,
                "emotion": emotion,
                "action": "process_request",
                "memory": memory,
                "bot_reply": (
                    f"I’ve found order {order_id}. "
                    f"Your request is being processed."
                )
            }

    # -------------------------------------------------
    # INTENT DETECTION
    # -------------------------------------------------
    intent = keyword_override(text)

    if not intent:
        scores = intent_model(text)[0]
        intent, confidence = best_model_intent(scores)
        if confidence < 0.6:
            intent = "unknown"
    else:
        confidence = 1.0

    # -------------------------------------------------
    # MEMORY OVERRIDE (CRITICAL FIX)
    # -------------------------------------------------
    if memory["order_id"] and intent == "unknown":
        intent = memory["intent"] or "track_order"

    memory["intent"] = intent
    memory["completed"] = False

    # -------------------------------------------------
    # RESPONSE LOGIC
    # -------------------------------------------------
    if intent in {
        "track_order", "cancel_order",
        "return_request", "replacement_request",
        "track_refund"
    }:
        if not memory["order_id"]:
            memory["awaiting"] = "order_id"
            bot_reply = "Please provide your order ID to continue."
            action = "ask_order_id"
        else:
            memory["completed"] = True
            bot_reply = f"Order {memory['order_id']} found. Processing now."
            action = "process_request"

    elif intent == "return_policy":
        bot_reply = INTENT_RESPONSES[intent]
        action = "inform"

    elif intent == "unknown":
        bot_reply = "Could you please clarify your request?"
        action = "ask_clarification"

    else:
        bot_reply = INTENT_RESPONSES.get(intent, "How can I help you?")
        action = "auto_reply"

    # -------------------------------------------------
    # FEEDBACK ONLY WHEN DONE & CALM
    # -------------------------------------------------
    if memory["completed"] and emotion not in {"anger", "frustration"}:
        bot_reply += " Before you go, please rate your experience from 1 to 5."
        action = "ask_feedback"

    return {
        "session_id": session_id,
        "intent": intent,
        "confidence": round(confidence, 4),
        "emotion": emotion,
        "action": action,
        "memory": memory,
        "bot_reply": bot_reply
    }