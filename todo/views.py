from django.db import IntegrityError  # Ошибка, если произошла попытка создать, существующего пользователя
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User  # Встроенный объект создания пользователя
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TodoForm
from .models import Todo


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):  # Создание нового пользователя
    if request.method == "GET":
        return render(request, "todo/signupuser.html", {"form": UserCreationForm()})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:  # Если пароли ровны, создаем пользователя, сохраняем и логиним его
                user = User.objects.create_user(username=request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)  # Логирование юзера
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, "todo/signupuser.html", {"form": UserCreationForm,
                                                                'error': "That username has already been taken."
                                                                         " Please, choose a new username"})
        else:
            return render(request, "todo/signupuser.html", {"form": UserCreationForm,
                                                            "error": "Password didn't match"})


def loginuser(request):  # Логирование пользователя
    if request.method == "GET":
        return render(request, "todo/loginuser.html", {"form": AuthenticationForm()})

    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, "todo/loginuser.html", {"form": AuthenticationForm(), 'error': "User or password "
                                                                                                  "didn't match"})
        else:
            login(request, user)
            return redirect('currenttodos')  # Перенаправление на ссылку по имени(name in path())


@login_required  # Проверяет зарегистрирован ли пользователь перед доступом к функции
def logoutuser(request):
    if request.method == 'POST':
        logout(request)  # Выход из сайта, встроенной функцией django
        return redirect('home')


@login_required  # Проверяет зарегистрирован ли пользователь перед доступом к функции
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, "todo/currenttodos.html", {'todos': todos})


@login_required  # Проверяет зарегистрирован ли пользователь перед доступом к функции
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, "todo/compleetedtodos.html", {'todos': todos})


@login_required
def createtodo(request):  # Создание самой задачи
    if request.method == 'GET':
        return render(request, "todo/createtodo.html", {"form": TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, "todo/createtodo.html", {"form": TodoForm(), 'error': "Bad data passed in"
                                                                                         "Try ad"})


@login_required
def viewtodo(request, todo_pk):  # Показываем отдельную задачу, принимая её id в аргументы
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)  # ИЗ Таблицы по ключу и пользователю
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, "todo/viewtodo.html", {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            form = TodoForm(instance=todo)
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': "Bad info"})


@login_required
def completetodo(request, todo_pk):  # Завершение задачи
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):  # Удаление задачи
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
