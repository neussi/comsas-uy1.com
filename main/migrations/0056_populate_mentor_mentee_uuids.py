import uuid
from django.db import migrations, models

def populate_uuids(apps, schema_editor):
    Mentor = apps.get_model('main', 'Mentor')
    Mentee = apps.get_model('main', 'Mentee')
    
    for m in Mentor.objects.all():
        m.uuid = uuid.uuid4()
        m.save(update_fields=['uuid'])
            
    for m in Mentee.objects.all():
        m.uuid = uuid.uuid4()
        m.save(update_fields=['uuid'])

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_match_compatibility_score_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_uuids, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='mentor',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='mentee',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
