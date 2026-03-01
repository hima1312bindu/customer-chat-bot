Customer Support Chatbot (Transformer-Based)
Overview

This project is a transformer-based customer support chatbot designed to handle common e-commerce queries such as order tracking, cancellations, returns, and replacements. It uses NLP models to understand both user intent and user emotion to provide accurate and context-aware responses.

Features

Intent detection using a fine-tuned transformer model

Emotion detection to identify frustrated or angry users

Session-based conversation memory

Automatic escalation to human agent when needed

REST API built using FastAPI

Models Used

Intent Detection: Fine-tuned DistilBERT model

Emotion Detection: Pretrained transformer-based emotion classifier

Tech Stack

Python

FastAPI

Hugging Face Transformers

PyTorch

Regex for order ID extraction


How It Works

User sends a message to the chatbot

Emotion model detects user sentiment

Intent model predicts user intent

Conversation memory maintains context

Bot responds or escalates to a human agent

Use Cases

E-commerce customer support

Order tracking and returns

Payment and account-related queries

Future Enhancements

Database-backed conversation memory

Multilingual support

Frontend integration (React / Mobile App)
