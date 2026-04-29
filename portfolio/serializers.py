from rest_framework import serializers
from .models import Category, Skill, Project, ProjectImage, Experience


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for project categories
    """
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'projects_count', 'created_at']

    def get_projects_count(self, obj):
        return obj.projects.count()


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for technical skills
    """
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'slug', 'category', 'proficiency_level',
            'icon', 'projects_count', 'created_at'
        ]

    def get_projects_count(self, obj):
        return obj.projects.count()


class ProjectImageSerializer(serializers.ModelSerializer):
    """
    Serializer for project images
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'image_url', 'caption', 'order', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProjectSerializer(serializers.ModelSerializer):
    """
    Base serializer for projects
    """
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    skills = SkillSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'status', 'featured', 'architecture_explanation', 'challenges_solved',
            'github_url', 'live_demo_url', 'project_url', 'cover_image_url',
            'owner', 'owner_name', 'category', 'category_name', 'skills', 'images',
            'start_date', 'end_date', 'duration', 'team_size', 'is_personal_project',
            'is_open_source', 'created_at', 'updated_at'
        ]
        read_only_fields = ['owner']

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_duration(self, obj):
        return obj.duration_months


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for project lists
    """
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    skills_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'short_description', 'status', 'featured',
            'cover_image_url', 'owner_name', 'category_name', 'skills_count',
            'start_date', 'end_date', 'created_at'
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.cover_image:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_skills_count(self, obj):
        return obj.skills.count()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating projects
    """
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'title', 'slug', 'description', 'short_description',
            'status', 'featured', 'architecture_explanation', 'challenges_solved',
            'github_url', 'live_demo_url', 'project_url', 'cover_image',
            'category', 'skills', 'start_date', 'end_date', 'team_size',
            'is_personal_project', 'is_open_source'
        ]

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        project = Project.objects.create(**validated_data)
        project.skills.set(skills_data)
        return project

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skills_data is not None:
            instance.skills.set(skills_data)
        
        return instance


class ExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for work experience
    """
    company_logo_url = serializers.SerializerMethodField()
    skills = SkillSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            'id', 'company', 'position', 'description', 'start_date',
            'end_date', 'is_current_job', 'company_logo_url', 'company_website',
            'skills', 'duration', 'created_at'
        ]

    def get_company_logo_url(self, obj):
        request = self.context.get('request')
        if request and obj.company_logo:
            return request.build_absolute_uri(obj.company_logo.url)
        return None

    def get_duration(self, obj):
        if obj.start_date:
            end_date = obj.end_date or timezone.now().date()
            return (end_date.year - obj.start_date.year) * 12 + \
                   (end_date.month - obj.start_date.month) + 1
        return None


class ExperienceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating experience
    """
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Experience
        fields = [
            'company', 'position', 'description', 'start_date', 'end_date',
            'is_current_job', 'company_logo', 'company_website', 'skills'
        ]

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        experience = Experience.objects.create(**validated_data)
        experience.skills.set(skills_data)
        return experience

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skills_data is not None:
            instance.skills.set(skills_data)
        
        return instance
