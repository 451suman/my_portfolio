#!/usr/bin/env python
import os
import django
from django.conf import settings
from django.core.files.base import ContentFile
from portfolio.models import Project

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')
django.setup()

def add_sample_project_images():
    """Add sample cover images to projects that don't have them"""
    
    # Create sample image data (simple colored rectangles)
    sample_images = {
        'social-media-dashboard': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82',
        'ecommerce-platform': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82',
        'task-management-api': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82',
    }
    
    projects = Project.objects.all()
    updated_count = 0
    
    for project in projects:
        if not project.cover_image:
            # Use a simple 1x1 PNG as placeholder
            image_data = sample_images.get(project.slug.replace('-', '_'), 
                                         sample_images['social-media-dashboard'])
            
            # Create a simple filename based on project title
            filename = f"{project.slug.replace('-', '_')}_cover.png"
            
            # Save the image
            project.cover_image.save(filename, ContentFile(image_data), save=True)
            updated_count += 1
            print(f"Added cover image for: {project.title}")
    
    print(f"\nTotal projects updated: {updated_count}")

if __name__ == '__main__':
    add_sample_project_images()
