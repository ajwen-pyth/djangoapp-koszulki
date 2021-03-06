from django.views.generic import CreateView, ListView, DetailView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import get_template
from .forms import *
from .models import Tshirt, Story

# Create your views here.


class HomePageView(ListView):
    model = Tshirt
    template_name = 'index.html'

    def get_context_data(self):
        # Call the base implementation first to get a context
        context = super().get_context_data()
        # Add in a QuerySet of all the Tshirts, referable as num_shirts
        context['num_tshirts'] = Tshirt.objects.all().count()
        # queryset for all uniqe Tshirt items of the brand column
        context['num_brands'] = Tshirt.objects.values('brand').distinct().count()
        # this line below counts the number of existing stories
        context['num_stories'] = Story.objects.all().count()
        return context


class SearchResultsView(ListView):
    model = Tshirt
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Tshirt.objects.filter(
            Q(design__icontains=query) | Q(brand__icontains=query)
        )
        return object_list


class CreateTshirtView(LoginRequiredMixin, CreateView):
    model = Tshirt
    form_class = TshirtForm
    template_name = 'add_tshirt.html'
    success_url = reverse_lazy('index')

    
class UpdateTshirtView(UpdateView):
    model = Tshirt
    form_class = TshirtForm
    template_name = 'add_tshirt.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        tshirt = self.get_object()
        if self.request.user == tshirt.author:
            return True
        return False

class DeleteTshirtView(DeleteView):
    model = Tshirt
    success_url = reverse_lazy('index')

    def test_func(self):
        tshirt = self.get_object()
        if self.request.user == tshirt.author:
            return True
        return False

class CreateStoryView(LoginRequiredMixin, CreateView):

    """
    a sepearate view for adding story
    """
    model = Story
    form_class = StoryForm
    template_name = 'add_story.html'
    success_url = reverse_lazy('index')


class TshirtList(ListView):
    """
    Draws a list of all t-shirts from db.
    """
    model = Tshirt
    template_name = 'tshirt_list.html'
    ordering = ['-created']
    paginate_by = 5

    def get_context_data(self):
        context = super().get_context_data()
        context['tshirts'] = Tshirt.objects.all()
        return context


class TshirtDetail(TemplateView):
    """
    Creates a detailed view (all relevant objects, stories and t-shirt items) of a t-shirt from db.
    """
    # model = Tshirt
    context_object_name = "tshirt_detail"
    template_name = "tshirt_detail.html"
    # queryset = Tshirt.objects.all()


    # def get(self, request, pk):
    #     id = pk
    #     tshirt_items = get_object_or_404(Tshirt)
    #     story_items = Story.objects.filter(story=tshirt_items)
    #     return render(self.request, "tshirt_detail.html", {"tshirt": tshirt_items, "story": story_items})

    #
    # def get_queryset(self):
    #     # all_objects = tshirt_objects | story_objects
    #     return tshirt_items

    def get_context_data(self, **kwargs):
        context = super(TshirtDetail, self).get_context_data(**kwargs)
        context['tshirts'] = Tshirt.objects.all() # creates queryset of all Tshirt items referable as tshirts
        context['stories'] = Story.objects.all()
        return context


class BrandsList(ListView):
    model = Tshirt
    template_name = 'brand_list.html'
    ordering = ['-created']

    def get_context_data(self):
        context = super().get_context_data()
        context['brands'] = Tshirt.objects.values('brand').distinct()
        return context


class StoryList(ListView):
    """
    Draws a list of all stories from db.
    """
    model = Story
    template_name = 'story_list.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['stories'] = Story.objects.all()
        return context


class StoryDetail(DetailView):
    """
    Pulls a detailed view (content) of a story from db.
    """
    model = Story
    template_name = "story_detail.html"

    def get_queryset(self):
        return Story.objects

"""Contact form-view"""
def Contact(request):
    Contact_Form = ContactForm
    if request.method == 'POST':
        form = Contact_Form(data=request.POST)

        if form.is_valid():
            contact_name = request.POST.get('contact_name')
            contact_email = request.POST.get('contact_email')
            contact_content = request.POST.get('content')

        template = get_template('contact_form.txt')

        content = {
            'contact_name': contact_name,
            'contact_email': contact_email,
            'contact_content': contact_content
        }

        content = template.render(content)

        email = EmailMessage(
            "New contact form",
            content,
            "KoszulkiApp" + '',
            ['koszulkistore@gmail.com'],
            headers= {'Reply to': contact_email}
        )

        email.send()

        return redirect('index')


    return render(request, 'contact.html', {'form': Contact_Form})