# 🚀 Dark Theme Productivity Dashboard

A modern, polished dark-theme dashboard application built with **Flask**, featuring a real-time clock, a persistent to-do list, and integration with your personal **Google Calendar** for upcoming events. Designed for local use and deployed with **Gunicorn** for reliable performance.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-latest-green.svg)

---

## ✨ Features

- **Real-Time Clock & Date** - Displays the current time and full date
- **Persistent To-Do List** - Tasks are saved to a local JSON file (`notifications.json`)
- **Google Calendar Integration** - Connects securely via local credentials to display events for the next 24 hours
- **Polished Dark UI** - Sleek, modern dark theme with glassmorphism effects (blur and transparency)
- **Production Ready** - Configured for deployment using Gunicorn and Nginx

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed and configured:

### 1. Python Environment

Python 3.8 or higher is required. A virtual environment is highly recommended.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Google Calendar API Setup

This project uses your personal Google credentials for simple, local access.

1. **Enable API**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and enable the Google Calendar API for your project.

2. **Create Credentials**: 
   - Navigate to **APIs & Services > Credentials**
   - Create an **OAuth client ID**
   - Select the application type as **Desktop App**

3. **Download & Rename**: 
   - Download the JSON credentials file
   - Rename it to `client_secret.json`
   - Place it in the root directory of this project

### 3. Required Python Packages

Install the necessary libraries using pip:

```bash
pip install Flask gunicorn google-api-python-client google-auth-oauthlib google-auth-httplib2
```

Or install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 📂 Project Structure

```
my-dashboard/
├── app.py                      # Flask application and API endpoints
├── client_secret.json          # Your downloaded Google OAuth file
├── requirements.txt            # List of dependencies
├── notifications.json          # Persistent storage for to-do list (auto-generated)
├── token.json                  # Google refresh token (auto-generated after first run)
└── templates/
    └── index.html              # Frontend UI (HTML, CSS, JS)
```

---

## ⚙️ Local Development and First Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pgokul695/Todo_app
   cd dark-theme-dashboard
   ```

2. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask app**:
   ```bash
   python app.py
   ```

5. **Authorization**: On the first run, the terminal will prompt you to authorize the application. A browser window will open; follow the steps to grant access to your calendar. This will generate a `token.json` file, allowing for silent refreshes on future runs.

6. **Access**: Open your browser to `http://127.0.0.1:5000/`

---

## 🚀 Production Deployment (Gunicorn & Nginx)

For reliable hosting, use Gunicorn as the application server and Nginx as a reverse proxy.

### 1. Run Gunicorn

Start Gunicorn, binding it to a local port (e.g., 8000):

```bash
gunicorn -w 4 'app:app' --bind 0.0.0.0:8000
```

### 2. Configure Nginx Reverse Proxy

Create an Nginx configuration file (e.g., `/etc/nginx/sites-available/dashboard`):

```nginx
server {
    listen 80;
    server_name your_server_ip_or_domain;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Manage with Systemd

Create a Systemd service file (e.g., `/etc/systemd/system/dashboard.service`):

```ini
[Unit]
Description=Gunicorn instance to serve Dark Theme Dashboard
After=network.target

[Service]
User=your_system_user
Group=www-data
WorkingDirectory=/path/to/my-dashboard/
ExecStart=/path/to/your/venv/bin/gunicorn -w 4 'app:app' --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Reload and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start dashboard
sudo systemctl enable dashboard
```

---

## 🔒 Security Notes

- Keep `client_secret.json` and `token.json` private and never commit them to version control
- Add them to your `.gitignore` file:
  ```
  client_secret.json
  token.json
  notifications.json
  ```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📧 Contact

Gokul P- pgokul695@gmail.com

Project Link: [https://github.com/pgokul695/Todo_app](https://github.com/pgokul695/Todo_app)]
---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Google Calendar API](https://developers.google.com/calendar) - Calendar integration
- [Gunicorn](https://gunicorn.org/) - WSGI HTTP Server
