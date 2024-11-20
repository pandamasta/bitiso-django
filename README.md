# 🌐 Django-Bitiso

**Django-Bitiso** is a Django-based platform designed to manage and share torrents, offering advanced features like tracker scraping and user management.

## 🚀 Features

### 📤 Torrent Upload
- Upload torrents directly through the user interface.
- Organize your torrents by categories and projects.

### 📥 Torrent Download
- Import torrents from external sources.
- Support for `.torrent` files and Magnet links.

### 🔍 Tracker Scraping
- Scrape tracker data for efficient torrent management.
- Automatically update statistics (seed, leech, etc.).

### 🌎 Multilingual Support
- Fully localized in English and French.
- Looking for contributors to help with additional translations! 🌟

### 🔒 GPG Signature Management *(In Progress)*
- Add a security layer with GPG signatures to ensure file authenticity.

### 👥 User Management *(In Progress)*
- User profiles with profile pictures, bios, and social links.
- Customizable notifications and preferences.
- API to fetch liked torrents from user profiles (Coming Soon).

## 📈 Coming Soon...
- **Advanced Torrent Management:** Bonus points, ratio tracking, and gamification.
- **Moderation & RBAC:** Content moderation and admin roles.
- **Real-Time Stats:** Integration with RRD or InfluxDB/Grafana.
- **Driver Support:** Download and create torrents from sources like GitHub.
- **API Improvements:** Enhanced endpoints for managing torrents and user data.

## 💻 Installation

1. Clone the repository:
   ```
   git clone https://github.com/pandamasta/bitiso-django.git
   cd django-bitiso
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Apply database migrations:
   ```
   python manage.py migrate
   ```
4. Start the server:
   ```
   python manage.py runserver
   ```

## 🌟 Contributing

Contributions are welcome!
- Help expand translations 🌍 (currently supporting EN & FR).
- Suggest or implement features like advanced stats, API endpoints, and more.
- Open an issue or submit a pull request to get started!

