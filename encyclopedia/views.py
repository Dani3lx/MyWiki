from django.shortcuts import render
import markdown2
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util


class SearchForm(forms.Form):
    search = forms.CharField(label="", widget=forms.TextInput(attrs={'class':"search", 'type':"text", 'name':"q", 'placeholder':"Search Encyclopedia"}))

class CreateForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Markdown Content", widget=forms.Textarea(attrs={'placeholder':"Enter the markdown here"}))

class EditForm(forms.Form):
    field = forms.CharField(label="Content to edit", widget=forms.Textarea())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm
    })

def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["field"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("index"))
    else:
        prevcontent = util.get_entry(title)
        form = EditForm(initial={"field": prevcontent})
        return render(request, "encyclopedia/edit.html", {
            "field": form,
            "title": title
        })

def entry(request, title):

    result = util.get_entry(title)
    if result == None:
        return render(request, "encyclopedia/entry.html", {
            "content": "Requested page was not found.",
            "title": "ERROR",
            "form": SearchForm,
        })
    else:
        result = markdown2.markdown(result)
        return render(request, "encyclopedia/entry.html", {
            "content": result,
            "title": title,
            "form": SearchForm,
        })

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data["search"]
            result = util.get_entry(search)
            if result == None:
                lst = util.list_entries()
                filtered = filter(lambda query: search.casefold() in query.casefold(), lst)
                return render(request, "encyclopedia/index.html", {
                    "entries": filtered,
                    "form": SearchForm
                })
            else:
                result = markdown2.markdown(result)
                return render(request, "encyclopedia/entry.html", {
                    "content": result,
                    "title": search,
                    "form": SearchForm,
                })
    
    return render(request, "encyclopedia/search.html", {
        "form": SearchForm,
    })

def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in util.list_entries():
                return render(request, "encyclopedia/entry.html", {
                    "content": "This page already exist.",
                    "title": "ERROR",
                    "form": SearchForm,
                })                
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("index"))

    return render(request, "encyclopedia/create.html", {
        "textarea": CreateForm,
    })
