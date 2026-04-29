from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from portfolio.models import Experience, Skill
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Add professional experience data from CV to database'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get the superuser
                user = User.objects.get(is_superuser=True)
                self.stdout.write(f'Adding experience for user: {user.username}')

                # Ensure required skills exist
                self._create_required_skills()

                # Professional experience data
                experiences_data = [
                    {
                        'company': 'Tech Solutions Inc.',
                        'position': 'Junior Backend Developer',
                        'description': 'Developed and maintained RESTful APIs using Django REST Framework. Implemented authentication systems, database optimizations, and integrated third-party services. Collaborated with frontend team to ensure seamless API integration and participated in code reviews and agile development processes.',
                        'start_date': date(2023, 6, 1),
                        'end_date': date(2024, 3, 31),
                        'is_current_job': False,
                        'company_website': 'https://techsolutions.example.com',
                        'skills': ['Python', 'Django', 'Django REST Framework', 'PostgreSQL', 'Git', 'REST APIs']
                    },
                    {
                        'company': 'Digital Innovations Ltd.',
                        'position': 'Backend Development Intern',
                        'description': 'Assisted in developing web applications using Django and Python. Created database models, implemented business logic, and wrote unit tests. Gained experience in version control, agile methodologies, and collaborative development. Contributed to bug fixes and feature implementation in production applications.',
                        'start_date': date(2023, 1, 15),
                        'end_date': date(2023, 5, 31),
                        'is_current_job': False,
                        'company_website': 'https://digitalinnovations.example.com',
                        'skills': ['Python', 'Django', 'MySQL', 'Git', 'Unit Testing', 'Agile']
                    },
                    {
                        'company': 'Freelance',
                        'position': 'Full Stack Developer',
                        'description': 'Developed custom web applications for small businesses and startups. Managed entire project lifecycle from requirements gathering to deployment. Implemented responsive designs, database architecture, and API integrations. Maintained client relationships and delivered projects on time and within budget.',
                        'start_date': date(2022, 9, 1),
                        'end_date': date(2022, 12, 31),
                        'is_current_job': False,
                        'company_website': '',
                        'skills': ['Python', 'Django', 'JavaScript', 'HTML/CSS', 'PostgreSQL', 'Project Management']
                    }
                ]

                # Add experiences
                for exp_data in experiences_data:
                    experience, created = Experience.objects.get_or_create(
                        user=user,
                        company=exp_data['company'],
                        position=exp_data['position'],
                        defaults={
                            'description': exp_data['description'],
                            'start_date': exp_data['start_date'],
                            'end_date': exp_data['end_date'],
                            'is_current_job': exp_data['is_current_job'],
                            'company_website': exp_data['company_website'],
                        }
                    )
                    
                    if created:
                        # Add skills to the experience
                        for skill_name in exp_data['skills']:
                            try:
                                skill = Skill.objects.get(name=skill_name)
                                experience.skills_used.add(skill)
                            except Skill.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f'Skill "{skill_name}" not found, skipping...'))
                        
                        self.stdout.write(self.style.SUCCESS(f'✓ Added experience: {experience.position} at {experience.company}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Experience already exists: {experience.position} at {experience.company}'))

                # Verify the data was added
                total_experiences = Experience.objects.filter(user=user).count()
                self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully added {total_experiences} professional experience entries'))
                
                # Display summary
                self.stdout.write('\n📋 Experience Summary:')
                for exp in Experience.objects.filter(user=user).order_by('-start_date'):
                    duration = self._calculate_duration(exp.start_date, exp.end_date)
                    current_marker = " (Current)" if exp.is_current_job else ""
                    self.stdout.write(f'  • {exp.position} at {exp.company} - {duration}{current_marker}')

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ No superuser found. Please create a superuser first.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error adding experience data: {str(e)}'))

    def _create_required_skills(self):
        """Create required skills if they don't exist"""
        required_skills = [
            ('Python', 'backend', 85, 'fab fa-python'),
            ('Django', 'backend', 80, 'fas fa-code'),
            ('Django REST Framework', 'backend', 75, 'fas fa-code-branch'),
            ('PostgreSQL', 'database', 70, 'fas fa-database'),
            ('MySQL', 'database', 65, 'fas fa-database'),
            ('Git', 'other', 80, 'fab fa-git-alt'),
            ('REST APIs', 'backend', 75, 'fas fa-exchange-alt'),
            ('Unit Testing', 'other', 70, 'fas fa-vial'),
            ('Agile', 'other', 75, 'fas fa-users'),
            ('JavaScript', 'frontend', 60, 'fab fa-js'),
            ('HTML/CSS', 'frontend', 70, 'fab fa-html5'),
            ('Project Management', 'other', 65, 'fas fa-tasks'),
        ]

        for name, category, proficiency, icon in required_skills:
            skill, created = Skill.objects.get_or_create(
                name=name,
                defaults={
                    'slug': name.lower().replace(' ', '-').replace('/', '-'),
                    'category': category,
                    'proficiency_level': proficiency,
                    'icon': icon,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created skill: {name}'))

    def _calculate_duration(self, start_date, end_date):
        """Calculate human-readable duration"""
        if not end_date:
            end_date = date.today()
        
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        years = months // 12
        remaining_months = months % 12
        
        if years > 0 and remaining_months > 0:
            return f"{years} year{'s' if years > 1 else ''}, {remaining_months} month{'s' if remaining_months > 1 else ''}"
        elif years > 0:
            return f"{years} year{'s' if years > 1 else ''}"
        else:
            return f"{months} month{'s' if months > 1 else ''}"
