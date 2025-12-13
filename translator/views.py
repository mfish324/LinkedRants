from django.shortcuts import render, get_object_or_404
from django.views.generic import View, DetailView
from django.http import JsonResponse
from django.conf import settings

from .models import Translation
from .services import translate


class TranslatorView(View):
    """Main translator tool page."""

    def get(self, request):
        return render(request, 'translator/translate.html', {
            'has_api_key': bool(settings.ANTHROPIC_API_KEY),
        })

    def post(self, request):
        text = request.POST.get('text', '').strip()
        mode = request.POST.get('mode', 'to_linkedin')

        if not text:
            return render(request, 'translator/translate.html', {
                'error': 'Please enter some text to translate.',
                'has_api_key': bool(settings.ANTHROPIC_API_KEY),
            })

        if not settings.ANTHROPIC_API_KEY:
            return render(request, 'translator/translate.html', {
                'error': 'API key not configured. Translation unavailable.',
                'has_api_key': False,
            })

        # Perform translation
        translated = translate(text, mode)

        # Save translation for sharing
        translation = Translation.objects.create(
            original_text=text,
            translated_text=translated,
            mode=mode,
        )

        context = {
            'original_text': text,
            'translated_text': translated,
            'mode': mode,
            'mode_display': 'Make it LinkedIn' if mode == 'to_linkedin' else 'Make it Real',
            'translation': translation,
            'has_api_key': True,
        }

        # For HTMX requests, return just the result partial
        if request.htmx:
            return render(request, 'translator/partials/result.html', context)

        return render(request, 'translator/translate.html', context)


class TranslateAPIView(View):
    """API endpoint for translations (for potential future use)."""

    def post(self, request):
        import json

        try:
            data = json.loads(request.body)
            text = data.get('text', '').strip()
            mode = data.get('mode', 'to_linkedin')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        if not settings.ANTHROPIC_API_KEY:
            return JsonResponse({'error': 'API not configured'}, status=503)

        translated = translate(text, mode)

        # Save for sharing
        translation = Translation.objects.create(
            original_text=text,
            translated_text=translated,
            mode=mode,
        )

        return JsonResponse({
            'original': text,
            'translated': translated,
            'mode': mode,
            'share_url': request.build_absolute_uri(translation.get_absolute_url()),
        })


class ShareView(DetailView):
    """View a shared translation."""
    model = Translation
    template_name = 'translator/share.html'
    context_object_name = 'translation'
    slug_field = 'share_slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode_display'] = (
            'Make it LinkedIn' if self.object.mode == 'to_linkedin'
            else 'Make it Real'
        )
        return context
