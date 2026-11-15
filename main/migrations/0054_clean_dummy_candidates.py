from django.db import migrations

def remove_dummy_candidates(apps, schema_editor):
    CofestiCandidate = apps.get_model('main', 'CofestiCandidate')
    # Supprimer les candidats de démonstration
    CofestiCandidate.objects.all().delete()

def rollback_clean(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_populate_cofesti_initial_data'),
    ]

    operations = [
        migrations.RunPython(remove_dummy_candidates, rollback_clean),
    ]
