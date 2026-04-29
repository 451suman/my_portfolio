#!/usr/bin/env python
import os
import django
import sys

# Add the project path
sys.path.append("/media/suman/django/try_windsurf")

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio_project.settings")
django.setup()

from accounts.models import User
from blog.models import BlogPost, Category
from datetime import datetime, timedelta
import random


def insert_fake_data():
    # Get or create user
    user, created = User.objects.get_or_create(
        username="suman",
        defaults={
            "email": "sumanmushyakhwo@gmail.com",
            "first_name": "Suman",
            "last_name": "Mushyakhwo",
        },
    )
    if created:
        user.set_password("admin123")
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Created superuser: {user.username}")
    else:
        print(f"User already exists: {user.username}")

    # Get existing categories
    categories = Category.objects.all()
    if not categories.exists():
        print("No categories found!")
        return

    print(f"Found {categories.count()} categories")

    # Create fake blog posts
    blog_posts_data = [
        {
            "title": "Building Scalable APIs with Django REST Framework",
            "slug": "building-scalable-apis-django-rest-framework",
            "content": """In this comprehensive guide, we'll explore how to build scalable APIs using Django REST Framework. We'll cover best practices for API design, authentication, pagination, and performance optimization.

Django REST Framework provides powerful tools for building web APIs, including:
- Serializers for data validation and conversion
- ViewSets for organizing API logic
- Authentication and permission systems
- Pagination for large datasets
- Throttling and rate limiting

Let's dive deep into each of these topics and learn how to build production-ready APIs.""",
            "excerpt": "Learn how to build scalable APIs using Django REST Framework with best practices for performance and security.",
            "status": "published",
            "category_name": "Django",
        },
        {
            "title": "Implementing Real-time Features with Django Channels",
            "slug": "implementing-real-time-features-django-channels",
            "content": """Real-time features are essential for modern web applications. Django Channels extends Django to handle WebSockets, chat protocols, IoT protocols, and more.

In this tutorial, we'll cover:
- Setting up Django Channels
- Creating WebSocket consumers
- Building a real-time chat application
- Handling authentication with WebSockets
- Deploying Channels applications

Real-time communication opens up possibilities for live notifications, collaborative editing, gaming, and much more.""",
            "excerpt": "Discover how to implement real-time features in Django using Channels for WebSocket communication.",
            "status": "published",
            "category_name": "Web Development",
        },
        {
            "title": "Advanced Django ORM Techniques",
            "slug": "advanced-django-orm-techniques",
            "content": """The Django ORM is powerful, but many developers only scratch the surface of its capabilities. This article explores advanced techniques for optimizing database queries.

Topics covered:
- Query optimization strategies
- Using select_related and prefetch_related
- Database aggregation and annotation
- Raw SQL integration
- Database routing for multi-database setups

Master these techniques to build high-performance Django applications.""",
            "excerpt": "Master advanced Django ORM techniques for optimal database performance and query efficiency.",
            "status": "published",
            "category_name": "Django",
        },
        {
            "title": "Python Best Practices for Clean Code",
            "slug": "python-best-practices-clean-code",
            "content": """Writing clean, maintainable code is crucial for long-term project success. This article covers Python best practices that every developer should know.

Key topics:
- PEP 8 and code formatting
- Naming conventions and readability
- Function and class design principles
- Error handling and logging
- Testing strategies
- Documentation practices

Clean code leads to better collaboration, easier maintenance, and fewer bugs.""",
            "excerpt": "Learn Python best practices for writing clean, maintainable, and professional code.",
            "status": "published",
            "category_name": "Python",
        },
        {
            "title": "Modern Web Development with Django",
            "slug": "modern-web-development-django",
            "content": """Django has evolved significantly over the years. This article explores modern Django development practices and the ecosystem around it.

We'll cover:
- Django 4.x features and improvements
- Integration with modern frontend frameworks
- API-first development approaches
- Docker and deployment strategies
- Performance optimization techniques
- Security best practices

Stay up-to-date with the latest Django development trends and tools.""",
            "excerpt": "Explore modern Django development practices, tools, and ecosystem for building cutting-edge web applications.",
            "status": "published",
            "category_name": "Web Development",
        },
    ]

    for post_data in blog_posts_data:
        # Find the category by name
        try:
            category = Category.objects.get(name=post_data["category_name"])
        except Category.DoesNotExist:
            print(f"Category '{post_data['category_name']}' not found, skipping post")
            continue

        # Create or update the blog post
        post, created = BlogPost.objects.get_or_create(
            slug=post_data["slug"],
            defaults={
                "title": post_data["title"],
                "content": post_data["content"],
                "excerpt": post_data["excerpt"],
                "status": post_data["status"],
                "author": user,
                "category": category,
            },
        )

        if created:
            # Set published date to a random date in the past 30 days
            post.published_at = datetime.now() - timedelta(days=random.randint(1, 30))
            post.save()
            print(f"Created blog post: {post.title}")
        else:
            # Update existing post to ensure it has an author
            if not post.author:
                post.author = user
                post.save()
            print(f"Blog post already exists: {post.title}")

    print("Fake data insertion completed successfully!")


if __name__ == "__main__":
    insert_fake_data()
