from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, User
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Register(forms.Form):
    text_box = forms.CharField(label='Introducir Nombres', max_length=100)
    text_box2 = forms.CharField(label='Introducir Apellidos', max_length=100)
    text_box3 = forms.IntegerField(label='Introducir Cédula')
    oculto = forms.IntegerField(widget=forms.HiddenInput(), required=False)

class Update(forms.Form):
    text_box = forms.IntegerField(label='Introducir Cédula')

class EnableDisable(forms.Form):
    text_box = forms.CharField(label='Introducir Nombres', max_length=100, widget=forms.HiddenInput())
    text_box2 = forms.CharField(label='Introducir Apellidos', max_length=100, widget=forms.HiddenInput())
    text_box3 = forms.IntegerField(label='Introducir Cédula', widget=forms.HiddenInput())
    estado = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    options = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[('1', 'Activar'), ('2', 'Desactivar')],
        initial='1',
        label='Seleccione opción'
    )

class ManageUsers(forms.Form):
    options = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[('1', 'Agregar'), ('2', 'Modificar'), ('3', 'Eliminar')],
        initial='1',
        label='Seleccione opción',
        
    )

# Formulario para crear nuevos usuarios
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

# Formulario para modificar usuarios existentes
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff')
    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        # Eliminar el campo de la contraseña para que no se renderice
        if 'password' in self.fields:
            del self.fields['password']
        self.fields['is_staff'].label = 'Usuario Administrador'
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("El nombre de usuario ya está en usooooo.")
        return username

class ChangeUserForm(forms.Form):
    select_field = forms.ChoiceField(label="Elige una opción")
