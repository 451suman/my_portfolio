from rest_framework import serializers
from .models import Category, Tag, BlogPost, Comment


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for blog categories
    """
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color', 'posts_count', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for blog tags
    """
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'posts_count', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for blog comments
    """
    author_name = serializers.CharField(read_only=True)
    replies = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'author_name', 'author_email', 'author_website',
            'content', 'parent', 'replies', 'is_approved', 'created_at'
        ]
        read_only_fields = ['author', 'is_approved']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []

    def create(self, validated_data):
        request = self.context.get('request')
        
        # If user is authenticated, set author
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
            validated_data['author_name'] = request.user.get_full_name() or request.user.username
            validated_data['author_email'] = request.user.email
        
        return super().create(validated_data)


class BlogPostSerializer(serializers.ModelSerializer):
    """
    Base serializer for blog posts
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'author', 'author_name', 'content',
            'excerpt', 'featured_image', 'featured_image_url', 'category',
            'category_name', 'tags', 'status', 'featured',
            'estimated_reading_time', 'reading_time', 'meta_title',
            'meta_description', 'meta_keywords', 'published_at',
            'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'published_at']

    def get_featured_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.featured_image:
            return request.build_absolute_uri(obj.featured_image.url)
        return None

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_reading_time(self, obj):
        return obj.estimated_reading_time


class BlogPostListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for blog post lists
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image_url',
            'author_name', 'category_name', 'tags_count', 'featured',
            'published_at', 'reading_time'
        ]

    def get_featured_image_url(self, obj):
        request = self.context.get('request')
        if request and obj.featured_image:
            return request.build_absolute_uri(obj.featured_image.url)
        return None

    def get_tags_count(self, obj):
        return obj.tags.count()


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating blog posts
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'category', 'tags', 'status', 'featured',
            'estimated_reading_time', 'meta_title', 'meta_description',
            'meta_keywords'
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = BlogPost.objects.create(**validated_data)
        post.tags.set(tags_data)
        return post

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags_data is not None:
            instance.tags.set(tags_data)
        
        return instance
