from django.db import models
from django.contrib.auth.models import AbstractUser
import mysql.connector


class Administrator(models.Model):
    idkor = models.OneToOneField('Korisnik', models.DO_NOTHING, db_column='IdKor', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'administrator'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Kategorija(models.Model):
    idkat = models.AutoField(db_column='IdKat', primary_key=True)  # Field name made lowercase.
    naziv = models.CharField(db_column='Naziv', max_length=45)  # Field name made lowercase.
    slika = models.TextField(db_column='Slika')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'kategorija'


class Korisnik(models.Model):
    idkor = models.AutoField(db_column='IdKor', primary_key=True)  # Field name made lowercase.
    korisnicko_ime = models.CharField(db_column='Korisnicko_ime', max_length=45)  # Field name made lowercase.
    lozinka = models.CharField(db_column='Lozinka', max_length=45)  # Field name made lowercase.
    ime = models.CharField(db_column='Ime', max_length=45)  # Field name made lowercase.
    prezime = models.CharField(db_column='Prezime', max_length=45)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=45)  # Field name made lowercase.
    pol = models.CharField(db_column='Pol', max_length=1)  # Field name made lowercase.
    broj_poena = models.IntegerField(db_column='Broj_poena')  # Field name made lowercase.
    nivo = models.IntegerField(db_column='Nivo')  # Field name made lowercase.
    vazeci = models.IntegerField(db_column='Vazeci')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'korisnik'


class Moderator(models.Model):
    idkor = models.OneToOneField(Korisnik, models.DO_NOTHING, db_column='IdKor', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'moderator'


class Ocena(models.Model):
    idoce = models.AutoField(db_column='IdOce', primary_key=True)  # Field name made lowercase.
    idpit = models.ForeignKey('Pitanje', models.DO_NOTHING, db_column='IdPit')  # Field name made lowercase.
    idkor = models.ForeignKey(Korisnik, models.DO_NOTHING, db_column='IdKor')  # Field name made lowercase.
    vrednost_ocene = models.IntegerField(db_column='Vrednost_ocene')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ocena'


class Pitanje(models.Model):
    idpit = models.AutoField(db_column='IdPit', primary_key=True)  # Field name made lowercase.
    idkat = models.ForeignKey(Kategorija, models.DO_NOTHING, db_column='IdKat', blank=True, null=True)  # Field name made lowercase.
    tekst_pitanja = models.CharField(db_column='Tekst_pitanja', unique=True, max_length=250)  # Field name made lowercase.
    tezina_pitanja = models.IntegerField(db_column='Tezina_pitanja', blank=True, null=True)  # Field name made lowercase.
    tacan_odgovor = models.CharField(db_column='Tacan_odgovor', max_length=125, blank=True, null=True)  # Field name made lowercase.
    netacan1 = models.CharField(db_column='Netacan1', max_length=125, blank=True, null=True)  # Field name made lowercase.
    netacan2 = models.CharField(db_column='Netacan2', max_length=125, blank=True, null=True)  # Field name made lowercase.
    netacan3 = models.CharField(db_column='Netacan3', max_length=125, blank=True, null=True)  # Field name made lowercase.
    zbir_ocena = models.IntegerField(db_column='Zbir_ocena')  # Field name made lowercase.
    broj_ocena = models.IntegerField(db_column='Broj_ocena')  # Field name made lowercase.
    prosecna_ocena = models.DecimalField(db_column='Prosecna_ocena', max_digits=6, decimal_places=3)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pitanje'


class RegistrovaniKorisnik(models.Model):
    idkor = models.OneToOneField(Korisnik, models.DO_NOTHING, db_column='IdKor', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'registrovani_korisnik'
