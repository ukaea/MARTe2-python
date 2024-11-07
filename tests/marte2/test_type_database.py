import pdb
import pytest
import shutil
import os

from martepy.marte2.type_database import *

from ..utilities import top_lvl

def test_field_cls():
    field = Field('Hello','uint32',2,'World')
    assert field.comment == 'World'
    assert field.name == 'Hello'
    assert field.type == 'uint32'
    assert field.noelements == 2

    assert not field == Field('Hellob','uint64',1,'World')
    assert not field == list([])
    assert field == Field('Hello','uint32',2,'World')

def test_type_cls():
    type_obj = Type('uinty',False, 'uinty.h','2_0')
    assert type_obj.fundamental == False
    assert type_obj.name == 'uinty'
    assert type_obj.file == 'uinty.h'
    assert type_obj.version == '2_0'
    assert type_obj.fields == []

    field = Field('Hello','uint32',2,'World')
    type_obj.addField(field)

    assert type_obj.fields == [field]

    assert not type_obj == Type('uintyf',False, 'uinty.h','2_0')
    assert not type_obj == list([])
    compare_type = Type('uinty',False, 'uinty.h','2_0')
    compare_type.addField(field)
    assert type_obj == compare_type

def test_const_cls():
    const = Constant('RTPS_HEAD', '1', 'Hello World')
    assert const.comments == 'Hello World'
    assert const.name == 'RTPS_HEAD'
    assert const.value == '1'

def test_type_db_interface():
    test_db = TypeDBv2()
    test_db.loadDb(os.path.join(top_lvl, 'tests','marte2','headers'))

    # Test a few aspects
    assert test_db.definitions['RTPS_STAT_UNDEFINED'].value == 0
    assert test_db.definitions['KC1E_kc1e_METADATA'].value == 7

    assert test_db.types['belmPkt'].fields[1].name == 'sampleTime'
    assert test_db.types['belmPkt'].fields[1].type == 'uint32'

    assert test_db.types['belmPkt'].version == '2_2'
    assert test_db.types['belmPkt'].file.split('/')[-1] == 'BELM_2_2.h'

    assert not test_db == TypeDBv2()
    assert not test_db == list([])
    
    compare_db = TypeDBv2()
    compare_db.loadDb(os.path.join(top_lvl, 'tests','marte2','headers'))

    assert test_db == compare_db

    assert test_db.isFundamental('uint32')
    assert test_db.isFundamental('int32')
    assert test_db.isFundamental('float32')
    assert test_db.isFundamental('int16')

    assert not test_db.isFundamental('uinty')
    assert not test_db.isFundamental('belmPkt')

    assert test_db.getTypeByName('belmPkt') == test_db.types['belmPkt']

    with pytest.raises(TypeException) as excinfo:
        test_db.getTypeByName('uinty')

def test_type_toLibrary():
    test_db = TypeDBv2()
    test_db.loadDb(os.path.join(top_lvl, 'tests','marte2','headers'))

    output_path = os.path.join(top_lvl, 'tests','marte2','headers_out')
    test_db.toLibrary(output_path)

    def assert_packet_out(packet_name):
        packet_folder = os.path.join(output_path, packet_name)
        assert os.path.exists(packet_folder)
        assert os.path.exists(os.path.join(packet_folder, 'Makefile.gcc'))
        assert os.path.exists(os.path.join(packet_folder, 'Makefile.inc'))
        assert os.path.exists(os.path.join(packet_folder, f'{packet_name}.h'))
        assert os.path.exists(os.path.join(packet_folder, f'{packet_name}.cpp'))

    packets = ['aelmPkt', 'belmPkt', 'kc1e']
    for packet in packets:
        assert_packet_out(packet)

def test_genStruct():
    test_db = TypeDBv2()
    type_obj = Type('uinty',False, 'uinty.h','2_0')
    assert type_obj.fundamental == False
    assert type_obj.name == 'uinty'
    assert type_obj.file == 'uinty.h'
    assert type_obj.version == '2_0'
    assert type_obj.fields == []

    field = Field('Hello','uint32',2,'World')
    type_obj.addField(field)
    
    type_struct = test_db._generateStructDefinition(type_obj)
    assert type_struct == 'typedef struct {\n    uint32 Hello[2];\n} uinty;'
    
def test_incrementV():
    test_db = TypeDBv2()
    assert test_db.incrementVersion('1_2') == '1_3'

def test_changes_new():
    test_db = TypeDBv2()
    old_db = os.path.join(top_lvl, 'tests','marte2','headers')
    new_db = os.path.join(top_lvl, 'tests','marte2','new_headers')
    if os.path.exists(new_db):
        shutil.rmtree(new_db)
    shutil.copytree(old_db,new_db)
    test_db.loadDb(new_db)
    
    type_obj = Type('uinty',False, os.path.join(new_db,'uinty_2_0.h'),'2_0')
    assert type_obj.fundamental == False
    assert type_obj.name == 'uinty'
    assert type_obj.file == os.path.join(new_db,'uinty_2_0.h')
    assert type_obj.version == '2_0'
    assert type_obj.fields == []

    field = Field('Hello','uint32',2,'World')
    type_obj.addField(field)
    
    test_db.types['uinty'] = type_obj
    
    test_db.updateDb(new_db)
    
    with open(type_obj.file, 'r', encoding='utf-8') as infile:
        contents = infile.read()

    assert contents.split('*/',maxsplit=1)[1] == '''

#ifndef _uinty_H
#define _uinty_H



/**
 * uinty packet.
 */

typedef struct {
    uint32 Hello[2];
} uinty;

#endif /* _uinty_H */
'''

def test_changes_update():
    test_db = TypeDBv2()
    old_db = os.path.join(top_lvl, 'tests','marte2','headers')
    new_db = os.path.join(top_lvl, 'tests','marte2','new_headers')
    if os.path.exists(new_db):
        shutil.rmtree(new_db)
    shutil.copytree(old_db,new_db)
    test_db.loadDb(new_db)
    
    test_db.types['aelmPkt'].fields[0].name = 'seq'
    test_db.updateDb(new_db)
    with open(os.path.join(new_db, 'AELM_2_9.h'), 'r', encoding='utf-8') as infile:
        contents = infile.read()
        
    assert contents == '''/*
 * DO NOT EDIT THIS FILE.
 * Automatically generated from /home/RTDNdb-man/PIW/uploads/ccl/AELM/AELM_2_2.ccl at 16:51:06 16/08/21 by astephen
 * via program ccl4rtdn version 1 SU 21331
 * for the AELM system
 * RTDN ID version:- 488000002
 * RTDN version:- 2
 * aelmPkt metadata version:- 2
 */

#ifndef _aelmPkt_H
#define _aelmPkt_H

#include <stdrtdn.h>



/**
 * AELM RTDN packet.
 */

typedef struct {
    uint32 seq;
    uint32 sampleTime;
    uint32 available[3];
    uint32 saturated[5];
    float32 RFdevHz[488];
    float32 AEfreq;
    float32 DampingRaw;
    float32 DampingNorm;
    float32 TimeDamping;
    uint32 RFdevHz_sta;
    uint32 AEfreq_sta;
    uint32 DampingRaw_sta;
    uint32 DampingNorm_sta;
    uint32 TimeDamping_sta;
    uint32 aelmPkt_488000002;
} aelmPkt;

#define RTDN_aelmPkt_PVC 488

#define RTDN_aelmPkt_ID 488000002

#define RTDN_aelmPkt_VERSION 2

#define AELM_aelmPkt_METADATA 2

#define GET_RTDN_aelmPkt_ID(p) ((p)->aelmPkt_488000002)
#define SET_RTDN_aelmPkt_ID(p) ((p)->aelmPkt_488000002 = 488000002)
#define IS_RTDN_aelmPkt_PKT(p) ((p)->aelmPkt_488000002 == 488000002)

#endif /* _aelmPkt_H */
'''

def test_changes_updateV():
    test_db = TypeDBv2()
    old_db = os.path.join(top_lvl, 'tests','marte2','headers')
    new_db = os.path.join(top_lvl, 'tests','marte2','new_headers')
    if os.path.exists(new_db):
        shutil.rmtree(new_db)
    shutil.copytree(old_db,new_db)
    test_db.loadDb(new_db)
    test_db.updateFileVersion(os.path.join(new_db, 'AELM_2_8.h'), '4_1')
    assert os.path.exists(os.path.join(new_db, 'AELM_4_1.h'))


