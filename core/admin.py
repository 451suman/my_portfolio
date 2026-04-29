from django.contrib import admin

# The core app only contains abstract models (TimeStampedModel, SoftDeleteModel)
# which don't need to be registered with the admin interface.
# This file is kept for consistency with other apps.
