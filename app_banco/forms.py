from django import forms
from .models import Cliente
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ('last_login'\
                       ,'is_superuser'\
                       ,'last_name'\
                       ,'email'\
                       ,'is_staff'\
                       ,'is_active'\
                       ,'date_joined'\
                       ,'first_name'\
                       ,'groups'\
                       ,'user_permissions'\
                       ,)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'type':'password'})

        }



class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        exclude = ('user',)
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        