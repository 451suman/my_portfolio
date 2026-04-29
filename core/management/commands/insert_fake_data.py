from django.core.management.base import BaseCommand
from accounts.models import User
from blog.models import BlogPost, Category
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = "Insert fake data into the database"

    def handle(self, *args, **options):
        # Create superuser if not exists
        if not User.objects.filter(username="suman").exists():
            user = User.objects.create_user(
                username="suman",
                email="sumanmushyakhwo@gmail.com",
                password="admin123",
                first_name="Suman",
                last_name="Mushyakhwo",
            )
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS("Created superuser: suman"))
        else:
            user = User.objects.get(username="suman")
            self.stdout.write(self.style.SUCCESS("Superuser already exists: suman"))

        # Create categories if they don't exist
        categories_data = [
            {"name": "Django", "slug": "django"},
            {"name": "Python", "slug": "python"},
            {"name": "Web Development", "slug": "web-development"},
            {"name": "API Development", "slug": "api-development"},
            {"name": "Real-time Features", "slug": "real-time-features"},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data["slug"], defaults={"name": cat_data["name"]}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created category: {category.name}")
                )

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
                "author": user,
                "category": Category.objects.get(slug="django"),
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
                "author": user,
                "category": Category.objects.get(slug="real-time-features"),
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
                "author": user,
                "category": Category.objects.get(slug="django"),
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
                "author": user,
                "category": Category.objects.get(slug="python"),
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
                "author": user,
                "category": Category.objects.get(slug="web-development"),
            },
        ]

        for post_data in blog_posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=post_data["slug"], defaults=post_data
            )
            if created:
                post.published_at = datetime.now() - timedelta(
                    days=random.randint(1, 30)
                )
                post.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Created blog post: {post.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Blog post already exists: {post.title}")
                )

        self.stdout.write(
            self.style.SUCCESS("Fake data insertion completed successfully!")
        )
