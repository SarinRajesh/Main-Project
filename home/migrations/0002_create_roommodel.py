from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('model_file', models.FileField(upload_to='room_models/')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='room_model_thumbnails/')),
                ('category', models.CharField(default='furniture', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('position_x', models.FloatField(default=0)),
                ('position_y', models.FloatField(default=0)),
                ('position_z', models.FloatField(default=0)),
                ('rotation_y', models.FloatField(default=0)),
                ('scale', models.FloatField(default=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.users')),
            ],
            options={
                'verbose_name': 'Room Model',
                'verbose_name_plural': 'Room Models',
            },
        ),
    ]