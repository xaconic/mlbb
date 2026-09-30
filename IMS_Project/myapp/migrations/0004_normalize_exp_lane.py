from django.db import migrations


def normalize_exp_lane(apps, schema_editor):
    Player = apps.get_model('myapp', 'Player')
    Player.objects.using(schema_editor.connection.alias).filter(
        main_role__in=('EXP', 'EXP Lane'),
    ).update(main_role='Exp Lane')


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_player_current_stars_player_highest_stars'),
    ]

    operations = [
        migrations.RunPython(normalize_exp_lane, migrations.RunPython.noop),
    ]