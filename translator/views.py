from django.shortcuts import render, get_object_or_404
from django.views.generic import View, DetailView
from django.http import JsonResponse

from .models import Translation
from .services import translate
from .providers import get_enabled_providers


class TranslatorView(View):
    """Main translator tool page."""

    def get(self, request):
        providers = get_enabled_providers()
        return render(request, 'translator/translate.html', {
            'has_api_key': len(providers) > 0,
        })

    def post(self, request):
        text = request.POST.get('text', '').strip()
        mode = request.POST.get('mode', 'to_linkedin')
        providers = get_enabled_providers()

        if not text:
            return render(request, 'translator/translate.html', {
                'error': 'Please enter some text to translate.',
                'has_api_key': len(providers) > 0,
            })

        if not providers:
            return render(request, 'translator/translate.html', {
                'error': 'No AI providers configured. Translation unavailable.',
                'has_api_key': False,
            })

        try:
            # Perform translation - now returns a dict
            result = translate(text, mode)
            translated_text = result['translation']
            provider_name = result['provider_name']

            # Save translation for sharing
            translation = Translation.objects.create(
                original_text=text,
                translated_text=translated_text,
                mode=mode,
            )

            context = {
                'original_text': text,
                'translated_text': translated_text,
                'mode': mode,
                'mode_display': 'Make it LinkedIn' if mode == 'to_linkedin' else 'Make it Real',
                'translation': translation,
                'has_api_key': True,
                'powered_by': provider_name,
            }

        except Exception as e:
            context = {
                'original_text': text,
                'translated_text': f"Translation failed: {str(e)}",
                'mode': mode,
                'has_api_key': True,
                'error': str(e),
            }

        # For HTMX requests, return just the result partial
        if request.htmx:
            return render(request, 'translator/partials/result.html', context)

        return render(request, 'translator/translate.html', context)


class TranslateAPIView(View):
    """API endpoint for translations."""

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

        providers = get_enabled_providers()
        if not providers:
            return JsonResponse({'error': 'No AI providers configured'}, status=503)

        try:
            result = translate(text, mode)

            # Save for sharing
            translation = Translation.objects.create(
                original_text=text,
                translated_text=result['translation'],
                mode=mode,
            )

            return JsonResponse({
                'original': text,
                'translated': result['translation'],
                'mode': mode,
                'powered_by': result['provider_name'],
                'share_url': request.build_absolute_uri(translation.get_absolute_url()),
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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
