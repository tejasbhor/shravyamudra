# Shravyamudra: Real-time Gesture to Text Translation

---

![Shravyamudra Logo/Banner](https://via.placeholder.com/1200x400/007bff/ffffff?text=Shravyamudra+Banner)
*Replace this with an actual project banner/logo if available.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-green)
![React](https://img.shields.io/badge/React-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-darkblue)
![Node.js](https://img.shields.io/badge/Node.js-16%2B-green)

---

## ✨ Project Overview

Shravyamudra is an innovative web application designed to bridge communication gaps by providing **real-time gesture-to-text translation**. Leveraging a powerful combination of a Django REST Framework backend and a React frontend, Shravyamudra empowers users to translate gestures into written text, making communication more accessible and intuitive.

Beyond real-time translation, the platform includes interactive **learning modules** to help users understand and practice various gestures, fostering a deeper understanding of sign language.

**Shravyamudra** represents a significant advancement in assistive technology, specifically designed to bridge communication barriers between English/Hindi speakers and users of Indian Sign Language (ISL). As a **capstone project for university**, Shravyamudra has evolved into a sophisticated platform aimed at empowering the deaf community through seamless and intuitive communication.

This innovative web application accurately converts written text into ISL gestures, leveraging a modular, full-stack architecture that incorporates modern technologies. Our primary objective is to enhance accessibility and communication for the ISL community by providing:

* **Real-time Gesture Translation:** A powerful system for converting text into visual ISL gestures.
* **User-Friendly Interface:** Designed for ease of use and compatibility across various devices.
* **Comprehensive Learning Platform:** Structured ISL lessons with progress tracking to foster deeper understanding and practice.

The implementation utilizes **React with TypeScript** for a dynamic frontend, with robust backend services powered by **Django REST Framework** and **PostgreSQL** for efficient data management. The integration of **AI models** significantly enhances text processing and gesture mapping capabilities, ensuring accurate and effective translations.

Shravyamudra is not just a project; it's a crucial step forward in promoting inclusivity and usability in ISL communication, setting a foundation for future innovations in language translation technologies aimed at improving accessibility for the deaf community.

---

## 🏆 Awards & Recognition

We are proud to announce that Shravyamudra has achieved significant recognition:

* **Dipex Competition 2025 Qualifier:** This project has successfully participated and qualified for the prestigious Dipex Competition 2025, showcasing its innovation and potential on a larger stage.

---

## 🚀 Getting Started

Follow these steps to set up Shravyamudra on your local machine for development and testing.

### Prerequisites

Before you begin, ensure you have the following software installed on your system:

* **Node.js**: `v16.0` or higher (includes `npm`)
* **Python**: `v3.8` or higher
* **PostgreSQL**: `v12` or higher (a running instance is required)
* **Git**: For cloning the repository
* **pip**: Python package installer (usually comes with Python)
* **virtualenv** (or Python's built-in `venv`): For creating isolated Python environments

### Installation

1.  **Clone the Repository:**
    Start by cloning the Shravyamudra repository to your local machine:
    ```bash
    git clone [https://github.com/yourusername/Shravyamudra.git](https://github.com/yourusername/Shravyamudra.git)
    cd Shravyamudra
    ```
    *(**Remember to replace `yourusername` with the actual GitHub username or organization name for your repository!**)*

2.  **Backend Setup:**
    Navigate to the backend directory and set up the Python environment:
    ```bash
    cd Shravyamudra_Backend

    # Create a virtual environment
    python -m venv .venv

    # Activate the virtual environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    # .venv\Scripts\activate

    # Install Python dependencies
    pip install -r requirements.txt
    ```

3.  **Frontend Setup:**
    Open a **new terminal** or navigate back to the root `Shravyamudra` directory, then proceed to the frontend setup:
    ```bash
    cd ../Shravyamudra-frontend

    # Install Node.js dependencies
    npm install
    # or if you prefer yarn:
    # yarn install
    ```

### Configuration

Proper configuration of environment variables is crucial for both the backend and frontend.

1.  **Backend Configuration:**
    * Navigate back to the `Shravyamudra_Backend` directory.
    * Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    * **Edit the newly created `.env` file:** Fill in your specific configurations. Pay close attention to:
        * `SECRET_KEY`: Generate a strong, unique secret key for Django.
        * `DEBUG`: Set to `True` for development.
        * `ALLOWED_HOSTS`: Add `localhost`, `127.0.0.1`.
        * **Database Credentials:** `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
        * `GOOGLE_API_KEY`: Your Google AI API key, essential for AI-powered features.
        * Other settings like email configurations or CORS origins as needed.
    * **Database Setup:** Ensure your PostgreSQL server is running. Create the database and user as specified in your `.env` file. Here's an example using `psql`:
        ```sql
        -- Connect to your PostgreSQL server, then run:
        CREATE DATABASE shravyamudra;
        CREATE USER your_db_user WITH PASSWORD 'your_db_password';
        GRANT ALL PRIVILEGES ON DATABASE shravyamudra TO your_db_user;
        ```
        *(**Note:** Replace `shravyamudra`, `your_db_user`, and `your_db_password` with your actual values from the `.env` file.)*

2.  **Frontend Configuration:**
    * Navigate to the `Shravyamudra-frontend` directory.
    * Copy the example environment file:
        ```bash
        cp .env.example .env.local
        ```
    * **Edit the `.env.local` file:** Set the backend API URL:
        ```env
        VITE_API_BASE_URL=http://localhost:8000/api
        ```

### Running the Application

With everything configured, you can now run both the backend and frontend servers.

1.  **Run Backend Migrations & Setup:**
    * Ensure you are in the `Shravyamudra_Backend` directory with your virtual environment activated.
    * Apply database migrations to set up your database schema:
        ```bash
        python manage.py migrate
        ```
    * Create a superuser account to access the Django administration panel:
        ```bash
        python manage.py createsuperuser
        ```
    * *(Optional)* Load any initial data if your project includes it:
        ```bash
        # python manage.py loaddata initial_data.json
        ```

2.  **Start the Backend Server:**
    In the `Shravyamudra_Backend` directory (with virtual environment activated), start the Django development server:
    ```bash
    python manage.py runserver
    ```
    The backend API will typically be accessible at `http://localhost:8000`.

3.  **Start the Frontend Development Server:**
    * Open a **new terminal window/tab**.
    * Navigate to the `Shravyamudra-frontend` directory.
    * Start the Vite development server:
        ```bash
        npm run dev
        # or if you prefer yarn:
        # yarn dev
        ```
    The frontend application will typically be available at `http://localhost:5173`.

---

## 💻 Usage

Once both the backend and frontend servers are successfully running:

1.  Open your preferred web browser and navigate to `http://localhost:5173` (or the port indicated by Vite).
2.  **Register** for a new user account or **Log In** if you already have credentials.
3.  Explore the **gesture translation features** to see real-time translation in action.
4.  Dive into the **learning modules** to enhance your understanding of various gestures.
5.  Access the **Django Admin interface** at `http://localhost:8000/admin/` using the superuser credentials you created to manage data and users.

---

## 📄 API Documentation

The Shravyamudra backend API is powered by Django REST Framework and comes with interactive documentation:

* **Swagger UI:** Access detailed, interactive API documentation and test endpoints at `http://localhost:8000/api/docs/`
* **Redoc:** View alternative, user-friendly API documentation at `http://localhost:8000/api/redoc/`

Key API endpoint categories you'll find include:

* `/auth/`: User Authentication (Registration, Login, Profile Management)
* `/translation/`: Gesture Translation & History Management
* `/learn/`: Learning Modules & Progress Tracking

Refer to the interactive documentation for precise endpoint specifications, request/response schemas, and testing capabilities.

---

## 🔧 Development

Here are some quick references and guidelines for development:

* **Backend API Base URL:** `http://localhost:8000/api/`
* **Frontend Dev Server:** `http://localhost:5173`
* **Code Style:** We adhere to standard Python (PEP 8) and TypeScript/React conventions. We highly recommend using linters and formatters:
    * **Python:** `flake8`, `black`
    * **TypeScript/React:** `ESLint`, `Prettier`
* **Testing:**
    * **Backend Tests:**
        ```bash
        cd Shravyamudra_Backend
        python manage.py test
        ```
    * **Frontend Tests:**
        ```bash
        cd Shravyamudra-frontend
        npm test
        # or yarn test
        ```
    *(**Note:** Ensure your test commands are correctly configured in `package.json` for frontend and Django settings for backend.)*

---

## 🤝 Contributing

We welcome and highly appreciate contributions to Shravyamudra! Your efforts help make this project better for everyone. Here’s how you can contribute:

1.  **Fork the Repository:** Create your own copy of the project on GitHub.
2.  **Create a Feature Branch:** Choose a descriptive name for your branch:
    ```bash
    git checkout -b feature/your-amazing-feature
    # Example: git checkout -b feat/add-dark-mode
    ```
    Or for bug fixes:
    ```bash
    git checkout -b bugfix/resolve-issue-xyz
    # Example: git checkout -b fix/login-button-alignment
    ```
3.  **Make Your Changes:** Implement your feature or fix the bug.
4.  **Commit Your Changes:** Write clear, concise, and descriptive commit messages. Follow Conventional Commits for better readability.
    ```bash
    git commit -m 'feat: Add feature X' -m 'Detailed description of the new functionality added.'
    # For fixes:
    # git commit -m 'fix: Resolve issue Y' -m 'Description of the bug fix and its impact.'
    ```
5.  **Push to Your Branch:**
    ```bash
    git push origin feature/your-amazing-feature
    ```
6.  **Open a Pull Request (PR):**
    * Go to your forked repository on GitHub and open a Pull Request from your branch to the `main` branch of the original Shravyamudra repository.
    * Provide a detailed description of your changes, the problem it solves, or the feature it introduces in the PR description.

**Contribution Guidelines:**

* Please **report bugs or suggest features** by opening an issue first. This allows for discussion and avoids duplicate efforts.
* Ensure your code adheres to the project's coding standards. Run linters and formatters before committing.
* **Write tests** for new features or bug fixes to ensure reliability.
* **Update documentation** (like this README, code comments) as needed to reflect your changes.
* Ensure your Pull Request is based on the latest `main` branch to minimize merge conflicts.

---

## 🗺️ Roadmap

Here's a glimpse of what's planned for the future of Shravyamudra:

* [ ] Enhanced multi-language support for UI and translation output.
* [ ] Offline mode capabilities for translation and learning modules.
* [ ] Advanced analytics for learning patterns and user engagement.
* [ ] Integration with a wider range of sign language datasets.
* [ ] Dedicated mobile application development (iOS/Android).
* [ ] User-customizable gesture library with personalized learning paths.

*(This roadmap is subject to change based on community feedback and project priorities.)*

---

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file in the root of this repository for more details.

---

## 📞 Contact & Support

Have questions, need support, or want to connect?

* **Project Repository:** [https://github.com/yourusername/Shravyamudra](https://github.com/yourusername/Shravyamudra) *(**Don't forget to update `yourusername`!**)*
* **Report an Issue:** [https://github.com/yourusername/Shravyamudra/issues](https://github.com/yourusername/Shravyamudra/issues)
* **Request a Feature:** [https://github.com/yourusername/Shravyamudra/issues/new?template=feature_request.md](https://github.com/yourusername/Shravyamudra/issues/new?template=feature_request.md) *(Assumes you have issue templates set up on GitHub.)*

---

## 🙏 Acknowledgments

A heartfelt thank you to:

* The incredible open-source community for inspiration and countless valuable resources.
* The developers of the core technologies that power Shravyamudra: **Django**, **React**, **PostgreSQL**, and **Vite**.
* [shadcn/ui](https://ui.shadcn.com/) for providing a fantastic set of UI components that greatly enhance the frontend.
* And finally, to **all contributors** who help improve Shravyamudra!