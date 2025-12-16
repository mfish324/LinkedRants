from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse_lazy

from .models import Category, Rant, SideBySide, GhostingStory, Reaction
from .forms import RantForm, SideBySideForm, GhostingStoryForm, ReportForm


class HomeView(ListView):
    """Homepage with feed of recent rants."""
    model = Rant
    template_name = 'rants/home.html'
    context_object_name = 'rants'
    paginate_by = 10

    def get_queryset(self):
        queryset = Rant.objects.filter(is_approved=True)

        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Sorting
        sort = self.request.GET.get('sort', 'recent')
        if sort == 'reactions':
            queryset = queryset.annotate(
                reaction_count=Count('reactions')
            ).order_by('-reaction_count', '-created_at')
        elif sort == 'featured':
            queryset = queryset.filter(is_featured=True).order_by('-created_at')
        else:  # recent
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort', 'recent')
        context['sidebysides'] = SideBySide.objects.filter(is_approved=True)[:5]
        context['reaction_types'] = Reaction.REACTION_TYPES
        context['reaction_labels'] = Reaction.REACTION_LABELS
        return context


class RantDetailView(DetailView):
    """Detail view for a single rant."""
    model = Rant
    template_name = 'rants/rant_detail.html'
    context_object_name = 'rant'

    def get_queryset(self):
        return Rant.objects.filter(is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reaction_types'] = Reaction.REACTION_TYPES
        context['reaction_labels'] = Reaction.REACTION_LABELS
        # Get user's reactions for this rant
        session_key = self.request.session.session_key
        if session_key:
            context['user_reactions'] = list(
                Reaction.objects.filter(
                    rant=self.object,
                    session_key=session_key
                ).values_list('reaction_type', flat=True)
            )
        else:
            context['user_reactions'] = []
        return context


class SideBySideDetailView(DetailView):
    """Detail view for a side-by-side comparison."""
    model = SideBySide
    template_name = 'rants/sidebyside_detail.html'
    context_object_name = 'sidebyside'

    def get_queryset(self):
        return SideBySide.objects.filter(is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reaction_types'] = Reaction.REACTION_TYPES
        context['reaction_labels'] = Reaction.REACTION_LABELS
        session_key = self.request.session.session_key
        if session_key:
            context['user_reactions'] = list(
                Reaction.objects.filter(
                    sidebyside=self.object,
                    session_key=session_key
                ).values_list('reaction_type', flat=True)
            )
        else:
            context['user_reactions'] = []
        return context


class RantCreateView(CreateView):
    """Create a new rant."""
    model = Rant
    form_class = RantForm
    template_name = 'rants/rant_form.html'
    success_url = reverse_lazy('rants:home')

    def form_valid(self, form):
        messages.success(self.request, 'Your rant has been posted!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Submit a Rant'
        return context


class SideBySideCreateView(CreateView):
    """Create a new side-by-side comparison."""
    model = SideBySide
    form_class = SideBySideForm
    template_name = 'rants/sidebyside_form.html'
    success_url = reverse_lazy('rants:home')

    def form_valid(self, form):
        messages.success(self.request, 'Your side-by-side has been posted!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Submit a Side-by-Side'
        return context


class CategoryView(ListView):
    """View rants in a specific category."""
    model = Rant
    template_name = 'rants/category.html'
    context_object_name = 'rants'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Rant.objects.filter(
            category=self.category,
            is_approved=True
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        context['reaction_types'] = Reaction.REACTION_TYPES
        context['reaction_labels'] = Reaction.REACTION_LABELS
        return context


class ReactView(View):
    """Handle reactions via HTMX."""

    def post(self, request, content_type, pk, reaction_type):
        # Ensure session exists
        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key

        # Validate reaction type
        valid_types = [code for code, _ in Reaction.REACTION_TYPES]
        if reaction_type not in valid_types:
            return HttpResponse(status=400)

        # Get content object
        if content_type == 'rant':
            content = get_object_or_404(Rant, pk=pk, is_approved=True)
            existing = Reaction.objects.filter(
                rant=content,
                session_key=session_key,
                reaction_type=reaction_type
            ).first()
        elif content_type == 'sidebyside':
            content = get_object_or_404(SideBySide, pk=pk, is_approved=True)
            existing = Reaction.objects.filter(
                sidebyside=content,
                session_key=session_key,
                reaction_type=reaction_type
            ).first()
        elif content_type == 'ghosting':
            content = get_object_or_404(GhostingStory, pk=pk, is_approved=True)
            existing = Reaction.objects.filter(
                ghosting_story=content,
                session_key=session_key,
                reaction_type=reaction_type
            ).first()
        else:
            return HttpResponse(status=400)

        # Toggle reaction
        if existing:
            existing.delete()
            is_active = False
        else:
            if content_type == 'rant':
                Reaction.objects.create(
                    rant=content,
                    session_key=session_key,
                    reaction_type=reaction_type
                )
            elif content_type == 'sidebyside':
                Reaction.objects.create(
                    sidebyside=content,
                    session_key=session_key,
                    reaction_type=reaction_type
                )
            else:  # ghosting
                Reaction.objects.create(
                    ghosting_story=content,
                    session_key=session_key,
                    reaction_type=reaction_type
                )
            is_active = True

        # Get updated counts
        reaction_counts = content.get_reaction_counts()

        # Return updated reaction button (HTMX partial)
        if request.htmx:
            return render(request, 'rants/partials/reaction_buttons.html', {
                'content': content,
                'content_type': content_type,
                'reaction_types': Reaction.REACTION_TYPES,
                'reaction_labels': Reaction.REACTION_LABELS,
                'reaction_counts': reaction_counts,
                'user_reactions': [reaction_type] if is_active else [],
            })

        return JsonResponse({
            'count': reaction_counts[reaction_type],
            'is_active': is_active,
        })


class ReportView(View):
    """Handle content reporting."""

    def post(self, request, content_type, pk):
        if content_type == 'rant':
            content = get_object_or_404(Rant, pk=pk)
        elif content_type == 'sidebyside':
            content = get_object_or_404(SideBySide, pk=pk)
        elif content_type == 'ghosting':
            content = get_object_or_404(GhostingStory, pk=pk)
        else:
            return HttpResponse(status=400)

        content.is_reported = True
        content.report_count += 1
        content.save()

        if request.htmx:
            return HttpResponse('<span class="text-gray-400">Reported</span>')

        messages.info(request, 'Content has been reported for review.')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class HallOfFameView(ListView):
    """Top rants of all time."""
    model = Rant
    template_name = 'rants/hall_of_fame.html'
    context_object_name = 'rants'
    paginate_by = 20

    def get_queryset(self):
        return Rant.objects.filter(is_approved=True).annotate(
            reaction_count=Count('reactions')
        ).order_by('-reaction_count', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reaction_types'] = Reaction.REACTION_TYPES
        context['reaction_labels'] = Reaction.REACTION_LABELS
        return context


class WallOfShameView(ListView):
    """Wall of Shame - ghosting recruiters."""
    model = GhostingStory
    template_name = 'rants/wall_of_shame.html'
    context_object_name = 'stories'
    paginate_by = 15

    def get_queryset(self):
        queryset = GhostingStory.objects.filter(is_approved=True)

        # Filter by company
        company = self.request.GET.get('company')
        if company:
            queryset = queryset.filter(company__icontains=company)

        # Filter by stage
        stage = self.request.GET.get('stage')
        if stage:
            queryset = queryset.filter(stage=stage)

        # Sorting
        sort = self.request.GET.get('sort', 'recent')
        if sort == 'reactions':
            queryset = queryset.annotate(
                reaction_count=Count('reactions')
            ).order_by('-reaction_count', '-created_at')
        elif sort == 'featured':
            queryset = queryset.filter(is_featured=True).order_by('-created_at')
        else:  # recent
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stage_choices'] = GhostingStory.STAGE_CHOICES
        context['current_stage'] = self.request.GET.get('stage', '')
        context['current_sort'] = self.request.GET.get('sort', 'recent')
        context['current_company'] = self.request.GET.get('company', '')
        context['reaction_types'] = Reaction.REACTION_TYPES
        context['reaction_labels'] = Reaction.REACTION_LABELS
        return context


class GhostingStoryDetailView(DetailView):
    """Detail view for a ghosting story."""
    model = GhostingStory
    template_name = 'rants/ghosting_detail.html'
    context_object_name = 'story'

    def get_queryset(self):
        return GhostingStory.objects.filter(is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reaction_types'] = Reaction.REACTION_TYPES
        context['reaction_labels'] = Reaction.REACTION_LABELS
        session_key = self.request.session.session_key
        if session_key:
            context['user_reactions'] = list(
                Reaction.objects.filter(
                    ghosting_story=self.object,
                    session_key=session_key
                ).values_list('reaction_type', flat=True)
            )
        else:
            context['user_reactions'] = []
        return context


class GhostingStoryCreateView(CreateView):
    """Submit a ghosting story to the Wall of Shame."""
    model = GhostingStory
    form_class = GhostingStoryForm
    template_name = 'rants/ghosting_form.html'
    success_url = reverse_lazy('rants:wall_of_shame')

    def form_valid(self, form):
        messages.success(self.request, 'Your story has been added to the Wall of Shame!')
        return super().form_valid(form)
