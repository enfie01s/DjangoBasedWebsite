from django.db import models

colours = {
"0":"#000",#Black
"1":"#00A",#Dark Blue
"2":"#0A0",#Dark Green
"3":"#0AA",#Dark Aqua
"4":"#A00",#Dark Red
"5":"#A0A",#Purple
"6":"#FA0",#Gold
"7":"#AAA",#Gray
"8":"#555",#Dark Gray
"9":"#55F",#Blue
"a":"#5F5",#Bright Green
"b":"#5FF",#Aqua
"c":"#F55",#Red
"d":"#F5F",#Pink
"e":"#FF5",#Yellow
"f":"#FFF"#White
}
#coloursrev = dict(map(reversed, colours.items()))


# Create your models here.

class GPplayer(models.Model):
    name = models.CharField(max_length=50,unique=True)
    lastlogin = models.DateTimeField()
    accruedblocks = models.IntegerField()
    bonusblocks = models.IntegerField()
    uuid = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name

    def lastlogin_pretty(self):
        return self.lastlogin.strftime('%d/%m/%y %H:%I')

    class Meta:
        db_table = 'griefprevention_playerdata'

class Entity(models.Model):
    name = models.CharField(max_length=50)
    etype = models.SmallIntegerField(db_column='type')
    nick = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'pex_entity'
        ordering = ['etype','name']

class Inheritance(models.Model):
    child = models.CharField(max_length=50)
    parent = models.CharField(max_length=50)
    itype = models.SmallIntegerField(db_column='type')
    world = models.CharField(max_length=50)

    def __str__(self):
        return self.child

    class Meta:
        db_table = 'pex_inheritance'

class Permission(models.Model):
    name = models.CharField(max_length=50)
    ptype = models.SmallIntegerField(db_column='type')
    permission = models.TextField()
    world = models.CharField(max_length=50)
    value = models.TextField()

    def __str__(self):
        return self.permission

    class Meta:
        db_table = 'pex_permissions'
        ordering = ['name','world']

class Rank(models.Model):
    rank = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    suffix = models.CharField(max_length=255)
    rpass = models.CharField(max_length=255,db_column='pass')
    order = models.IntegerField()

    def __str__(self):
        return self.rank

    def prettyprefix(self):
        pref = '<span>' + self.prefix + '</span>'
        for k,v in colours.items():
            pref = pref.replace('&'+k, '</span><span style=\'color:'+ v +'\'>')
        return pref

    class Meta:
        db_table = 'mc_ranks'
        ordering = ['order']

class SitePlayer(models.Model):# specify db_column on a foreign key field or it will expect col to be col_id
    rank = models.ForeignKey(Rank, db_column='rank',related_name='rankid', on_delete=models.DO_NOTHING)
    passaduchy = models.CharField(max_length=255)
    mailaddy = models.EmailField(max_length=254)
    player = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    suffix = models.CharField(max_length=255)
    uuid = models.ForeignKey(GPplayer, to_field = 'name',db_column='uuid',related_name='gp', on_delete=models.DO_NOTHING)
    ip = models.GenericIPAddressField(unpack_ipv4=True)
    dateadded = models.DateTimeField()

    def __str__(self):
        return self.player

    class Meta:
        db_table = 'mc_players'
        ordering = ['rank']
        #order_with_respect_to = 'rank' # needs _order column in this db

class SitePerm(models.Model):
    RANKCHOICES = Rank.objects.values_list('id','rank').all()
    PLUGINCHOICES = (
        ('bukkit','Bukkit'),
        ('GriefPrevention','Grief Prevention'),
        ('Essentials','Essentials'),
        ('WorldEdit','World Edit'),
        ('WorldGuard','World Guard'),
        ('Multiverse-Core','Multiverse Core'),
        ('iConomy','iConomy'),
        ('LogBlock','Log Block'),
        ('DeathControl','Death Control'),
        ('ChestShop','Chest Shop'),
        ('QuickShop','Quick Shop'),
        ('RegionForSale','Region For Sale'),
        ('NoLagg','No Lagg')
    )
    pl = models.CharField(max_length=255,choices=PLUGINCHOICES)
    perm = models.CharField(max_length=255)
    bool = models.CharField(max_length=255,choices=(('true','True'),('false','False')))
    comm = models.CharField(max_length=255)
    descrip = models.CharField(max_length=255)
    minrank = models.ForeignKey(Rank, db_column='minrank',choices=RANKCHOICES, default='10', related_name='prankid', on_delete=models.DO_NOTHING)
    world = models.CharField(max_length=255)
    altcomm = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)

    def __str__(self):
        return self.perm

    def useage(self):
        '''
        com always there
        altcom not always there but contains useage
        join altcom to com if not blank 
        theComm = self.altcomm if len(self.altcomm) > 0 else self.comm
        '''
        usebits = self.altcomm.replace('/&lt;command&gt;','')
        return self.comm + usebits

    class Meta:
        db_table = 'mc_plugperms'
        ordering = ['-minrank','perm']

class World(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'mc_world'