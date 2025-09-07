from django.utils.text import slugify


class SlugMixin:
    """Generate unique slug automatically.

    Provides functionality to generate unique slugs for model instances
    based on a text field, typically used for URL-friendly identifiers.
    """

    def generate_unique_slug(self, model_class, slug_field: str = 'slug',
                             text_field: str = 'name') -> None:
        """Generate unique slug for model.

        Args:
            model_class: Model class to check for existing slugs
            slug_field: Name of the slug field (default: 'slug')
            text_field: Name of the text field to generate slug from
        """
        if not getattr(self, slug_field):
            slug = slugify(getattr(self, text_field))
            original_slug = slug
            counter = 1

            # Get the object's ID if it exists (for existing objects)
            obj_id = getattr(self, 'id', None)

            while model_class.objects.filter(**{slug_field: slug}).exclude(
                    id=obj_id).exists() and counter < 100:
                slug = f"{original_slug}_{counter}"
                counter += 1

            setattr(self, slug_field, slug)
