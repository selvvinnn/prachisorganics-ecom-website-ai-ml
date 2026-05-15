# Prachi's Organics E-Commerce Website with AI Features

Prachi's Organics is a full-stack e-commerce website built for an organic skincare and haircare brand. The platform includes product browsing, user authentication, cart management, order flow, profile management, AI chatbot support, and an AI-based face authentication login system.

Live Website: https://prachisorganics.com

---

## Project Overview

This project started as an e-commerce website for Prachi's Organics and was later extended with AI/ML features to improve user experience and authentication.

The website allows users to:

- Browse skincare, haircare, and bodycare products
- View product details
- Add products to cart
- Place orders
- Track orders
- Manage their user profile
- Register and log in using facial recognition
- Ask product and policy-related questions through an AI chatbot

---

## Key Features

### 1. E-Commerce Functionality

- Product listing page
- Product detail page
- Category-based product browsing
- Cart system
- Checkout flow
- Order success page
- Order tracking
- User profile page
- Login and signup system
- Policy pages such as privacy, refund, returns, and terms

---

### 2. AI Chatbot Assistant

The website includes an AI chatbot assistant that helps users ask questions related to:

- Products
- Skincare routines
- Haircare products
- Refund policy
- Delivery information
- Brand-related FAQs

The chatbot is connected to a backend AI service that uses Retrieval-Augmented Generation to answer user queries based on the brand knowledge base.

---

### 3. Multimodal RAG System

A separate Multimodal Retrieval-Augmented Generation system was built for the chatbot.

The RAG system can process:

- PDF documents
- Text content
- Tables
- Images inside documents

It extracts useful information from the brand knowledge base and uses it to generate accurate answers for user queries.

Main RAG workflow:

1. Load PDF knowledge base
2. Extract text, tables, and image content
3. Create intelligent chunks
4. Generate AI-enhanced summaries
5. Store embeddings in a vector database
6. Retrieve relevant chunks based on user query
7. Generate final answer using an LLM

---

### 4. AI Face Authentication System

The project includes a browser-based facial recognition login system integrated with the existing Django authentication system.

Face login flow:

1. User opens the login page
2. User clicks "Login with Face"
3. Browser opens webcam
4. Image is captured from the webcam
5. Image is sent to Django backend
6. Backend processes the image using the face authentication service
7. Face is detected
8. Facial embedding is generated
9. Embedding is compared with the stored user embedding
10. If matched, the user is logged in using Django sessions

The system works on:

- Desktop browsers
- Laptop browsers
- Mobile browsers with camera access

---

## Privacy Approach for Face Login

The system does not store raw face images.

Instead, it stores only facial embeddings in the database. These embeddings are numerical representations of the user's face and are used for matching during login.

This approach improves privacy compared to storing actual face images.

---

## Face Authentication Reliability Checks

The face authentication system includes validation checks such as:

- Single-face validation
- Face detection confidence check
- Blur detection
- Brightness validation
- Face-size validation
- Embedding similarity comparison

These checks help reduce false matches and improve login reliability.

---

## Tech Stack

### Backend

- Python
- Django
- FastAPI
- SQLite
- Django Authentication
- Django Sessions

### Frontend

- HTML
- CSS
- JavaScript
- Tailwind CSS

### AI / ML

- InsightFace
- ONNX Runtime
- OpenCV
- LangChain
- ChromaDB
- OpenAI API
- Unstructured PDF Parser

### Deployment

- AWS
- Gunicorn
- Nginx
- GitHub

---

## Folder Structure

```text
PrachiWebsiteNEW/
│
├── face_auth/
│   ├── service.py
│   └── ...
│
├── prachiorganics/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── store/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── store/
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── login.html
│   │       ├── signup.html
│   │       ├── profile.html
│   │       ├── face_register.html
│   │       ├── face_login.html
│   │       ├── products.html
│   │       ├── product_detail.html
│   │       ├── cart.html
│   │       └── ...
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── ...
│
├── media/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md


Installation and Local Setup
1. Clone the Repository
git clone https://github.com/selvvinnn/your-repository-name.git
cd your-repository-name
2. Create a Virtual Environment
python -m venv .venv

Activate it:

For Windows:

.venv\Scripts\activate

For Mac/Linux:

source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Create .env File

Create a .env file in the project root.

Example:

SECRET_KEY=your_django_secret_key
DEBUG=True
OPENAI_API_KEY=your_openai_api_key

Do not push .env to GitHub.

5. Run Migrations
python manage.py makemigrations
python manage.py migrate
6. Create Superuser
python manage.py createsuperuser
7. Run Django Server
python manage.py runserver

Open:

http://127.0.0.1:8000/
