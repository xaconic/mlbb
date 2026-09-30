from django.db import models

class Player(models.Model):
    player_id = models.BigIntegerField(primary_key=True)
    server = models.IntegerField()
    ign = models.CharField(max_length=100)
    main_role = models.CharField(max_length=20)
    highest_rank = models.CharField(max_length=50)
    highest_stars = models.PositiveIntegerField(default=0)
    current_rank = models.CharField(max_length=50)
    current_stars = models.PositiveIntegerField(default=0)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.ign