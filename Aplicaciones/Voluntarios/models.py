from django.contrib.auth.models import User
from django.db import models

class Voluntario(models.Model):
    cedula = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Actividad(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(max_length=150)
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(null=True, blank=True)
    lugar = models.CharField(max_length=200)

    cupo_maximo = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='actividades/', null=True, blank=True)

    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def cupos_disponibles(self):
        inscritos = self.inscripciones.count()
        return self.cupo_maximo - inscritos

    def __str__(self):
        return self.titulo

class Inscripcion(models.Model):
    voluntario = models.ForeignKey(
        Voluntario,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )

    documento_compromiso = models.FileField(
        upload_to='documentos_compromiso/',
        null=True,
        blank=True
    )

    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=10,
        choices=[
            ('INSCRITO', 'Inscrito'),
            ('CANCELADO', 'Cancelado'),
        ],
        default='INSCRITO'
    )

    class Meta:
        unique_together = ('voluntario', 'actividad')

    def __str__(self):
        return f"{self.voluntario} → {self.actividad}"
