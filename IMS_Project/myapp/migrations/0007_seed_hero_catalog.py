from django.db import migrations


HEROES = (
    ('Angela', 'Roam'),
    ('Balmond', 'Jungle'),
    ('Beatrix', 'Gold Lane'),
    ('Benedetta', 'Exp Lane'),
    ('Bruno', 'Gold Lane'),
    ('Chou', 'Exp Lane'),
    ('Clint', 'Gold Lane'),
    ('Eudora', 'Mid Lane'),
    ('Fanny', 'Jungle'),
    ('Franco', 'Roam'),
    ('Gatotkaca', 'Roam'),
    ('Granger', 'Jungle'),
    ('Gusion', 'Jungle'),
    ('Hayabusa', 'Jungle'),
    ('Kagura', 'Mid Lane'),
    ('Karina', 'Jungle'),
    ('Layla', 'Gold Lane'),
    ('Ling', 'Jungle'),
    ('Lolita', 'Roam'),
    ('Lunox', 'Mid Lane'),
    ('Miya', 'Gold Lane'),
    ('Nana', 'Mid Lane'),
    ('Paquito', 'Exp Lane'),
    ('Pharsa', 'Mid Lane'),
    ('Ruby', 'Exp Lane'),
    ('Saber', 'Jungle'),
    ('Tigreal', 'Roam'),
    ('Valentina', 'Mid Lane'),
    ('X.Borg', 'Exp Lane'),
    ('Yu Zhong', 'Exp Lane'),
)


def seed_heroes(apps, schema_editor):
    Hero = apps.get_model('myapp', 'Hero')
    Hero.objects.using(schema_editor.connection.alias).bulk_create(
        [Hero(name=name, role=role) for name, role in HEROES],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0006_hero_alter_player_options_player_available_for_team_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_heroes, migrations.RunPython.noop),
    ]
