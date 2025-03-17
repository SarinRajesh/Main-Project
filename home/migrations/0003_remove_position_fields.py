from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_create_roommodel'),  # Replace with your previous migration
    ]

    operations = [
        migrations.RemoveField(
            model_name='roommodel',
            name='position_x',
        ),
        migrations.RemoveField(
            model_name='roommodel',
            name='position_y',
        ),
        migrations.RemoveField(
            model_name='roommodel',
            name='position_z',
        ),
        migrations.RemoveField(
            model_name='roommodel',
            name='rotation_y',
        ),
        migrations.RemoveField(
            model_name='roommodel',
            name='scale',
        ),
    ] 