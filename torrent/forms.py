from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label="Search", max_length=100, min_length=2)

    def clean_query(self):
        query = self.cleaned_data.get('query')
        if len(query) < 2:
            raise forms.ValidationError("La recherche doit contenir au moins 2 caractères.")
        return query