from django.utils.text import slugify


class SlugMixin:
    """Generate unique slug automatically."""

    def generate_unique_slug(self, model_class, slug_field='slug',
                             text_field='name'):
        """Generate unique slug for model."""
        if not getattr(self, slug_field):
            slug = slugify(getattr(self, text_field))
            original_slug = slug
            counter = 1

            while model_class.objects.filter(**{slug_field: slug}).exclude(
                    id=self.id).exists() and counter < 100:
                slug = f"{original_slug}_{counter}"
                counter += 1

            setattr(self, slug_field, slug)
