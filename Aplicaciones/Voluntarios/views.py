from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404,JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Voluntario, Actividad, Inscripcion
from django.contrib.auth import login, logout
from .forms import RegistroAdminForm, LoginForm
from django.core.mail import send_mail
from django.conf import settings
            
def registrar_admin(request):
    if request.method == 'POST':
        form = RegistroAdminForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password1'])  # 🔑 hash correcto
            usuario.is_staff = True
            usuario.is_superuser = True
            usuario.save()
            return redirect('login')
    else:
        form = RegistroAdminForm()
    return render(request, 'registrar_admin.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def index(request):
    context = {
        'total_voluntarios': Voluntario.objects.count(),
        'total_actividades': Actividad.objects.count(),
        'total_inscripciones': Inscripcion.objects.count()
    }
    return render(request, 'index.html', context)

@login_required
def VoluntarioIndex(request):
    voluntarios = Voluntario.objects.all()
    return render(request, 'VoluntarioIndex.html', {'voluntarios': voluntarios})

@login_required
def nuevoVoluntario(request):
    return render(request, 'nuevoVoluntario.html')


@login_required
def guardarVoluntario(request):
    Voluntario.objects.create(
        cedula=request.POST['cedula'],
        nombres=request.POST['nombres'],
        apellidos=request.POST['apellidos'],
        email=request.POST['email'],
        telefono=request.POST['telefono'],
        direccion=request.POST.get('direccion')  
    )
    messages.success(request, 'Voluntario registrado correctamente')
    return redirect('/VoluntarioIndex')

@login_required
def editarVoluntario(request, id):
    voluntario = Voluntario.objects.get(id=id)
    return render(request, 'editarVoluntario.html', {'voluntario': voluntario})

@login_required
def actualizarVoluntario(request):
    if request.method == 'POST':
        voluntario_id = request.POST.get('voluntario_id')
        voluntario = get_object_or_404(Voluntario, id=voluntario_id)

        cedula = request.POST.get('cedula')
        email = request.POST.get('email')

        # Validar cédula duplicada (excepto el mismo registro)
        if Voluntario.objects.exclude(id=voluntario.id).filter(cedula=cedula).exists():
            messages.error(request, "Esta cédula ya está registrada")
            return redirect('editarVoluntario', id=voluntario.id)

        # Validar email duplicado (excepto el mismo registro)
        if Voluntario.objects.exclude(id=voluntario.id).filter(email=email).exists():
            messages.error(request, "Este email ya está registrado")
            return redirect('editarVoluntario', id=voluntario.id)

        # Actualizar campos
        voluntario.cedula = cedula
        voluntario.nombres = request.POST.get('nombres')
        voluntario.apellidos = request.POST.get('apellidos')
        voluntario.email = email
        voluntario.telefono = request.POST.get('telefono')
        voluntario.direccion = request.POST.get('direccion')

        voluntario.save()
        messages.success(request, "Voluntario actualizado correctamente")
        return redirect('VoluntarioIndex')

    return redirect('VoluntarioIndex')

@login_required
def eliminarVoluntario(request, id):
    Voluntario.objects.get(id=id).delete()
    messages.success(request, 'Voluntario eliminado')
    return redirect('/VoluntarioIndex')

@login_required
def ActividadIndex(request):
    actividades = Actividad.objects.all()
    return render(request, 'ActividadIndex.html', {'actividades': actividades})

@login_required
def nuevaActividad(request):
    return render(request, 'nuevaActividad.html')

@login_required
def guardarActividad(request):
    if request.method == 'POST':
        Actividad.objects.create(
            titulo=request.POST.get('titulo'),
            descripcion=request.POST.get('descripcion'),
            fecha=request.POST.get('fecha'),
            hora=request.POST.get('hora'),  # puede venir vacío
            lugar=request.POST.get('lugar'),
            cupo_maximo=request.POST.get('cupo_maximo'),
            imagen=request.FILES.get('imagen'),
            activa=True
        )
        messages.success(request, 'Actividad registrada correctamente')
        return redirect('/ActividadIndex')

@login_required
def editarActividad(request, id):
    actividad = Actividad.objects.get(id=id)
    return render(request, 'editarActividad.html', {'actividad': actividad})

@login_required
def actualizarActividad(request):
    actividad = Actividad.objects.get(id=request.POST['id'])
    actividad.titulo = request.POST['titulo']
    actividad.descripcion = request.POST['descripcion']
    actividad.fecha = request.POST['fecha']
    actividad.cupo_maximo = request.POST['cupo_maximo']
    imagen = request.FILES.get('imagen')
    if imagen:
        actividad.imagen = imagen
    actividad.save()
    messages.success(request, 'Actividad actualizada correctamente')
    return redirect('/ActividadIndex')

@login_required
def eliminarActividad(request, id):
    Actividad.objects.get(id=id).delete()
    messages.success(request, 'Actividad eliminada correctamente')
    return redirect('/ActividadIndex')


@login_required
def InscripcionIndex(request):
    inscripciones = Inscripcion.objects.all()

    # ⚠️ NO acceder a .url directamente si no hay archivo
    for i in inscripciones:
        if i.documento_compromiso:
            print(i.documento_compromiso.url)
        else:
            print("Sin documento")

    return render(request, 'InscripcionIndex.html', {
        'inscripciones': inscripciones
    })

@login_required
def nuevaInscripcion(request):
    voluntarios = Voluntario.objects.all()
    actividades = Actividad.objects.all()
    return render(request, 'nuevaInscripcion.html', {
        'voluntarios': voluntarios,
        'actividades': actividades
    })

@login_required
def guardarInscripcion(request):
    if request.method == 'POST':
        voluntario_id = request.POST.get('voluntario')
        actividad_id = request.POST.get('actividad')
        documento_compromiso = request.FILES.get('documento_compromiso')

        voluntario = get_object_or_404(Voluntario, id=voluntario_id)
        actividad = get_object_or_404(Actividad, id=actividad_id)

        # Validar duplicado
        if Inscripcion.objects.filter(voluntario=voluntario, actividad=actividad).exists():
            messages.error(request, 'Este voluntario ya está inscrito en esta actividad')
            return redirect('/InscripcionIndex')

        # ======== CREAR INSCRIPCIÓN =========
        inscripcion = Inscripcion.objects.create(
            voluntario=voluntario,
            actividad=actividad,
            documento_compromiso=documento_compromiso,
            estado='INSCRITO'
        )

        # ======== ENVIAR CORREO =========
        try:
            send_mail(
                subject='Confirmación de inscripción',
                message=f'''
Hola {voluntario.nombres} {voluntario.apellidos},

Tu inscripción se realizó correctamente.

Actividad: {actividad.titulo}
Fecha: {actividad.fecha}
Hora: {actividad.hora}
Lugar: {actividad.lugar}

Gracias por ser parte del voluntariado.
''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[voluntario.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            # Log the error but don't fail the inscription
            print(f"Error sending email: {e}")
            email_sent = False

        if email_sent:
            messages.success(request, 'Inscripción realizada correctamente y correo enviado')
        else:
            messages.success(request, 'Inscripción realizada correctamente (no se pudo enviar el correo)')
        return redirect('/InscripcionIndex')


@login_required
def editarInscripcion(request, id):
    inscripcion = get_object_or_404(Inscripcion, id=id)
    voluntarios = Voluntario.objects.all()
    actividades = Actividad.objects.all()
    return render(request, 'editarInscripcion.html', {
        'inscripcion': inscripcion,
        'voluntarios': voluntarios,
        'actividades': actividades
    })


@login_required
def actualizarInscripcion(request):
    if request.method == 'POST':
        inscripcion = get_object_or_404(Inscripcion, id=request.POST['id'])

        voluntario_id = request.POST['voluntario']
        actividad_id = request.POST['actividad']

        # 🔹 Guardar correo anterior
        correo_anterior = inscripcion.voluntario.email

        # Validar duplicado
        if Inscripcion.objects.exclude(id=inscripcion.id).filter(
            voluntario_id=voluntario_id,
            actividad_id=actividad_id
        ).exists():
            messages.error(request, 'No se puede actualizar, ya está inscrito en esta actividad')
            return redirect('editarInscripcion', id=inscripcion.id)

        # Actualizar datos
        inscripcion.voluntario_id = voluntario_id
        inscripcion.actividad_id = actividad_id

        documento_compromiso = request.FILES.get('documento_compromiso')
        if documento_compromiso:
            inscripcion.documento_compromiso = documento_compromiso

        inscripcion.save()

        # 🔹 Obtener correo actualizado
        correo_nuevo = inscripcion.voluntario.email

        # ======== REENVIAR CORREO SI CAMBIÓ =========
        try:
            send_mail(
                    subject='Actualización de inscripción',
                    message=f'''
Hola {inscripcion.voluntario.nombres} {inscripcion.voluntario.apellidos},

Tu inscripción ha sido actualizada correctamente.

Actividad: {inscripcion.actividad.titulo}
Fecha: {inscripcion.actividad.fecha}
Hora: {inscripcion.actividad.hora}
Lugar: {inscripcion.actividad.lugar}

Este correo se envió porque se actualizó tu inscripción.
''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[correo_nuevo],
                    fail_silently=False,
                )
            email_sent = True
        except Exception as e:
            # Log the error but don't fail the inscription update
            print(f"Error sending email: {e}")
            email_sent = False

        if email_sent:
            messages.success(request, 'Inscripción actualizada correctamente y correo reenviado')
        else:
            messages.success(request, 'Inscripción actualizada correctamente (no se pudo enviar el correo)')
        return redirect('InscripcionIndex')


@login_required
def eliminarInscripcion(request, id):
    inscripcion = get_object_or_404(Inscripcion, id=id)
    inscripcion.delete()
    messages.success(request, 'Inscripción eliminada correctamente')
    return redirect('/InscripcionIndex')

@login_required
def reporte_voluntarios_pdf(request, actividad_id):
    try:
        actividad = Actividad.objects.get(id=actividad_id)
    except Actividad.DoesNotExist:
        raise Http404("La actividad no existe.")

    inscripciones = Inscripcion.objects.filter(actividad=actividad)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_voluntarios_{actividad_id}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)

    # Encabezado general
    p.setFont("Helvetica-Bold", 16)
    p.drawString(225, 770, "Reporte de Voluntario")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 750, f"Actividad: {actividad.titulo}")
    p.line(50, 740, 580, 740)

    y = 710  # posición inicial de los datos

    for i in inscripciones:
        voluntario = i.voluntario

        # Datos principales arriba
        p.setFont("Helvetica-Bold", 12)
        p.drawString(30, y, f"Cédula: {voluntario.cedula}")
        p.drawString(180, y, f"Nombre: {voluntario.nombres}")
        p.drawString(370, y, f"Apellido: {voluntario.apellidos}")
        y -= 40

        # Datos adicionales debajo
        p.setFont("Helvetica", 11)
        p.drawString(30, y, f"Teléfono: {getattr(voluntario, 'telefono', 'N/A')}")
        p.drawString(180, y, f"Fecha Inscripción: {i.fecha_inscripcion.strftime('%d/%m/%Y') if getattr(i, 'fecha_inscripcion', None) else 'N/A'}")
        p.drawString(370, y, f"Actividad: {actividad.titulo}")
        y -= 40  # espacio antes del siguiente voluntario

        p.setFont("Helvetica", 11)
        p.drawString(30, y, f"Email: {voluntario.email}")
        y -= 40

        # Nueva página si se acaba el espacio
        if y < 100:
            p.showPage()
            y = 750
            # Rehacer encabezado
            p.setFont("Helvetica-Bold", 16)
            p.drawString(150, 770, "Reporte de Voluntario")
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, 750, f"Actividad: {actividad.titulo}")
            p.line(50, 740, 580, 740)
            y = 710

    p.showPage()
    p.save()
    return response

def verificar_cedula(request):
    cedula = request.GET.get('cedula')
    voluntario_id = request.GET.get('voluntario_id')

    existe = Voluntario.objects.filter(cedula=cedula)\
        .exclude(id=voluntario_id).exists()

    return JsonResponse(not existe, safe=False)


def verificar_email(request):
    email = request.GET.get('email')
    voluntario_id = request.GET.get('voluntario_id')

    existe = Voluntario.objects.filter(email=email)\
        .exclude(id=voluntario_id).exists()

    return JsonResponse(not existe, safe=False)
