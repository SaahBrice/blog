# 📖 SAAH Blogging Platform

Welcome to **SAAH** – a powerful and feature-rich blogging platform inspired by Medium, with unique enhancements that make it a standout choice for content creators. 

## 🚀 Project Overview

**SAAH** is a blogging platform designed to provide a rich and engaging user experience. With all the core features of Medium and additional enhancements like multilingual support, advanced reactions, TEXT to SPEECH and more, **SAAH** aims to be the go-to platform for bloggers and readers alike.

### Key Features:

- **User Registration and Authentication**: Including phone, Google, and email authentication.
- **Article Management**: Write, edit, publish, and manage articles with ease.
- **Reactions**: Three types of reactions (clap, laugh, sad) with customizable reaction counts.
- **Media Support**: Upload videos alongside your articles.
- **Tagging**: Tag users and topics within articles.
- **Text-to-Speech**: Listen to articles being read aloud.
- **Translation**: Switch between English and French with a simple button.
- **Categorization**: Separate articles into English and French categories, with support for bilingual content.
- **User Interaction**: Commenting, following, notifications, and bookmarking.

## 🛠️ Technology Stack

### Backend

- **Django**: The primary backend framework, providing a robust and scalable architecture.
- **SQL Database**: For managing persistent data efficiently.
- **Django Allauth**: Handling various authentication methods.

### Frontend

- **React (or similar UI library)**: A powerful frontend library for building interactive user interfaces.
- **Material UI**: For a minimalistic and user-friendly design.
- **Custom CSS**: For additional styling and customization.

### External Libraries and Tools

- **Text Editor**: Integrated text editor for creating rich content (EditorJS).
- **Text-to-Speech API**: Convert text to speech within articles.
- **Translation API**: For translating articles between English and French.


## 🔧 Installation and Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10**: Required for running Django.
- **PostgreSQL/MySQL**: Recommended SQL databases for production.
- **Git**: For version control.

### Installation

Follow these steps to get the project up and running on your local machine:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/saahbrice/blog.git
   cd 237
   ```

2. **Create a Virtual Environment**:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install Backend Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**:


   ```bash
   pip install tailwindcss
   ```

5. **Database Setup**:

   Ensure your database is set up and configure the connection in `settings.py`:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': '237_db',
           'USER': 'yourusername',
           'PASSWORD': 'yourpassword',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

   Then, apply the migrations:

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**:

   ```bash
   python manage.py runserver
   ```

   The app should now be running at `http://127.0.0.1:8000/`.

8. **Access the Admin Panel**:

   Visit `http://127.0.0.1:8000/admin/` and log in with the superuser credentials you created.

## 🛠️ Features and Implementation Details

### 1. **User Authentication**

The platform supports multiple authentication methods, including:

- **Phone Authentication**: Secure phone number verification.
- **Google Authentication**: Quick login via Google accounts.
- **Email Authentication**: Standard email-based registration and login.

Implementation is handled via **Django Allauth**, providing a flexible and secure authentication system.

### 2. **Article Management**

Users can write, edit, and publish articles using a rich text editor integrated into the platform. The editor supports markdown and HTML, making it easy to format content. Articles are stored in the SQL database, and users can categorize them by tags and topics.

### 3. **Reactions System**

The platform features an advanced reactions system where users can:

- **Clap**: Show appreciation.
- **Laugh**: React humorously.
- **Sad**: Express sympathy or sadness.

Each reaction can be amplified by choosing the number of reactions (+10, +50, +100), allowing users to express their feelings more intensely.

### 4. **Media Uploads**

Articles can include embedded videos, making content more engaging.

### 5. **Tagging and Categorization**

- **Tagging Users and Topics**: Enhance content discovery by tagging other users and relevant topics.
- **Categorization**: Articles are categorized into English and French, supporting a bilingual audience.

### 6. **Text-to-Speech and Translation**

- **Text-to-Speech**: Users can listen to articles through an integrated text-to-speech feature, enhancing accessibility.
- **Translation**: With a click of a button, switch between English and French, making the platform accessible to a wider audience.

### 7. **Responsive UI/UX**

The platform is designed with a minimalistic approach using **Material UI**, ensuring a clean and user-friendly interface. The UI is responsive, providing a seamless experience across devices, from desktops to mobile phones.


## 🚀 Deployment

### Deployment Steps

1. **Configure Production Settings**: Update `settings.py` with production configurations, such as disabling `DEBUG`, setting `ALLOWED_HOSTS`, and configuring the production database.

2. **Collect Static Files**:

   ```bash
   python manage.py collectstatic
   ```

3. **Deploy to Cloud Platform**: Deploy the application using cloud services like **Heroku**, **AWS**, or **Google Cloud**. Ensure the environment is set up correctly with environment variables and database connections.



## 📄 License

This project is licensed under the MIT License

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## 📧 Contact

For any inquiries or support, please contact the project team at saahbrice98@gmail.com
