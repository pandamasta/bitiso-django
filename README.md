bitiso/
├── bitiso/                       # Core project files
│   ├── settings.py               # Updated with I18N settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── accounts/                     # User authentication and management
│   ├── models.py                 # Custom user model
│   ├── views.py                  # Registration, login, 2FA
│   ├── forms.py                  # User forms
│   ├── urls.py                   # Account URLs
│   ├── templates/                # Translatable templates
│   └── signals.py                # Account signals
├── torrents/                     # Torrent management
│   ├── models/                   # Models including translations
│   ├── views.py                  # Upload, search, management
│   ├── forms.py                  # Torrent forms
│   ├── filters.py                # Search and filtering logic
│   ├── urls.py                   # Torrent URLs
│   ├── templates/                # Translatable templates
├── user_profiles/                # User profiles and stats
│   ├── models.py                 # Profile models
│   ├── views.py                  # Profile views
│   ├── templates/                # Translatable templates
│   ├── urls.py                   # Profile URLs
├── moderation/                   # Moderation tools
│   ├── models.py                 # Moderation models
│   ├── views.py                  # Moderation views
│   ├── templates/                # Translatable templates
│   └── urls.py                   # Moderation URLs
├── pages/                        # Dynamic pages with I18N
│   ├── models.py                 # Page models with translations
│   ├── views.py                  # Page rendering
│   ├── templates/                # Translatable templates
│   └── urls.py                   # Page URLs
├── gpg/                          # GPG functionality
│   ├── models.py                 # GPG models
│   ├── views.py                  # Key management, signing
│   ├── services.py               # GPG logic
│   ├── forms.py                  # GPG forms
│   ├── templates/                # Translatable templates
│   └── urls.py                   # GPG URLs
├── locale/                       # Directory for translation files
├── static/                       # Static files
├── media/                        # Media files
└── manage.py                     # Django management script
