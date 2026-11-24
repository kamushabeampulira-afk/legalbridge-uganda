"""
Rewrite existing users' phone numbers into canonical +256XXXXXXXXX form,
so accounts created before normalisation can still log in.
"""
from django.db import migrations

from users.phone import normalize_phone


def normalize_existing(apps, schema_editor):
    User = apps.get_model('users', 'User')
    taken = set(User.objects.values_list('phone_number', flat=True))
    for user in User.objects.all():
        canonical = normalize_phone(user.phone_number)
        if canonical == user.phone_number:
            continue
        if canonical in taken:
            # Two accounts for the same number: leave this one for an admin to resolve.
            print(f'\n  Skipped {user.phone_number!r}: {canonical!r} already belongs to another account.')
            continue
        taken.discard(user.phone_number)
        taken.add(canonical)
        user.phone_number = canonical
        user.save(update_fields=['phone_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(normalize_existing, migrations.RunPython.noop),
    ]
