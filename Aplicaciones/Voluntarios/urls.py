from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar_admin/', views.registrar_admin, name='registrar_admin'),
    path('', views.index, name='index'),  
    # =============================
    # VOLUNTARIOS
    # =============================
    path('VoluntarioIndex/', views.VoluntarioIndex, name='VoluntarioIndex'),
    path('nuevoVoluntario/', views.nuevoVoluntario, name='nuevoVoluntario'),
    path('guardarVoluntario/', views.guardarVoluntario, name='guardarVoluntario'),
    path('editarVoluntario/<int:id>/', views.editarVoluntario, name='editarVoluntario'),
    path('actualizarVoluntario/', views.actualizarVoluntario, name='actualizarVoluntario'),
    path('eliminarVoluntario/<int:id>/', views.eliminarVoluntario, name='eliminarVoluntario'),


    # =============================
    # ACTIVIDADES
    # =============================
    path('ActividadIndex/', views.ActividadIndex, name='ActividadIndex'),
    path('nuevaActividad/', views.nuevaActividad, name='nuevaActividad'),
    path('guardarActividad/', views.guardarActividad, name='guardarActividad'),
    path('editarActividad/<int:id>/', views.editarActividad, name='editarActividad'),
    path('actualizarActividad/', views.actualizarActividad, name='actualizarActividad'),
    path('eliminarActividad/<int:id>/', views.eliminarActividad, name='eliminarActividad'),


    # =============================
    # INSCRIPCIONES
    # =============================
    path('InscripcionIndex/', views.InscripcionIndex, name='InscripcionIndex'),
    path('nuevaInscripcion/', views.nuevaInscripcion, name='nuevaInscripcion'),
    path('guardarInscripcion/', views.guardarInscripcion, name='guardarInscripcion'),
    path('editarInscripcion/<int:id>/', views.editarInscripcion, name='editarInscripcion'),
    path('actualizarInscripcion/', views.actualizarInscripcion, name='actualizarInscripcion'),
    path('eliminarInscripcion/<int:id>/', views.eliminarInscripcion, name='eliminarInscripcion'),


    # =============================
    # REPORTES
    # =============================

    path('reporte_voluntarios_pdf/<int:actividad_id>/', views.reporte_voluntarios_pdf, name='reporte_voluntarios_pdf'),
    path('verificar_cedula/', views.verificar_cedula, name='verificar_cedula'),
    path('verificar_email/', views.verificar_email, name='verificar_email'),
    
    
]