# Generated manually
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Crear modelo Especialistas (managed=False, no se crea tabla)
        migrations.CreateModel(
            name='Especialistas',
            fields=[
                ('id_especialistas', models.IntegerField(db_column='ID_Especialistas', primary_key=True, serialize=False)),
                ('id_especialidad_especialista', models.CharField(blank=True, max_length=45, null=True)),
                ('dni', models.IntegerField(blank=True, db_column='DNI', null=True)),
                ('matricula', models.IntegerField(blank=True, db_column='Matricula', null=True)),
                ('email', models.CharField(blank=True, db_column='Email', max_length=100, null=True)),
                ('telefono', models.IntegerField(blank=True, db_column='Telefono', null=True)),
            ],
            options={
                'db_table': 'especialistas',
                'managed': False,
            },
        ),
        # Crear modelo EstadisticaPaciente
        migrations.CreateModel(
            name='EstadisticaPaciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('edad', models.IntegerField()),
                ('especialidad', models.CharField(choices=[('Psicología', 'Psicología'), ('Fonoaudiología', 'Fonoaudiología'), ('Kinesiología', 'Kinesiología'), ('Psicomotricidad', 'Psicomotricidad'), ('Psicopedagogía', 'Psicopedagogía')], max_length=50)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        # Eliminar especialista_rel de Perfil
        migrations.RemoveField(
            model_name='perfil',
            name='especialista_rel',
        ),
        # Cambiar especialista en Observacion a CharField
        migrations.AlterField(
            model_name='observacion',
            name='especialista',
            field=models.CharField(choices=[('sol_psico', 'Lic. Sol Espasandin'), ('carlos_kine', 'Lic. Carlos Herrera'), ('mailen_psico', 'Lic. Mailen Danilowicz'), ('silvina_psico', 'Lic. Silvina Diaz'), ('carolina_psicope', 'Lic. Carolina Herrera'), ('monica_fono', 'Lic. Monica Palacios Cañizares'), ('itati_psicope', 'Lic. Itati Gordillo')], max_length=100),
        ),
        # Actualizar Meta options
        migrations.AlterModelOptions(
            name='turno',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='especialidades',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='centrosterapeuticos',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='detallepagos',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='estadopaciente',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='historialpaciente',
            options={'managed': False},
        ),
        # CREAR NUEVO modelo InformeInterdisciplinario
        migrations.CreateModel(
            name='InformeInterdisciplinario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asunto', models.CharField(max_length=255, verbose_name='Asunto del informe')),
                ('fecha_informe', models.DateField(verbose_name='Fecha del informe (para qué día es)')),
                ('descripcion_general', models.TextField(blank=True, null=True, verbose_name='Descripción general')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Creado el')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='Última modificación')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='informes_creados', to=settings.AUTH_USER_MODEL)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='informes', to='app.paciente')),
                ('especialistas', models.ManyToManyField(limit_choices_to={'rol': 'especialista'}, related_name='informes_colaborados', to='app.perfil')),
            ],
            options={
                'verbose_name': 'Informe Interdisciplinario',
                'verbose_name_plural': 'Informes Interdisciplinarios',
                'ordering': ['-fecha_informe'],
            },
        ),
        # Crear modelo SeccionInforme
        migrations.CreateModel(
            name='SeccionInforme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField(verbose_name='Contenido de la sección')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Creado el')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='Última modificación')),
                ('especialista', models.ForeignKey(limit_choices_to={'rol': 'especialista'}, on_delete=django.db.models.deletion.CASCADE, to='app.perfil')),
                ('informe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secciones', to='app.informeinterdisciplinario')),
            ],
            options={
                'verbose_name': 'Sección de Informe',
                'verbose_name_plural': 'Secciones de Informe',
                'ordering': ['fecha_creacion'],
                'unique_together': {('informe', 'especialista')},
            },
        ),
    ]
