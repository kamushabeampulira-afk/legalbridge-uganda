# Generated manually for multilingual support (en, lg, nyn, ach, lgg).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_normalize_phone_numbers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='preferred_language',
            field=models.CharField(
                choices=[
                    ('en', 'English'),
                    ('lg', 'Luganda'),
                    ('nyn', 'Runyankore'),
                    ('ach', 'Acholi'),
                    ('lgg', 'Lugbara'),
                ],
                default='en',
                max_length=5,
            ),
        ),
    ]
