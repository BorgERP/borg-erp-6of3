row_defs={ 
    '900':{
        'IZ900DVBDIPOS':[    1,  7], # VBDI – posiljatelja (banke)
        'IZ900NAZBAN':  [    8, 57], # Naziv banke
        'IZ9000OIBBNK': [   58, 68], # OIB banke
        'IZ900VRIZ':    [   69, 72], # Vrsta izvatka
        'IZ900DATUM':   [   73, 80], # Datum obrade – tekuci datum GGGGMMDD
        'IZ900REZ2':    [  81, 997], # Rezerva
        'IZ900TIPSL':   [998, 1000], # Tip sloga
    }
    '903':{
        'IZ903VBDI':    [   1,   7], # Vodeci broj banke
        'IZ903BIC':     [   8,  18], # BIC - Identifikacijska sifra banke
        'IZ903RACUN':   [  19,  39], # Transakcijski racun klijenta
        'IZ903VLRN':    [  40,  42], # Valuta transakcijskog racuna
        'IZ903NAZKLI':  [  43, 112], # Naziv klijenta
        'IZ903SJEDKLI': [ 113, 147], # Sjediste klijenta
        'IZ903MB':      [ 148, 155], # Maticni broj
        'IZ903OIBKLI':  [ 156, 166], # OIB klijenta
        'IZ903RBIZV':   [ 167, 169], # Redni broj izvatka
        'IZ903PODBR':   [ 170, 172], # Podbroj izvatka
        'IZ903DATUM':   [ 173, 180], # Datum izvatka
        'IZ903BRGRU':   [ 181, 184], # Redni broj grupe paketa
        'IZ903VRIZ':    [ 185, 188], # Vrsta izvatka
        'IZ903REZ':     [ 189, 997], # Rezerva
        'IZ903TIPSL':   [998, 1000], # Tip sloga
    }
    '905':{
        'IZ905OZTRA':        [   1,   2], # Oznaka transakcije
        'IZ905RNPRPL':       [   3,  36], # Racun primatelja-platitelja
        'IZ905NAZPRPL':      [  37, 106], # Naziv primatelja-platitelja
        'IZ905ADRPRPL':      [ 107, 141], # Adresa primatelja-platitelja
        'IZ905SJPRPL':       [ 142, 176], # Sjediste primatelja-platitelja
        'IZ905DATVAL':       [ 177, 184], # Datum valute(GGGGMMDD)
        'IZ905DATIZVR':      [ 185, 192], # Datum izvrsenja(GGGGMMDD)
        'IZ905VLPL':         [ 193, 195], # Valuta pokrica
        'IZ905TECAJ':        [ 196, 210], # Tecaj/koeficijent
        'IZ905PREDZNVL':     [ 211, 211], # Predznak je „+“, a u slucaju storna upisuje se „-„
        'IZ905IZNOSPPVALUTE':[ 212, 226], # Iznos u valuti pokrica
        'IZ905PREDZN':       [ 227, 227], # Predznak je „+“, a u slucaju storna upisuje se „-„
        'IZ905IZNOS':        [ 228, 242], # Iznos
        'IZ905PNBPL':        [ 243, 268], # Poziv na broj platitelja
        'IZ905PNBPR':        [ 269, 294], # Poziv na broj primatelja
        'IZ905SIFNAM':       [ 295, 298], # Sifra namjene
        'IZ905OPISPL':       [ 299, 438], # Opis placanja
        'IZ905IDTRFINA':     [ 439, 480], # Identifikator transakcije – inicirano u FINI
        'IZ905IDTRBAN':      [ 481, 515], # Identifikator transakcije – inicirano izvan FINE
        'IZ905REZ2':         [ 516, 997], # Rezerva
        'IZ905TIPSL':        [998, 1000], # Tip sloga
    }
    '907':{
        'IZ907RACUN':   [   1,  21], # Transakcijski racun klijenta
        'IZ907VLRN':    [  22,  24], # Valuta transakcijskog racuna
        'IZ907NAZKLI':  [  25,  94], # Naziv klijenta
        'IZ907RBIZV':   [  95,  97], # Redni broj Izvatka
        'IZ907PRRBIZV': [  98, 100], # Redni broj prethodnog Izvatka
        'IZ907DATUM':   [ 101, 108], # Datum izvatka
        'IZ907DATPRSAL':[ 109, 116], # Datum prethodnog stanja(GGGGMMDD)
        'IZ907PPPOS':   [ 117, 117], # Predznak prethodnog stanja
        'IZ907PRSAL':   [ 118, 132], # Prethodno stanje
        'IZ907PREREZ':  [ 133, 133], # Predznak rezervacije
        'IZ907IZNREZ':  [ 134, 148], # Iznos rezervacije
        'IZ907DATOKV':  [ 149, 156], # Datum dozvoljenog prekoracenja(GGGMMDD)
        'IZ907IZNOKV':  [ 157, 171], # Dozvoljeno prekoracenje (okvirni kredit)
        'IZ907IZNZAPSR':[ 172, 186], # Iznos zaplijenjenih sredstava
        'IZ907PRASPSTA':[ 187, 187], # Predznak raspolozivog stanja
        'IZ907IZNRASP': [ 188, 202], # Iznos raspolozivog stanja
        'IZ907PDUGU':   [ 203, 203], # Predznak ukupnog dugovnog prometa
        'IZ907KDUGU':   [ 204, 218], # Ukupni dugovni promet
        'IZ907PPOTR':   [ 219, 219], # Predznak ukupnog potraznog prometa
        'IZ907KPOTR':   [ 220, 234], # Ukupni potrazni promet
        'IZ07PRNOS':    [ 235, 235], # Predznak novog stanja
        'IZ907KOSAL':   [ 236, 250], # Novo stanje
        'IZ907BRGRU':   [ 251, 254], # Redni broj grupe u paketu
        'IZ907BRSTA':   [ 255, 260], # Broj stavaka u grupi
        'IZ907TEKST':   [ 261, 680], # Tekstualna poruka
        'IZ907REZ2':    [ 681, 997], # Rezerva
        'IZ907TIPSL':   [998, 1000], # Tip sloga
    }
    '909':{
        'IZ909DATUM':   [  1,    8], # Datum obrade
        'IZ909UKGRU':   [  9,   13], # Ukupan broj grupa/paket
        'IZ909UKSLG':   [ 14,   19], # Ukupan broj slog/paket
        'IZ909REZ3':    [ 20,  997], # Rezerva
        'IZ909TIPSL':   [998, 1000], # Tip sloga
    }
    '999':{
        'IZ999REZ1':    [  1,  997], # Rezervirana mjesta
        'IZ999TIPSL':   [997, 1000], # Tip sloga – oznaka 999
    }
 }