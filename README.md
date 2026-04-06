# 🏭 Order Systems Production

A RESTful API built with **Flask** and **SQLite** for managing production orders in a factory environment. It exposes a full CRUD interface and serves a static frontend dashboard directly from the backend.

---

## 📁 Project Structure

```
Order_Systems_Production/
├── app.py              # Main Flask application — all API routes
├── database.py         # SQLite database initialization and connection
├── orders.db           # SQLite database file (auto-generated on first run)
├── requirements.txt    # Python dependencies
├── static/             # Frontend files (HTML, CSS, JS) served by Flask
├── postman/            # Postman collection for API testing
├── .gitignore          # Files and folders excluded from version control
└── README.md           # This file
```

---

## ⚙️ Prerequisites

- **Python 3.8+** installed on your system
- **pip** (comes bundled with Python)
- **VS Code** (recommended editor)

---

## 🧩 Recommended VS Code Extensions

Install the following extensions from the VS Code Marketplace (`Ctrl+Shift+X`):

| Extension | Purpose |
|---|---|
| **Python** (Microsoft) | Python language support, IntelliSense, and debugging |
| **SQLite Viewer** | View and inspect the `orders.db` database file directly in VS Code |
| **HTML** | Syntax highlighting and completion for HTML files |
| **CSS** | Styling support for the frontend |
| **JavaScript** | JS language support for the frontend scripts |
| **Rest Client** | Send HTTP requests to the API directly from `.http` files inside VS Code |
| **Git Lens** | Provides deep insight into code history, authorship and collaborative workflows |

> 💡 **Tip:** You can install all of them quickly by searching their names in the Extensions panel (`Ctrl+Shift+X`).

---

## 🐍 Setting Up the Virtual Environment (venv)

A virtual environment keeps this project's dependencies isolated from other Python projects on your machine — always use one.

### 1. Create the virtual environment

Open a terminal in the project root folder and run:

```bash
# Windows
python -m venv venv

# macOS / Linux
python3 -m venv venv
```

This creates a `venv/` folder inside the project directory.

### 2. Activate the virtual environment

```bash
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Once activated, your terminal prompt will show `(venv)` at the beginning, confirming the environment is active.

### 3. Deactivate when done coding

```bash
deactivate
```

---

## 📦 Installing Dependencies (`requirements.txt`)

The `requirements.txt` file lists every external Python library that this project needs, with their exact version numbers pinned to ensure consistent behavior across machines. It includes:

| Package | Purpose |
|---|---|
| `Flask` | The web framework that powers the API and serves the frontend |
| `flask-cors` | Enables Cross-Origin Resource Sharing (CORS) so the frontend can call the API |
| `Werkzeug` | Flask's underlying HTTP toolkit (request/response handling) |
| `Jinja2` | Templating engine used internally by Flask |
| `MarkupSafe` | Safe string handling for Jinja2 |
| `click` | Command-line utilities used by Flask's CLI |
| `blinker` | Signal support used by Flask's event system |
| `colorama` | Colored terminal output (used on Windows) |
| `itsdangerous` | Cryptographic signing for Flask sessions |

### Install all dependencies at once

With your virtual environment **active**, run (you might need to upgrade your pip first):

```bash
pip install -r requirements.txt
```

This reads every line in `requirements.txt` and installs the exact version specified, so you always get the same environment as the original developer.

---

## 🚀 Running the Application

With the virtual environment active and dependencies installed:

```bash
python app.py
```

The server starts on **http://localhost:5000**.

You should see output like:

```
Database successfully inicialized!
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

Open your browser and go to **http://localhost:5000** to view the dashboard.

---

## 🔌 API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend dashboard (`index.html`) |
| `GET` | `/status` | Health check — returns API version and status |
| `GET` | `/orders` | Lists all production orders (newest first) |
| `GET` | `/orders/<id>` | Retrieves a single order by ID |
| `POST` | `/orders` | Creates a new production order |
| `PUT` | `/orders/<id>` | Updates the status of an existing order |
| `DELETE` | `/orders/<id>` | Permanently removes an order |

### Order status values

- `Pending` (default when creating)
- `In progress`
- `Done`

### Example request body for POST / PUT

```json
{
  "product": "Gear Assembly",
  "quantity": 50,
  "status": "Pending"
}
```

---

## 🗄️ Database

The project uses **SQLite** via Python's built-in `sqlite3` module — no external database server required.

- The database file `orders.db` is automatically created on first run by `database.py`.
- The `orders` table is created with `CREATE TABLE IF NOT EXISTS`, making it safe to call the initializer multiple times without overwriting data.
- Each order record contains: `id`, `product`, `quantity`, `status`, and `created_at`.

You can inspect the database visually using the **SQLite Viewer** VS Code extension — simply click on `orders.db` in the Explorer panel.

---

## 🧪 Testing the API

### Option 1 — Rest Client (VS Code)

Create a file named `requests.http` in the project root and write requests like:

```http
GET http://localhost:5000/orders

###

POST http://localhost:5000/orders
Content-Type: application/json

{
  "product": "Wheel Hub",
  "quantity": 100
}

###

PUT http://localhost:5000/orders/1
Content-Type: application/json

{
  "status": "In progress"
}

###

DELETE http://localhost:5000/orders/1
```

Click **Send Request** above each block to execute it directly in VS Code.

### Option 2 — Postman

A ready-to-import Postman collection is included in the `postman/collections/Order System API/` folder. Import it into Postman to get all endpoints pre-configured.

---

## 🙈 Version Control & `.gitignore`

The `.gitignore` file tells Git which files and folders to **exclude from version tracking**. This is important to avoid committing unnecessary or sensitive files.

For this project, you should make sure the following are ignored:

```gitignore
# Virtual environment — never commit this
venv/

# Python bytecode cache
__pycache__/
*.pyc
*.pyo

# SQLite database — optional (ignore if you don't want to share data)
orders.db

# VS Code workspace settings
.vscode/

# OS-generated files
.DS_Store
Thumbs.db

# Environment variables (if added in the future)
.env
```

> ⚠️ **Important:** Always add `venv/` to `.gitignore` before your first commit. The virtual environment folder can contain hundreds of files and should never be pushed to GitHub. Anyone cloning the repo will recreate it using `requirements.txt`.

---

## 🔁 Typical Development Workflow

```bash
# 1. Clone the repository
git clone https://github.com/henrique-svg21/Order_Systems_Production.git
cd Order_Systems_Production

# 2. Create and activate the virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python app.py

# 5. Open http://localhost:5000 in your browser
```

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
