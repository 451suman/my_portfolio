# Professional Developer Portfolio

A production-level Django portfolio website showcasing backend engineering skills with modern animated UI/UX. Built with Django REST Framework, WebSockets, and GSAP animations.

## 🚀 Features

### Backend Engineering
- **Custom User Model** with JWT authentication
- **Django REST Framework** with comprehensive API endpoints
- **Django Channels** for real-time WebSocket functionality
- **Role-based permissions** and security best practices
- **Email integration** with SMTP configuration
- **Database optimization** with indexes and query optimization

### Frontend & UI/UX
- **Dark gaming-inspired theme** (Fortnite-style)
- **Bootstrap 5.3** for responsive design
- **GSAP animations** for smooth 60fps interactions
- **Particle background** effects
- **Typing animations** and scroll-based reveals
- **Mobile-responsive** design

### Real-time Features
- **Live chat system** with WebSocket connections
- **Real-time notifications**
- **Online user tracking**
- **Message reactions** and typing indicators

## 📁 Project Architecture

```
portfolio_project/
├── accounts/          # Authentication & user profiles
├── core/              # Base utilities & frontend views
├── portfolio/         # Projects, skills, experience
├── blog/              # Blog posts & articles
├── contact/           # Contact form & email handling
├── realtime/          # WebSocket & real-time features
└── static/            # CSS, JS, images
```

### Module Purposes

- **accounts**: User authentication, profiles, JWT tokens
- **core**: Base models, frontend templates, utilities
- **portfolio**: Projects showcase, skills, work experience
- **blog**: Blog posts, categories, comments system
- **contact**: Contact forms, email notifications, newsletter
- **realtime**: WebSocket chat, notifications, online users

## 🛠️ Technology Stack

### Backend
- **Django 6.0.4** - Web framework
- **Django REST Framework** - API development
- **Django Channels** - WebSocket support
- **JWT Authentication** - Token-based auth
- **PostgreSQL** - Database (production)
- **Redis** - Channel layers & caching

### Frontend
- **Bootstrap 5.3** - UI framework
- **GSAP 3.12** - Animation library
- **Font Awesome 6.4** - Icons
- **Custom CSS** - Dark theme & animations

### Development Tools
- **Python 3.12** - Programming language
- **Virtual Environment** - Dependency isolation
- **Environment Variables** - Configuration management

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL (for production)
- Redis (for WebSocket support)
- Node.js (optional, for asset management)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd portfolio_project
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
# Create PostgreSQL database
createdb portfolio_db

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start Redis server**
```bash
redis-server
```

8. **Run the application**
```bash
python manage.py runserver
```

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=portfolio_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

## 🌐 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

### Main API Endpoints

#### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - User profile

#### Portfolio
- `GET /api/portfolio/projects/` - List projects
- `POST /api/portfolio/projects/` - Create project
- `GET /api/portfolio/skills/` - List skills
- `GET /api/portfolio/categories/` - List categories

#### Blog
- `GET /api/blog/posts/` - List blog posts
- `POST /api/blog/posts/` - Create blog post
- `GET /api/blog/categories/` - List categories

#### Contact
- `POST /api/contact/messages/` - Send contact message
- `POST /api/contact/newsletter/subscribe/` - Subscribe to newsletter

## 🎨 Frontend Features

### Animations
- **Hero Section**: Particle background, typing animation
- **Scroll Reveal**: Fade-in, slide-up, scale-in effects
- **Skill Bars**: Animated progress bars with shimmer effect
- **Card Hover**: Smooth scale and glow effects
- **Navigation**: Sticky navbar with scroll effects

### Responsive Design
- **Mobile-first** approach
- **Breakpoints**: 576px, 768px, 992px, 1200px
- **Touch-friendly** interactions
- **Optimized** for all screen sizes

## 🔄 WebSocket Features

### Real-time Chat
```javascript
// Connect to chat room
const chatSocket = new WebSocket('ws://localhost:8000/ws/chat/room-name/');

// Send message
chatSocket.send(JSON.stringify({
    'type': 'text',
    'content': 'Hello, world!'
}));
```

### Notifications
```javascript
// Connect to notifications
const notificationSocket = new WebSocket('ws://localhost:8000/ws/notifications/');
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test portfolio
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🚀 Deployment

### Production Setup

1. **Environment Setup**
```bash
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com
export DATABASE_URL=postgresql://user:pass@host:port/dbname
```

2. **Static Files**
```bash
python manage.py collectstatic
```

3. **Database Migrations**
```bash
python manage.py migrate
```

4. **Gunicorn Setup**
```bash
pip install gunicorn
gunicorn portfolio_project.wsgi:application --bind 0.0.0.0:8000
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "portfolio_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/portfolio_db
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: portfolio_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Cloud Deployment Options

#### Render
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

#### Railway
1. Import project from GitHub
2. Configure PostgreSQL add-on
3. Set Redis add-on for WebSocket support

#### AWS
1. Use EC2 for application server
2. RDS for PostgreSQL database
3. ElastiCache for Redis
4. S3 for static/media files
5. CloudFront for CDN

## 📊 Performance Optimization

### Database Optimization
- **Indexes** on frequently queried fields
- **select_related()** and **prefetch_related()** for query optimization
- **Database connection pooling**

### Caching
- **Redis** for session storage
- **View caching** for static content
- **API response caching**

### Frontend Optimization
- **Image optimization** and lazy loading
- **CSS/JS minification**
- **CDN** for static assets
- **Gzip compression**

## 🔒 Security Features

- **JWT authentication** with refresh tokens
- **CORS configuration** for API security
- **Input validation** and sanitization
- **SQL injection prevention** with Django ORM
- **XSS protection** with Django's built-in security
- **CSRF protection** for forms
- **Rate limiting** (can be added with django-ratelimit)

## 📈 Monitoring & Logging

### Django Logging
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Error Tracking
- **Sentry** integration (optional)
- **Custom error logging**
- **Performance monitoring**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run tests and ensure they pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django team for the amazing framework
- Bootstrap team for the UI components
- GSAP team for the animation library
- All contributors and supporters

---

**Built with ❤️ by [Your Name]**

For any questions or support, please reach out through the contact form or create an issue on GitHub.
