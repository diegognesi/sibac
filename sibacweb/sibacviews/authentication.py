# -*- coding: utf-8 -*-
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
import re


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {})
    elif request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        if not username:
            ctx = {"error_message": "Specificare il nome utente." }
        elif not password:
            ctx = {"error_message": "Specificare la password." }
        else:
            user = auth.authenticate(username=username, password=password)
            if user is None:
                ctx = {"error_message": "Tentativo di accesso fallito." }
            else:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect("/")
                else:
                    ctx = {"error_message": "L'utente è stato disabilitato. Contattare gli amministratori del sito per informazioni." }
        return render(request, 'login.html', ctx)
    else:
        raise Http404()

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html', {})
    elif request.method == 'POST':
        name = request.POST.get("name", "")
        surname = request.POST.get("surname", "")
        email = request.POST.get("email", "")
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        passwordrepeat = request.POST.get("passwordrepeat", "")
        ctx = None
        if not name:
            ctx = {"error_message": "Specificare il nome di battesimo." }
        if not surname:
            ctx = {"error_message": "Specificare il cognome." }
        if not username:
            ctx = {"error_message": "Specificare il nome utente." }
        elif len(username) < 3:
            ctx = {"Il nome utente deve essere composto di almeno 3 caratteri"}
        elif not password:
            ctx = {"error_message": "Specificare la password." }
        elif not re.match(r"^(?=.*\d)(?=.*\W)(?=.*[a-zA-Z]).{8,15}$", password):
            ctx = {"error_message": "La password deve avere tra gli 8 e i 15 caratteri, di cui almeno una lettera, un numero e un segno di punteggiatura." }
        elif password and passwordrepeat and not password == passwordrepeat:
            ctx = {"error_message": "Le password non coincidono." }
        else:
            try:
                validate_email( email )
            except ValidationError:
                ctx = {"error_message": "E-mail non valida." }
        if ctx is None:
            # No errors. Try to create the user.
            try:
                user = User.objects.create_user(username=username, password=password, email=email)
                user.first_name=name
                user.last_name=surname
                user.is_active=True
                user.save()
                return HttpResponseRedirect("user_registered")
            except:
                ctx = {"error_message": "Tentativo di creare l'utente fallito. Riprova o contatta gli amministratori del sito." }
        # If you are here, an error occurred.
        ctx["name"] = name
        ctx["surname"] = surname
        ctx["email"] = email
        ctx["username"] = username
        return render(request, 'register.html', ctx)
    else:
        raise Http404()

def user_registered(request):
    return render(request, 'user_registered.html', {})

@login_required
def change_password(request):
    if request.method == 'GET':
        return render(request, 'change_password.html', {})
    elif request.method == 'POST':
        oldpassword = request.POST.get("oldpassword", "")
        newpassword = request.POST.get("newpassword", "")
        newpasswordconfirm = request.POST.get("newpasswordconfirm", "")
        if not oldpassword:
            ctx = {"error_message": "Specificare la vecchia password."}
        elif not newpassword:
            ctx = {"error_message": "Specificare la nuova password."}
        elif not re.match(r"^(?=.*\d)(?=.*\W)(?=.*[a-zA-Z]).{8,15}$", newpassword):
            ctx = {"error_message": "La password deve avere tra gli 8 e i 15 caratteri, di cui almeno una lettera, un numero e un segno di punteggiatura." }
        elif not newpasswordconfirm:
            ctx = {"error_message": "La password deve essere digitata due volte."}
        elif newpassword and newpasswordconfirm and not newpassword == newpasswordconfirm:
            ctx = {"error_message": "Le password non coincidono."}
        elif not request.user.check_password(oldpassword):
            ctx = {"error_message": "Verifica della vecchia password fallita."}
        else:
            try:
                request.user.set_password(newpassword)
                request.user.save()
                ctx = {"success": True}
            except:
                ctx = {"error_message": "Tentativo di modificare la password fallito."}
        return render(request, 'change_password.html', ctx)
    else:
        raise Http404

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
         
