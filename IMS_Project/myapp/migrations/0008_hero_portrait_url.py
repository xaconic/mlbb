from django.db import migrations, models


PORTRAITS = (
    ('Angela', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_a815a3adad8df99481700c84abaf3c41.png'),
    ('Balmond', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_6c018674ea709972b4837ec90518e79e.png'),
    ('Beatrix', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_c1acd7cbd828f0c5d291e48a0f7c018d.png'),
    ('Benedetta', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_eceefa7ba07f093d71a30852f0051b7a.png'),
    ('Bruno', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_3259934dcb13b5a4ba25b25a3eb86f54.png'),
    ('Chou', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_850c4b51e3dbab3fd12a718917eaaf44.png'),
    ('Clint', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_9a8a8fa3b5eed761a86d8f98740a4325.png'),
    ('Eudora', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_1384ce93e5bdb142ea4e5e6b9f941ff1.png'),
    ('Fanny', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_8ea3a95fa3c726ed0338c0fdd21ad991.png'),
    ('Franco', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_d21e5731e8bf993a9b3271767a3b3b97.png'),
    ('Gatotkaca', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_e3ccd096c9c4649519d736073acca91a.png'),
    ('Granger', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_9ed57f48f91012fd110935258cd1ab61.png'),
    ('Gusion', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_82dbd20a7d0f274520895007898199e0.png'),
    ('Hayabusa', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_63cb1f44bf906b71767a000e38d8ab14.png'),
    ('Kagura', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_634196d9234babcc3072155d4fefaf0c.png'),
    ('Karina', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_4685e0fb17e2fabaf9cb23f8db8fa262.png'),
    ('Layla', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_6efe9abc2047f59d45fa1c88fb1261b7.png'),
    ('Ling', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_4405561c38db556d9cdc6a57b8642e66.png'),
    ('Lolita', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_55de18c865efe8e360b3b9ae463d76a2.png'),
    ('Lunox', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_69d35cd0c549a9bdbcf9fbfddf3122a5.png'),
    ('Miya', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_32c0d9d3a727a9052754296af6251435.png'),
    ('Nana', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_ce58cae711d0907a722de0e65fbb85b7.png'),
    ('Paquito', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_7d54ccba749ba18ec934631b49632d1f.png'),
    ('Pharsa', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_cccf53dbeacc789288ebc1fb63fcf7dd.png'),
    ('Ruby', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_5b9d38f9f2e7ca03f9f489de19656bc9.png'),
    ('Saber', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_b5980d535886303ad116fba3463c76ce.png'),
    ('Tigreal', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_4e0005dbfb1376beaccc54ef7aa39375.png'),
    ('Valentina', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_7923ebf470d0e963e9978cb21eb25780.png'),
    ('X.Borg', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_cc433460d0b2053a3d3a18b46462bfb2.png'),
    ('Yu Zhong', 'https://akmweb.youngjoygame.com/web/svnres/img/test/homepage_2_2_16_1232_1/100_7d5ad4d511f5257137028f19e9ee973f.png'),
)


def populate_portraits(apps, schema_editor):
    Hero = apps.get_model('myapp', 'Hero')
    database = schema_editor.connection.alias
    for name, url in PORTRAITS:
        Hero.objects.using(database).filter(name=name).update(portrait_url=url)


def clear_portraits(apps, schema_editor):
    Hero = apps.get_model('myapp', 'Hero')
    database = schema_editor.connection.alias
    for name, url in PORTRAITS:
        Hero.objects.using(database).filter(name=name, portrait_url=url).update(portrait_url='')


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0007_seed_hero_catalog'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='portrait_url',
            field=models.URLField(blank=True, help_text='Optional official hero portrait URL; leave blank to use the local fallback.'),
        ),
        migrations.RunPython(populate_portraits, clear_portraits),
    ]
