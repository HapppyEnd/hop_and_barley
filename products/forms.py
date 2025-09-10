from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model

from products.models import Review

User = get_user_model()


class ReviewForm(forms.ModelForm):
    """Form for creating and editing product reviews."""

    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': settings.TITLE_PLACEHOLDER,
                'maxlength': '100'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': settings.COMMENT_PLACEHOLDER,
                'rows': 4
            })
        }
        labels = {
            'rating': settings.RATING_LABEL,
            'title': settings.TITLE_LABEL,
            'comment': settings.COMMENT_LABEL
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """Validate that user can review this product."""
        cleaned_data = super().clean()

        # Get user from form context or request_user (for admin)
        user = getattr(self, 'request_user', None) or self.user

        # Skip validation if no user or product (admin case)
        if not user or not self.product:
            return cleaned_data

        # Debug information
        print(f"User: {user}, is_staff: {user.is_staff}, "
              f"can_review: {self.product.user_can_review(user)}")

        # Allow admins to review any product
        if not user.is_staff and not self.product.user_can_review(user):
            raise forms.ValidationError(settings.REVIEW_DELIVERY_REQUIRED)

        return cleaned_data
