"""Tests for nexus reading"""
import gzip
import pathlib

import pytest

from nexus.reader import NexusReader
from nexus.exceptions import NexusFormatException


@pytest.fixture
def nex_string(examples):
    return examples.joinpath('example.nex').read_text(encoding='utf8')


"""Test the Core functionality of NexusReader"""
def test_read_file(nex):
    assert 'data' in nex.blocks
    assert 'Simon' in nex.blocks['data'].matrix


def test_error_on_missing_file(examples):
    with pytest.raises(IOError):
        NexusReader(examples / 'sausage.nex')


def test_read_gzip_file(nex_string, tmpdir):
    # first, MAKE a gzip file
    with gzip.open(str(tmpdir.join('f.gz')), 'wb') as h:
        h.write(nex_string.encode('utf8'))

    # test it's ok
    nex = NexusReader(str(tmpdir.join('f.gz')))
    assert 'data' in nex.blocks
    assert 'Simon' in nex.blocks['data'].matrix


def test_read_string(nex_string):
    nex = NexusReader()
    nex.read_string(nex_string)
    assert 'data' in nex.blocks
    assert 'Simon' in nex.blocks['data'].matrix


def test_read_string_returns_self():
    nex = NexusReader().read_string(
        """
        #NEXUS
        
        Begin data;
        Dimensions ntax=1 nchar=1;
        Format datatype=standard symbols="01" gap=-;
        Matrix
        Harry              1
        ;
    """)
    assert isinstance(nex, NexusReader)


def test_write(examples):
    nex = NexusReader(examples / 'example.trees')
    assert examples.joinpath('example.trees').read_text(encoding='utf8') == nex.write()


def test_write_to_file(nex, tmpdir):
    tmp = pathlib.Path(str(tmpdir.join('f.nex')))
    nex.write_to_file(tmp)
    assert tmp.is_file()

    n2 = NexusReader(tmp)
    assert n2.data.matrix == nex.data.matrix
    assert sorted(n2.data.taxa) == sorted(nex.data.taxa)


def test_error_on_duplicate_block():
    with pytest.raises(NexusFormatException):
        NexusReader().read_string(
            """
            #NEXUS
            
            Begin data;
            Dimensions ntax=5 nchar=1;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              1
            ;
            
            Begin data;
            Dimensions ntax=5 nchar=1;
            Format datatype=standard symbols="01" gap=-;
            Matrix
            Harry              1
            """)
