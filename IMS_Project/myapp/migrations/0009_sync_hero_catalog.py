from django.db import migrations

SOURCE_URL = 'https://mobile-legends.fandom.com/api.php?action=parse&page=Template%3AList_of_heroes&prop=text&format=json'
HEROES = (
    ("Miya", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/8/8c/Hero011-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145035"),
    ("Balmond", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/9/93/Hero021-icon.png/revision/latest/scale-to-width-down/200?cb=20251110110542"),
    ("Saber", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/8/87/Hero031-icon.png/revision/latest/scale-to-width-down/200?cb=20250406000724"),
    ("Alice", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/fd/Hero041-icon.png/revision/latest/scale-to-width-down/200?cb=20250917073910"),
    ("Nana", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/c/c3/Hero051-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145100"),
    ("Tigreal", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/f/f2/Hero061-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145106"),
    ("Alucard", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/c/c7/Hero071-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145111"),
    ("Karina", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/8/8a/Hero081-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145117"),
    ("Akai", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/b/be/Hero091-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145133"),
    ("Franco", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/2/25/Hero101-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145139"),
    ("Bane", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/e/e7/Hero111-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145146"),
    ("Bruno", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/f9/Hero121-icon.png/revision/latest/scale-to-width-down/200?cb=20260916132625"),
    ("Clint", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/7/73/Hero131-icon.png/revision/latest/scale-to-width-down/200?cb=20260918135606"),
    ("Rafaela", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/5/5e/Hero141-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145203"),
    ("Eudora", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/2a/Hero151-icon.png/revision/latest/scale-to-width-down/200?cb=20260129103003"),
    ("Zilong", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/5/5f/Hero161-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145216"),
    ("Fanny", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/7/78/Hero171-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145223"),
    ("Layla", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/0/02/Hero181-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145229"),
    ("Minotaur", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/0/08/Hero191-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145234"),
    ("Lolita", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/1/17/Hero201-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145241"),
    ("Hayabusa", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/c/cb/Hero211-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145247"),
    ("Freya", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/4/4e/Hero221-icon.png/revision/latest/scale-to-width-down/200?cb=20251110105914"),
    ("Gord", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/27/Hero231-icon.png/revision/latest/scale-to-width-down/200?cb=20250109162109"),
    ("Natalia", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/6/6a/Hero241-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145304"),
    ("Kagura", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/e/ef/Hero251-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145310"),
    ("Chou", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/a/a9/Hero261-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145315"),
    ("Sun", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/fe/Hero271-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145321"),
    ("Alpha", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/3/38/Hero281-icon.png/revision/latest/scale-to-width-down/200?cb=20250802155834"),
    ("Ruby", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/1/1d/Hero291-icon.png/revision/latest/scale-to-width-down/200?cb=20250802152451"),
    ("Yi Sun-shin", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/e/ed/Hero301-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145338"),
    ("Moskov", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/2e/Hero311-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145343"),
    ("Johnson", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/7/73/Hero321-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145350"),
    ("Cyclops", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/9/96/Hero331-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145355"),
    ("Estes", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/9/92/Hero341-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145400"),
    ("Hilda", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/1/11/Hero351-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145405"),
    ("Aurora", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/2c/Hero361-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145411"),
    ("Lapu-Lapu", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/e/ee/Hero371-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145417"),
    ("Vexana", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/6/6d/Hero381-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145423"),
    ("Roger", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/9/97/Hero391-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145430"),
    ("Karrie", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/d/de/Hero401-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145437"),
    ("Gatotkaca", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/c/cb/Hero411-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145443"),
    ("Harley", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/9/92/Hero421-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145449"),
    ("Irithel", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/5/58/Hero431-icon.png/revision/latest/scale-to-width-down/200?cb=20260618090441"),
    ("Grock", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/d/dd/Hero441-icon.png/revision/latest/scale-to-width-down/200?cb=20250811073945"),
    ("Argus", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/c/c7/Hero451-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145507"),
    ("Odette", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/a/a9/Hero461-icon.png/revision/latest/scale-to-width-down/200?cb=20250118142124"),
    ("Lancelot", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/2/29/Hero471-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145518"),
    ("Diggie", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/e/e3/Hero481-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145524"),
    ("Hylos", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/0/0c/Hero491-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145529"),
    ("Zhask", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/5/54/Hero501-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145534"),
    ("Helcurt", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/e/eb/Hero511-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145541"),
    ("Pharsa", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/e/ef/Hero521-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145546"),
    ("Lesley", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/8/82/Hero531-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145551"),
    ("Jawhead", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/1/1c/Hero541-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145558"),
    ("Angela", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/1/13/Hero551-icon.png/revision/latest/scale-to-width-down/200?cb=20250406000608"),
    ("Gusion", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/9/94/Hero561-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145610"),
    ("Valir", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/6/60/Hero571-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145616"),
    ("Martis", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/a/ac/Hero581-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145622"),
    ("Uranus", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/b/ba/Hero591-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145629"),
    ("Hanabi", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/ff/Hero601-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145634"),
    ("Chang\u0027e", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/5/5c/Hero611-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145640"),
    ("Kaja", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/2/28/Hero621-icon.png/revision/latest/scale-to-width-down/200?cb=20260805104508"),
    ("Selena", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/d/d4/Hero631-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145650"),
    ("Aldous", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/9/95/Hero641-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145655"),
    ("Claude", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/29/Hero651-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145701"),
    ("Vale", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/fb/Hero661-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145708"),
    ("Leomord", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/8/88/Hero671-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145713"),
    ("Lunox", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/f6/Hero681-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145719"),
    ("Hanzo", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/f/f4/Hero691-icon.png/revision/latest/scale-to-width-down/200?cb=20250118142130"),
    ("Belerick", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/d/d7/Hero701-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145730"),
    ("Kimmy", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/1/15/Hero711-icon.png/revision/latest/scale-to-width-down/200?cb=20250402105900"),
    ("Thamuz", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/1/17/Hero721-icon.png/revision/latest/scale-to-width-down/200?cb=20250917080704"),
    ("Harith", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/5/5a/Hero731-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145748"),
    ("Minsitthar", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/1/1e/Hero741-icon.png/revision/latest/scale-to-width-down/200?cb=20241021145754"),
    ("Kadita", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/4/46/Hero751-icon.png/revision/latest/scale-to-width-down/200?cb=20260925052928"),
    ("Faramis", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/3/34/Hero761-icon.png/revision/latest/scale-to-width-down/200?cb=20241021152934"),
    ("Badang", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/a/a4/Hero771-icon.png/revision/latest/scale-to-width-down/200?cb=20260919020751"),
    ("Khufra", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/c/cd/Hero781-icon.png/revision/latest/scale-to-width-down/200?cb=20241021152946"),
    ("Granger", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/7/7c/Hero791-icon.png/revision/latest/scale-to-width-down/200?cb=20241108062800"),
    ("Guinevere", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/f1/Hero801-icon.png/revision/latest/scale-to-width-down/200?cb=20241021152957"),
    ("Esmeralda", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/8/88/Hero811-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153002"),
    ("Terizla", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/a/ab/Hero821-icon.png/revision/latest/scale-to-width-down/200?cb=20250802150120"),
    ("X.Borg", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/7/7a/Hero831-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153015"),
    ("Ling", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/c/ca/Hero841-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153020"),
    ("Dyrroth", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/6/62/Hero851-icon.png/revision/latest/scale-to-width-down/200?cb=20250917081355"),
    ("Lylia", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/a/a4/Hero861-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153033"),
    ("Baxia", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/0/09/Hero871-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153038"),
    ("Masha", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/c/c5/Hero881-icon.png/revision/latest/scale-to-width-down/200?cb=20260918142337"),
    ("Wanwan", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/24/Hero891-icon.png/revision/latest/scale-to-width-down/200?cb=20250118142135"),
    ("Silvanna", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/4/40/Hero901-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153056"),
    ("Cecilion", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/8/85/Hero911-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153102"),
    ("Carmilla", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/2/23/Hero921-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153106"),
    ("Atlas", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/6/6e/Hero931-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153111"),
    ("Popol and Kupa", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/a/ab/Hero941-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153117"),
    ("Yu Zhong", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/5/53/Hero951-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153123"),
    ("Luo Yi", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/f/f0/Hero961-icon.png/revision/latest/scale-to-width-down/200?cb=20260918005444"),
    ("Benedetta", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/4/47/Hero971-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153134"),
    ("Khaleed", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/d/d2/Hero981-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153140"),
    ("Barats", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/1/1a/Hero991-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153146"),
    ("Brody", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/1/12/Hero1001-icon.png/revision/latest/scale-to-width-down/200?cb=20260916131929"),
    ("Yve", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/c/cd/Hero1011-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153157"),
    ("Mathilda", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/c/cf/Hero1021-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153203"),
    ("Paquito", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/3/35/Hero1031-icon.png/revision/latest/scale-to-width-down/200?cb=20260925051951"),
    ("Gloo", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/4/45/Hero1041-icon.png/revision/latest/scale-to-width-down/200?cb=20250402105857"),
    ("Beatrix", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/a/a9/Hero1051-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153218"),
    ("Phoveus", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/8/88/Hero1061-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153224"),
    ("Natan", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/25/Hero1071-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153231"),
    ("Aulus", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/b/bf/Hero1081-icon.png/revision/latest/scale-to-width-down/200?cb=20260423095836"),
    ("Aamon", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/b/bc/Hero1091-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153241"),
    ("Valentina", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/6/62/Hero1101-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153247"),
    ("Edith", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/3/36/Hero1111-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153252"),
    ("Floryn", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/2/20/Hero1121-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153258"),
    ("Yin", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/b/b5/Hero1131-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153303"),
    ("Melissa", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/0/09/Hero1141-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153310"),
    ("Xavier", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/8/80/Hero1151-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153316"),
    ("Julian", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/c/c2/Hero1161-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153321"),
    ("Fredrinn", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/f/f4/Hero1171-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153327"),
    ("Joy", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/c/c1/Hero1181-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153333"),
    ("Novaria", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/a/a1/Hero1191-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153339"),
    ("Arlott", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/2/22/Hero1201-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153344"),
    ("Ixia", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/a/a2/Hero1211-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153350"),
    ("Nolan", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/e/e1/Hero1221-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153356"),
    ("Cici", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/6/65/Hero1231-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153402"),
    ("Chip", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/9/94/Hero1241-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153409"),
    ("Zhuxin", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/0/05/Hero1251-icon.png/revision/latest/scale-to-width-down/200?cb=20250406000840"),
    ("Suyou", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/c/c4/Hero1261-icon.png/revision/latest/scale-to-width-down/200?cb=20241021153421"),
    ("Lukas", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/1/1c/Hero1271-icon.png/revision/latest/scale-to-width-down/200?cb=20250125233414"),
    ("Kalea", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/5/56/Hero1281-icon.png/revision/latest/scale-to-width-down/200?cb=20250402015050"),
    ("Zetian", "Mid Lane", "https://static.wikia.nocookie.net/mobile-legends/images/5/5c/Hero1291-icon.png/revision/latest/scale-to-width-down/200?cb=20250402020310"),
    ("Obsidia", "Gold Lane", "https://static.wikia.nocookie.net/mobile-legends/images/9/9b/Hero1301-icon.png/revision/latest/scale-to-width-down/200?cb=20250928040150"),
    ("Sora", "Exp Lane", "https://static.wikia.nocookie.net/mobile-legends/images/c/cc/Hero1311-icon.png/revision/latest/scale-to-width-down/200?cb=20251220013450"),
    ("Marcel", "Roam", "https://static.wikia.nocookie.net/mobile-legends/images/e/ee/Hero1321-icon.png/revision/latest/scale-to-width-down/200?cb=20260312135432"),
    ("Hirara", "Jungle", "https://static.wikia.nocookie.net/mobile-legends/images/0/02/Hero1331-icon.png/revision/latest/scale-to-width-down/200?cb=20260619074900"),
)


def sync_hero_catalog(apps, schema_editor):
    Hero = apps.get_model('myapp', 'Hero')
    database = schema_editor.connection.alias
    existing = {hero.name: hero for hero in Hero.objects.using(database).all()}
    names = []
    to_create = []
    to_update = []

    for name, role, portrait_url in HEROES:
        names.append(name)
        hero = existing.get(name)
        if hero is None:
            to_create.append(Hero(name=name, role=role, portrait_url=portrait_url, is_active=True))
            continue
        if (hero.role, hero.portrait_url, hero.is_active) != (role, portrait_url, True):
            hero.role = role
            hero.portrait_url = portrait_url
            hero.is_active = True
            to_update.append(hero)

    Hero.objects.using(database).bulk_create(to_create, batch_size=100)
    Hero.objects.using(database).bulk_update(to_update, ('role', 'portrait_url', 'is_active'), batch_size=100)
    Hero.objects.using(database).exclude(name__in=names).update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0008_hero_portrait_url'),
    ]

    operations = [
        migrations.RunPython(sync_hero_catalog, migrations.RunPython.noop),
    ]
