row_defs={ 
    '300':{
        'S300DATSL':    [  1,    8], # Datum podnosenja/slanja datoteke
        'S300VRSTNAL':  [  9,    9], # Vrsta naloga u datoteci
        'S300IZDOK':    [ 10,   12], # Izvor dokumenta
        'S300REZERVA':  [ 13,  997], # Rezerva
        'S300TIPSLOG':  [998, 1000], # Tip sloga
    }  
    '301':{
        'S301IBANPLAT': [  1,   21], # IBAN platitelja
        'S301VALPL':    [ 22,   24], # Oznaka valute placanja
        'S301RNNAK':    [ 25,   45], # Racun naknade
        'S301VALNAK':   [ 46,   48], # Oznaka valute naknade
        'S301BRNALUK':  [ 49,   53], # Ukupan broj naloga u sljedecoj grupi (slogovi 309)
        'S301IZNNALUK': [ 54,   73], # Ukupan iznos naloga u sljedecoj grupi (slogovi 309)
        'S301DATIZVR':  [ 81,   74], # Datum izvrsenja naloga
        'S301REZERVA':  [ 82,  997], # Rezerva
        'S301TIPSLOG':  [998, 1000], # Tip sloga
    }
    '309':{
        'S309IBANRNPRIM':   [  1,   34], # IBAN ili racun primatelja
        'S309NAZIVPRIM':    [ 35,  104], # Naziv primatelja
        'S309ADRPRIM':      [105,  139], # Adresa primatelja
        'S309SJEDPRIM':     [140,  174], # Sjediste primatelja
        'S309SFZEMPRIM':    [175,  177], # Sifra zemlje primatelja
        'S309BRMODPLAT':    [178,  181], # Broj modela platitelja
        'S309PNBPLAT':      [182,  203], # Poziv na broj platitelja
        'S309SIFNAM':       [204,  207], # Sifra namjene
        'S309OPISPL':       [208,  347], # Opis placanja
        'S309IZN':          [348,  362], # Iznos
        'S309BRMODPRIM':    [363,  366], # Broj modela primatelja
        'S309PNBPRIM':      [367,  388], # Poziv na broj primatelja
        'S309BICBANPRIM':   [389,  399], # BIC (SWIFT) adresa
        'S309NAZBANPRIM':   [400,  469], # Naziv banke primatelja
        'S309ADRBNPRIM':    [470,  504], # Adresa banke primatelja
        'S309SJEDBNPRIM':   [505,  539], # Sjediste banke primatelja
        'S309SFZEMBNPRIM':  [540,  542], # Sifra zemlje banke primatelja
        'S309VRSTAPRIM':    [543,  543], # Vrsta strane osobe
        'S309VALPOKR':      [544,  546], # Valuta pokrica
        'S309TROSOP':       [547,  547], # Troskovna opcija
        'S309OZNHITN':      [548,  548], # Oznaka hitnosti
        'S309REZERVA':      [549,  997], # Rezerva
        'S309TIPSLOG':      [998, 1000], # Tip sloga   
    }
    '399':{
        'S399REZERVA':  [  1,  997], # Rezerva
        'S399PTIPSLOG': [998, 1000], # Tip sloga
    }
}