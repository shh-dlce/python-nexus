"""Tests for TreeHandler"""
import pytest

from nexus.reader import NexusReader
from nexus.exceptions import NexusFormatException
from nexus.handlers.tree import TreeHandler


def test_block_find(trees):
    # did we get a tree block?
    assert 'trees' in trees.blocks


def test_treecount(trees):
    # did we find 3 trees?
    assert len(trees.blocks['trees'].trees) == 3
    assert trees.blocks['trees'].ntrees == 3
    assert len(trees.trees.trees) == 3
    assert trees.trees.ntrees == 3


def test_taxa(trees):
    expected = [
        'Chris', 'Bruce', 'Tom', 'Henry', 'Timothy', 'Mark', 'Simon',
        'Fred', 'Kevin', 'Roger', 'Michael', 'Andrew', 'David'
    ]
    assert len(trees.trees.taxa) == len(expected)
    for taxon in expected:
        assert taxon in trees.trees.taxa


def test_iterable(trees):
    assert list(trees.blocks['trees'])
    assert list(trees.trees)


def test_write(trees, examples):
    written = trees.trees.write()
    expected = examples.joinpath('example.trees').read_text(encoding='utf8')
    # remove leading header which isn't generated by .write()
    expected = expected.lstrip("#NEXUS\n\n")
    assert expected == written


def test_write_produces_end(trees):
    assert "end;" in trees.trees.write()
    assert len([_ for _ in trees.trees[0].newick_tree.walk()]) == 25


def test_block_findt(trees_translated):
    # did we get a tree block?
    assert 'trees' in trees_translated.blocks


def test_treecountt(trees_translated):
    # did we find 3 trees?
    assert len(trees_translated.blocks['trees'].trees) == 3
    assert trees_translated.blocks['trees'].ntrees == 3
    assert len(trees_translated.trees.trees) == 3
    assert trees_translated.trees.ntrees == 3


def test_iterablet(trees_translated):
    assert list(trees_translated.blocks['trees'])
    assert list(trees_translated.trees)


def test_taxat(trees_translated):
    expected = [
        'Chris', 'Bruce', 'Tom', 'Henry', 'Timothy', 'Mark', 'Simon',
        'Fred', 'Kevin', 'Roger', 'Michael', 'Andrew', 'David'
    ]
    assert len(trees_translated.trees.taxa) == len(expected)
    for taxon in expected:
        assert taxon in trees_translated.trees.taxa


def test_was_translated_flag_set(trees_translated):
    assert trees_translated.trees.was_translated


def test_parsing_sets_translators(trees_translated):
    assert len(trees_translated.trees.translators) == 13


def test_been_detranslated_flag_set(trees_translated):
    assert not trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()
    assert trees_translated.trees._been_detranslated


def test_writet(trees_translated, examples):
    assert not trees_translated.trees._been_detranslated
    written = trees_translated.trees.write()
    expected = examples.joinpath('example-translated.trees').read_text(encoding='utf8')
    # remove leading header which isn't generated by .write()
    expected = expected.lstrip("#NEXUS\n\n")
    # remove tabs since we reformat things a bit
    expected = expected.replace("\t", "").strip()
    written = written.replace("\t", "").strip()
    # handle the workaround for the beast bug
    expected = expected.replace("12 David;", "12 David\n;")
    assert expected == written, "%s\n----\n%s" % (expected, written)


def test_no_error_on_multiple_translate(trees_translated):
    assert not trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()
    assert trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()  # should not cause an error


def test_detranslate(trees_translated, examples):
    assert not trees_translated.trees._been_detranslated
    trees_translated.trees.detranslate()
    # should NOW be the same as tree 0 in example.trees
    other_tree_file = NexusReader(str(examples / 'example.trees'))
    assert other_tree_file.trees[0] == trees_translated.trees[0]


def test_treelabel():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree TREEONE = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree TREEONE = (0,1,2);']


def test_no_treelabel():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree = (0,1,2);']


def test_rooted():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree [&] = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree [&] = (0,1,2);']
    assert nex.trees.trees[0].rooted is None  # we only recognize [&R]!


def test_unrooted():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree [&U] = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree [&U] = (0,1,2);']
    assert nex.trees.trees[0].rooted is False


def test_labelled_unrooted():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree unrooted [U] = (0,1,2);
    end;
    """)
    assert len(nex.trees.trees) == 1
    assert nex.trees.trees == ['tree unrooted [U] = (0,1,2);']


def test_ok_starting_with_zero():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            0 Tom,
            1 Simon,
            2 Fred;
            tree tree = (0,1,2)
    end;
    """)
    assert len(nex.trees.translators) == 3
    assert '0' in nex.trees.translators
    assert '1' in nex.trees.translators
    assert '2' in nex.trees.translators


def test_ok_starting_with_one():
    nex = NexusReader.from_string("""
    #NEXUS

    begin trees;
        translate
            1 Tom,
            2 Simon,
            3 Fred;
            tree tree = (1,2,3)
    end;
    """)
    assert len(nex.trees.translators) == 3
    assert '1' in nex.trees.translators
    assert '2' in nex.trees.translators
    assert '3' in nex.trees.translators


def test_error_on_duplicate_taxa_id():
    with pytest.raises(NexusFormatException):
        NexusReader.from_string("""
        #NEXUS
    
        begin trees;
            translate
                0 Tom,
                1 Simon,
                1 Tom;
                tree tree = (0,1,2)
        end;
        """)


def test_error_on_duplicate_taxa():
    with pytest.raises(NexusFormatException):
        NexusReader.from_string("""
        #NEXUS
    
        begin trees;
            translate
                0 Tom,
                1 Simon,
                2 Tom;
                tree tree = (0,1,2)
        end;
        """)


def test_read_BEAST_format(trees_beast):
    assert trees_beast.trees[0].name == 'STATE_201000'
    assert len([_ for _ in trees_beast.trees[0].newick_tree.walk()]) == 75
    trees_beast.trees.detranslate()
    assert 'F38' in set(n.name for n in trees_beast.trees[0].newick_tree.walk())


def test_block_findb(trees_beast):
    # did we get a tree block?
    assert 'trees' in trees_beast.blocks


def test_taxab(trees_beast):
    expected = [
        "R1", "B2", "S3", "T4", "A5", "E6", "U7", "T8", "T9", "F10", "U11",
        "T12", "N13", "F14", "K15", "N16", "I17", "L18", "S19", "T20",
        "V21", "R22", "M23", "H24", "M25", "M26", "M27", "R28", "T29",
        "M30", "P31", "T32", "R33", "P34", "R35", "W36", "F37", "F38"
    ]
    assert len(trees_beast.trees.taxa) == len(expected)
    for taxon in expected:
        assert taxon in trees_beast.trees.taxa


def test_treecountb(trees_beast):
    assert len(trees_beast.blocks['trees'].trees) == 1
    assert trees_beast.blocks['trees'].ntrees == 1
    assert len(trees_beast.trees.trees) == 1
    assert trees_beast.trees.ntrees == 1


def test_flag_set(trees_beast):
    assert trees_beast.trees.was_translated


def test_parsing_sets_translatorsb(trees_beast):
    assert len(trees_beast.trees.translators) == 38


def test_detranslate_BEAST_format_extended(trees_beast):
    trees_beast.trees.detranslate()
    for index, taxon in trees_beast.trees.translators.items():
        # check if the taxon name is present in the tree...
        assert taxon in trees_beast.trees[0], \
            "Expecting taxon %s in tree description" % taxon
    assert trees_beast.trees._been_detranslated


@pytest.fixture
def findall():
    th = TreeHandler()
    return th._findall_chunks


def test_tree(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': 'Chris',
            'comment': None,
            'branch': None,
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': 'Bruce',
            'comment': None,
            'branch': None,
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': 'Tom',
            'comment': None,
            'branch': None,
            'end': ')'
        },
    }
    found = findall("tree a = ((Chris,Bruce),Tom);")
    assert len(found) == 3
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_tree_digits(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': '1',
            'comment': None,
            'branch': None,
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': '2',
            'comment': None,
            'branch': None,
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': '3',
            'comment': None,
            'branch': None,
            'end': ')'
        },
    }
    found = findall("tree a = ((1,2),3);")
    assert len(found) == 3
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_tree_with_branchlengths(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': '1',
            'comment': None,
            'branch': '0.1',
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': '2',
            'comment': None,
            'branch': '0.2',
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': '3',
            'comment': None,
            'branch': '0.3',
            'end': ')'
        },
    }
    found = findall("tree a = ((1:0.1,2:0.2):0.9,3:0.3):0.9;")
    assert len(found) == 3
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_tree_complex(findall):
    expected = {
        0: {
            'start': '(',
            'taxon': '1',
            'comment': '[&var=1]',
            'branch': '0.1',
            'end': ','
        },
        1: {
            'start': ',',
            'taxon': '2',
            'comment': '[&var=2]',
            'branch': '0.2',
            'end': ')'
        },
        2: {
            'start': ',',
            'taxon': '3',
            'comment': '[&var=4]',
            'branch': '0.3',
            'end': ')'
        },
    }
    found = findall(
        "tree a = ((1:[&var=1]0.1,2:[&var=2]0.2):[&var=3]0.9,3:[&var=4]0.3):[&var=5]0.9;"
    )
    assert len(found) == 3
    for match in expected:
        for key in expected[match]:
            assert expected[match][key] == found[match][key]


def test_no_change():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((Chris,Bruce),Tom);"
    newtree = "tree a = ((Chris,Bruce),Tom);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly NOT translate a simple tree"


def test_no_change_branchlengths():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
    newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly NOT translate a tree with branchlengths"


def test_change():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((0,1),2);"
    newtree = "tree a = ((Chris,Bruce),Tom);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a simple tree"


def test_change_branchlengths():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((0:0.1,1:0.2):0.3,2:0.4);"
    newtree = "tree a = ((Chris:0.1,Bruce:0.2):0.3,Tom:0.4);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a tree with branchlengths"


def test_change_comment():
    translatetable = {'0': 'Chris', '1': 'Bruce', '2': 'Tom'}
    oldtree = "tree a = ((0[x],1[y]),2[z]);"
    newtree = "tree a = ((Chris[x],Bruce[y]),Tom[z]);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a tree with branchlengths"


def test_BEAST_format():
    translatetable = {'1': 'Chris', '2': 'Bruce', '3': 'Tom'}
    oldtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((1:[&rate=1.0]48.056,3:[&rate=1.0]48.056):[&rate=1.0]161.121,2:[&rate=1.0]209.177);"
    newtree = "tree STATE_0 [&lnP=-584.441] = [&R] ((Chris:[&rate=1.0]48.056,Tom:[&rate=1.0]48.056):[&rate=1.0]161.121,Bruce:[&rate=1.0]209.177);"
    trans = TreeHandler()._detranslate_tree(oldtree, translatetable)
    assert trans == newtree, \
        "Unable to correctly detranslate a BEAST tree"
