import struct, zlib

# CRC-16 FIT
_CRC=[0x0000,0xCC01,0xD801,0x1400,0xF001,0x3C00,0x2800,0xE401,
      0xA001,0x6C00,0x7800,0xB401,0x5000,0x9C01,0x8801,0x4400]
def fit_crc(data):
    crc=0
    for byte in data:
        t=_CRC[crc & 0xF]; crc=(crc>>4)&0x0FFF; crc=crc ^ t ^ _CRC[byte & 0xF]
        t=_CRC[crc & 0xF]; crc=(crc>>4)&0x0FFF; crc=crc ^ t ^ _CRC[(byte>>4)&0xF]
    return crc & 0xFFFF

TIME_CREATED=1150265753  # constante reprise des fichiers S25

# Helpers allure -> vitesse m/s*1000 (FIT). pace en "m:ss"/km -> m/s
def pace_to_speed(pace):
    # pace "5:20" -> sec/km -> m/s*1000
    m,s=pace.split(':'); sec=int(m)*60+int(s)
    return round((1000.0/sec)*1000)

# ---- Construction d'un step ----
# kind: 'warmup','active','rest','cooldown'
# dur: ('time', seconds) ou ('distance', meters) ou ('open',)
# target: None | ('speed', low_pace, high_pace) | ('hr', low_bpm, high_bpm)
def step(name, kind, dur, target=None):
    return {'name':name,'kind':kind,'dur':dur,'target':target}
def repeat(from_index, count, name='Repetitions'):
    return {'repeat':True,'name':name,'from':from_index,'count':count}

INTENSITY={'active':0,'rest':1,'warmup':2,'cooldown':3}

def _string_field(s, size):
    b=s.encode('utf-8')[:size-1]
    return b + b'\x00'*(size-len(b))

def build_workout(wkt_name, steps, serial):
    """Retourne les octets data (records) d'un workout FIT, hors header/CRC."""
    out=bytearray()
    # --- file_id (gmsg 0) ---
    # DEF local0
    out+=bytes([0x40,0x00,0x00]) + struct.pack('<H',0) + bytes([5])
    out+=bytes([0,1,0, 1,2,132, 2,2,132, 3,4,140, 4,4,134])
    # DATA: type=5,manuf=1,product=0,serial,time_created
    out+=bytes([0x00]) + bytes([5]) + struct.pack('<H',1) + struct.pack('<H',0) + struct.pack('<I',serial) + struct.pack('<I',TIME_CREATED)
    # --- workout (gmsg 26) ---
    num_steps=len(steps)
    out+=bytes([0x40,0x00,0x00]) + struct.pack('<H',26) + bytes([3])
    out+=bytes([4,1,0, 6,2,132, 8,24,7])
    out+=bytes([0x00]) + bytes([1]) + struct.pack('<H',num_steps) + _string_field(wkt_name,24)
    # --- workout_step (gmsg 27) ---
    # On émet une définition adaptée par "forme" de step pour coller au style S25.
    # Champs possibles: 254 msg_index, 0 name, 1 dur_type, 2 dur_value, 3 tgt_type, 4 tgt_value, 5 cust_low, 6 cust_high, 7 intensity
    last_def=None
    for idx,s in enumerate(steps):
        if s.get('repeat'):
            fields=[(254,2,132),(0,len(_string_field(s['name'],0) or b'')+0,7)]  # placeholder, recompute below
            name_b=s['name'].encode('utf-8')+b'\x00'
            nsz=len(name_b)
            fielddef=[(254,2,132),(0,nsz,7),(1,1,0),(2,4,134),(3,1,0),(4,4,134),(7,1,0)]
            if fielddef!=last_def:
                out+=bytes([0x40,0x00,0x00])+struct.pack('<H',27)+bytes([len(fielddef)])
                for fn,fs,ft in fielddef: out+=bytes([fn,fs,ft])
                last_def=fielddef
            out+=bytes([0x00])+struct.pack('<H',idx)+name_b+bytes([6])+struct.pack('<I',s['from'])+bytes([2])+struct.pack('<I',s['count'])+bytes([0])
            continue
        name_b=s['name'].encode('utf-8')+b'\x00'; nsz=len(name_b)
        dur=s['dur']; tgt=s['target']; inten=INTENSITY[s['kind']]
        if dur[0]=='time': dtype,dval=0,int(round(dur[1]*1000))  # FIT: durée temps en millisecondes
        elif dur[0]=='distance': dtype,dval=1,int(dur[1]*100)  # distance en cm
        else: dtype,dval=5,0  # open
        if tgt is None:
            fielddef=[(254,2,132),(0,nsz,7),(1,1,0),(2,4,134),(3,1,0),(7,1,0)]
            if fielddef!=last_def:
                out+=bytes([0x40,0x00,0x00])+struct.pack('<H',27)+bytes([len(fielddef)])
                for fn,fs,ft in fielddef: out+=bytes([fn,fs,ft])
                last_def=fielddef
            out+=bytes([0x00])+struct.pack('<H',idx)+name_b+bytes([dtype])+struct.pack('<I',dval)+bytes([2])+bytes([inten])
        else:
            if tgt[0]=='speed':
                ttype=0; low=pace_to_speed(tgt[1]); high=pace_to_speed(tgt[2])
            else:  # hr
                ttype=1; low=tgt[1]+100; high=tgt[2]+100  # FIT custom HR = bpm+100
            fielddef=[(254,2,132),(0,nsz,7),(1,1,0),(2,4,134),(3,1,0),(4,4,134),(5,4,134),(6,4,134),(7,1,0)]
            if fielddef!=last_def:
                out+=bytes([0x40,0x00,0x00])+struct.pack('<H',27)+bytes([len(fielddef)])
                for fn,fs,ft in fielddef: out+=bytes([fn,fs,ft])
                last_def=fielddef
            out+=bytes([0x00])+struct.pack('<H',idx)+name_b+bytes([dtype])+struct.pack('<I',dval)+bytes([0])+struct.pack('<I',0)+struct.pack('<I',low)+struct.pack('<I',high)+bytes([inten])
    return bytes(out)

def fit_file(wkt_name, steps, serial):
    data=build_workout(wkt_name, steps, serial)
    header=bytes([12,0x23])+struct.pack('<H',2160)+struct.pack('<I',len(data))+b'.FIT'
    crc=fit_crc(header+data)
    return header+data+struct.pack('<H',crc)

if __name__=='__main__':
    # Validation: recalcul du CRC des fichiers de référence
    import sys
    for fn in ['fit_ref/S25-3-allure-marathon.fit','fit_ref/S25-1-footing-lignes.fit',
               'fit_ref/S25-2-footing-facile.fit','fit_ref/S25-4-sortie-longue.fit']:
        b=open(fn,'rb').read()
        recalc=fit_crc(b[:-2]); stored=struct.unpack('<H',b[-2:])[0]
        print(f"{fn}: CRC stored={stored:#06x} recalc={recalc:#06x} {'OK' if recalc==stored else 'FAIL'}")
