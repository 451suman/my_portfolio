#!/usr/bin/env python
"""
Sample data creation script for the portfolio website.
Run this script to populate the database with sample data for testing.
"""

import os
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from portfolio.models import Category, Skill, Project, ProjectImage, Experience
from blog.models import Category as BlogCategory, Tag, BlogPost, Comment
from contact.models import ContactMessage, NewsletterSubscription
from realtime.models import ChatRoom, ChatMessage, Notification

User = get_user_model()

def create_sample_data():
    """Create sample data for testing the portfolio website."""
    
    print("Creating sample data...")
    
    # Create sample user if it doesn't exist
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User',
            'bio': 'Passionate backend developer with expertise in Django, Python, and modern web technologies.',
            'github_username': 'demodev',
            'linkedin_url': 'https://linkedin.com/in/demodev',
            'twitter_url': 'https://twitter.com/demodev',
            'website_url': 'https://demo.example.com',
            'location': 'San Francisco, CA',
            'is_developer': True
        }
    )
    
    if created:
        user.set_password('demo123')
        user.save()
        print(f"Created user: {user.username}")
    
    # Create portfolio categories
    portfolio_categories = [
        {'name': 'Web Development', 'description': 'Full-stack web applications'},
        {'name': 'Mobile Apps', 'description': 'Mobile application development'},
        {'name': 'API Development', 'description': 'RESTful APIs and microservices'},
        {'name': 'Data Science', 'description': 'Data analysis and machine learning'},
    ]
    
    for cat_data in portfolio_categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': cat_data['name'].lower().replace(' ', '-'),
                'description': cat_data['description']
            }
        )
        if created:
            print(f"Created portfolio category: {category.name}")
    
    # Create skills
    skills_data = [
        {'name': 'Python', 'category': 'Web Development', 'proficiency_level': 95},
        {'name': 'Django', 'category': 'Web Development', 'proficiency_level': 90},
        {'name': 'JavaScript', 'category': 'Web Development', 'proficiency_level': 85},
        {'name': 'React', 'category': 'Web Development', 'proficiency_level': 80},
        {'name': 'PostgreSQL', 'category': 'Web Development', 'proficiency_level': 88},
        {'name': 'Docker', 'category': 'Web Development', 'proficiency_level': 82},
        {'name': 'Redis', 'category': 'Web Development', 'proficiency_level': 75},
        {'name': 'AWS', 'category': 'Web Development', 'proficiency_level': 78},
        {'name': 'Swift', 'category': 'Mobile Apps', 'proficiency_level': 70},
        {'name': 'React Native', 'category': 'Mobile Apps', 'proficiency_level': 75},
    ]
    
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=skill_data['name'],
            defaults={
                'slug': skill_data['name'].lower().replace(' ', '-'),
                'category': skill_data['category'],
                'proficiency_level': skill_data['proficiency_level']
            }
        )
        if created:
            print(f"Created skill: {skill.name}")
    
    # Create sample projects
    web_dev_cat = Category.objects.get(name='Web Development')
    api_cat = Category.objects.get(name='API Development')
    
    projects_data = [
        {
            'title': 'E-commerce Platform',
            'slug': 'ecommerce-platform',
            'description': 'A full-featured e-commerce platform built with Django and React. Features include user authentication, product catalog, shopping cart, payment integration, and admin dashboard.',
            'short_description': 'Modern e-commerce platform with Django backend and React frontend.',
            'status': 'completed',
            'featured': True,
            'architecture_explanation': 'Built using Django REST Framework for the backend API, React for the frontend, PostgreSQL for the database, and Redis for caching. Implemented JWT authentication, Stripe payment integration, and real-time notifications.',
            'challenges_solved': 'Handled complex inventory management, implemented real-time stock updates, and optimized database queries for high-traffic scenarios.',
            'github_url': 'https://github.com/demodev/ecommerce-platform',
            'live_demo_url': 'https://demo-ecommerce.example.com',
            'category': web_dev_cat,
            'start_date': timezone.datetime(2023, 1, 1).date(),
            'end_date': timezone.datetime(2023, 6, 1).date(),
            'team_size': 3,
            'is_personal_project': False,
            'is_open_source': True
        },
        {
            'title': 'Task Management API',
            'slug': 'task-management-api',
            'description': 'RESTful API for task management with features like user authentication, project organization, task assignments, and real-time updates using WebSockets.',
            'short_description': 'Scalable task management API with real-time features.',
            'status': 'completed',
            'featured': False,
            'architecture_explanation': 'Built with Django REST Framework, using PostgreSQL for data storage, Redis for caching and session management, and Django Channels for real-time WebSocket connections.',
            'challenges_solved': 'Implemented efficient real-time updates, handled concurrent task modifications, and optimized database queries for large datasets.',
            'github_url': 'https://github.com/demodev/task-api',
            'category': api_cat,
            'start_date': timezone.datetime(2023, 7, 1).date(),
            'end_date': timezone.datetime(2023, 9, 1).date(),
            'team_size': 2,
            'is_personal_project': True,
            'is_open_source': True
        },
        {
            'title': 'Social Media Dashboard',
            'slug': 'social-media-dashboard',
            'description': 'Analytics dashboard for social media management with data visualization, scheduled posting, and engagement tracking.',
            'short_description': 'Comprehensive social media analytics and management tool.',
            'status': 'completed',
            'featured': True,
            'architecture_explanation': 'Django backend with REST API, React frontend with Chart.js for data visualization, PostgreSQL for data storage, and Celery for background tasks.',
            'challenges_solved': 'Handled large datasets, implemented efficient data aggregation, and created responsive charts for mobile devices.',
            'github_url': 'https://github.com/demodev/social-dashboard',
            'live_demo_url': 'https://demo-social.example.com',
            'category': web_dev_cat,
            'start_date': timezone.datetime(2023, 10, 1).date(),
            'end_date': timezone.datetime(2023, 12, 1).date(),
            'team_size': 4,
            'is_personal_project': False,
            'is_open_source': False
        }
    ]
    
    for proj_data in projects_data:
        project, created = Project.objects.get_or_create(
            slug=proj_data['slug'],
            defaults={
                **proj_data,
                'owner': user
            }
        )
        
        if created:
            # Add skills to project
            python_skill = Skill.objects.get(name='Python')
            django_skill = Skill.objects.get(name='Django')
            react_skill = Skill.objects.get(name='React')
            postgres_skill = Skill.objects.get(name='PostgreSQL')
            
            project.skills.add(python_skill, django_skill, react_skill, postgres_skill)
            print(f"Created project: {project.title}")
    
    # Create blog categories
    blog_categories = [
        {'name': 'Django', 'description': 'Django tutorials and tips', 'color': '#092E20'},
        {'name': 'Python', 'description': 'Python programming articles', 'color': '#3776AB'},
        {'name': 'Web Development', 'description': 'General web development topics', 'color': '#E34C26'},
        {'name': 'DevOps', 'description': 'DevOps and deployment guides', 'color': '#FF6B35'},
    ]
    
    for cat_data in blog_categories:
        category, created = BlogCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': cat_data['name'].lower(),
                'description': cat_data['description'],
                'color': cat_data['color']
            }
        )
        if created:
            print(f"Created blog category: {category.name}")
    
    # Create tags
    tags_data = ['Django', 'Python', 'REST API', 'JavaScript', 'React', 'PostgreSQL', 'Docker', 'AWS', 'Tutorial', 'Best Practices']
    
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': tag_name.lower().replace(' ', '-')}
        )
        if created:
            print(f"Created tag: {tag.name}")
    
    # Create sample blog posts
    django_cat = BlogCategory.objects.get(name='Django')
    python_cat = BlogCategory.objects.get(name='Python')
    
    blog_posts_data = [
        {
            'title': 'Building REST APIs with Django REST Framework',
            'slug': 'building-apis-with-drf',
            'content': '''# Building REST APIs with Django REST Framework

Django REST Framework (DRF) is a powerful toolkit for building Web APIs with Django. In this tutorial, we'll explore how to build a complete REST API from scratch.

## Getting Started

First, let's install DRF:

```bash
pip install djangorestframework
```

Add it to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
]
```

## Creating Serializers

Serializers convert complex data types to native Python datatypes...

## Creating Views

DRF provides various view classes to handle API endpoints...

## Conclusion

Building APIs with DRF is straightforward and powerful...''',
            'excerpt': 'Learn how to build robust REST APIs using Django REST Framework with this comprehensive tutorial.',
            'status': 'published',
            'featured': True,
            'category': django_cat,
            'estimated_reading_time': 8,
            'published_at': timezone.datetime(2023, 11, 15),
        },
        {
            'title': 'Advanced Python Tips and Tricks',
            'slug': 'advanced-python-tips',
            'content': '''# Advanced Python Tips and Tricks

Python is a powerful language with many advanced features. Let's explore some tips and tricks...

## List Comprehensions

List comprehensions provide a concise way to create lists:

```python
# Traditional way
squares = []
for i in range(10):
    squares.append(i * i)

# List comprehension
squares = [i * i for i in range(10)]
```

## Generators

Generators are memory-efficient for large datasets...

## Decorators

Decorators allow you to modify functions...

## Conclusion

These Python tips will help you write more efficient code...''',
            'excerpt': 'Discover advanced Python techniques that will make your code more efficient and Pythonic.',
            'status': 'published',
            'featured': False,
            'category': python_cat,
            'estimated_reading_time': 6,
            'published_at': timezone.datetime(2023, 12, 1),
        }
    ]
    
    for post_data in blog_posts_data:
        post, created = BlogPost.objects.get_or_create(
            slug=post_data['slug'],
            defaults={
                **post_data,
                'author': user
            }
        )
        
        if created:
            # Add tags to post
            django_tag = Tag.objects.get(name='Django')
            python_tag = Tag.objects.get(name='Python')
            api_tag = Tag.objects.get(name='REST API')
            
            post.tags.add(django_tag, python_tag, api_tag)
            print(f"Created blog post: {post.title}")
    
    # Create sample contact messages
    contact_messages = [
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Project Collaboration',
            'message': 'I\'m interested in collaborating on a Django project. Let\'s discuss details.',
            'inquiry_type': 'collaboration',
            'priority': 'medium'
        },
        {
            'name': 'Jane Smith',
            'email': 'jane@company.com',
            'subject': 'Job Opportunity',
            'message': 'We have a backend developer position that might be a good fit for you.',
            'inquiry_type': 'job_offer',
            'priority': 'high'
        }
    ]
    
    for msg_data in contact_messages:
        message, created = ContactMessage.objects.get_or_create(
            email=msg_data['email'],
            defaults=msg_data
        )
        if created:
            print(f"Created contact message: {message.subject}")
    
    # Create sample chat room
    chat_room, created = ChatRoom.objects.get_or_create(
        slug='general-chat',
        defaults={
            'name': 'General Chat',
            'description': 'General discussion room',
            'room_type': 'public',
            'created_by': user,
            'is_active': True
        }
    )
    
    if created:
        chat_room.participants.add(user)
        print(f"Created chat room: {chat_room.name}")
    
    # Create sample notifications
    notifications = [
        {
            'recipient': user,
            'sender': user,
            'notification_type': 'system',
            'title': 'Welcome!',
            'message': 'Welcome to the portfolio website! Feel free to explore all the features.'
        },
        {
            'recipient': user,
            'sender': user,
            'notification_type': 'contact',
            'title': 'New Contact Message',
            'message': 'You have received a new contact message from John Doe.'
        }
    ]
    
    for notif_data in notifications:
        notification, created = Notification.objects.get_or_create(
            title=notif_data['title'],
            defaults=notif_data
        )
        if created:
            print(f"Created notification: {notification.title}")
    
    print("Sample data creation completed!")
    print(f"Created {User.objects.count()} users")
    print(f"Created {Category.objects.count()} portfolio categories")
    print(f"Created {Skill.objects.count()} skills")
    print(f"Created {Project.objects.count()} projects")
    print(f"Created {BlogCategory.objects.count()} blog categories")
    print(f"Created {Tag.objects.count()} tags")
    print(f"Created {BlogPost.objects.count()} blog posts")
    print(f"Created {ContactMessage.objects.count()} contact messages")
    print(f"Created {ChatRoom.objects.count()} chat rooms")
    print(f"Created {Notification.objects.count()} notifications")

if __name__ == '__main__':
    create_sample_data()
