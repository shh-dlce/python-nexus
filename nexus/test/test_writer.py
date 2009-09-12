import re
import copy
import nose
from writer import NexusWriter

data = {
    'char1': {'French': 1, 'English': 2, 'Latin': 3},
    'char2': {'French': 4, 'English': 5, 'Latin': 6},

}

class Test_NexusWriter_1:
    def setup(self):
        self.nex = NexusWriter()
        
    def test_char_adding1(self):
        """Test Character Addition 1"""
        for tx, value in data['char1'].iteritems():
            self.nex.add(tx, 'char1', value)
        assert self.nex.data['char1']['French'] == '1'
        assert self.nex.data['char1']['English'] == '2'
        assert self.nex.data['char1']['Latin'] == '3'
        
    def test_char_adding2(self):
        """Test Character Addition 2"""
        for tx, value in data['char2'].iteritems():
            self.nex.add(tx, 'char2', value)
        assert self.nex.data['char2']['French'] == '4'
        assert self.nex.data['char2']['English'] == '5'
        assert self.nex.data['char2']['Latin'] == '6'
        

class Test_NexusWriter_2:
    def setup(self):
        self.nex = NexusWriter()
        for char, b in data.iteritems():
            for taxon, value in b.iteritems():
                self.nex.add(taxon, char, value)

    def test_nexus_noninterleave(self):
        """Test Nexus Generation - Non-Interleaved"""
        n = self.nex.make_nexus(interleave=False)
        assert re.search("#NEXUS", n)
        assert re.search("BEGIN DATA;", n)
        assert re.search("DIMENSIONS NTAX=3 NCHAR=2;", n)
        assert re.search("CHARSTATELABELS", n)
        assert re.search("1 char1,", n)
        assert re.search("2 char2", n)
        assert re.search("MATRIX", n)
        assert re.search("Latin\s+36", n)
        assert re.search("French\s+14", n)
        assert re.search("English\s+25", n)
        assert re.search("FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
        assert re.search("FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] == 'STANDARD'
        assert re.search("FORMAT.*SYMBOLS\=(\d+);", n).groups()[0] == '123456'
        
    def test_nexus_interleave(self):
        """Test Nexus Generation - Interleaved"""
        n = self.nex.make_nexus(interleave=True)
        assert re.search("#NEXUS", n)
        assert re.search("BEGIN DATA;", n)
        assert re.search("DIMENSIONS NTAX=3 NCHAR=2;", n)
        assert re.search("CHARSTATELABELS", n)
        assert re.search("1 char1,", n)
        assert re.search("2 char2", n)
        assert re.search("MATRIX", n)
        # char1
        assert re.search("Latin\s+3", n)
        assert re.search("French\s+1", n)
        assert re.search("English\s+2", n)
        # char2
        assert re.search("Latin\s+6", n)
        assert re.search("French\s+4", n)
        assert re.search("English\s+5", n)
        
        assert re.search("FORMAT.*MISSING\=(.+?)", n).groups()[0] == '?'
        assert re.search("FORMAT.*DATATYPE\=(\w+)\s", n).groups()[0] == 'STANDARD'
        assert re.search("FORMAT.*SYMBOLS\=(\d+);", n).groups()[0] == '123456'
        assert re.search("FORMAT.*(INTERLEAVE)", n).groups()[0] == 'INTERLEAVE'


class Test_NexusWriter_Binary:
    def setup(self):
        self.nex = NexusWriter()
        for char, b in data.iteritems():
            for taxon, value in b.iteritems():
                self.nex.add(taxon, char, value)
    
    def test_to_binary(self):
        """Test Nexus -> Binary: Two Character"""
        n = copy.deepcopy(self.nex)
        n.recode_to_binary()
        
        assert n.data['char1']['French'] == '100'
        assert n.data['char1']['English'] == '010'
        assert n.data['char1']['Latin'] == '001'
        
        assert n.data['char2']['French'] == '100'
        assert n.data['char2']['English'] == '010'
        assert n.data['char2']['Latin'] == '001'
        
    def test_to_binary_symbollist(self):
        """Test Nexus -> Binary: Update Symbol List"""
        n = copy.deepcopy(self.nex)
        n.recode_to_binary()
        
        # check symbol list was updated
        assert len(n.symbols) == 2
        assert '1' in n.symbols
        assert '0' in n.symbols
        
    def test_to_binary_combined(self):
        """Test Nexus -> Binary: Three Character, extra state"""
        n = copy.deepcopy(self.nex)
        # add some more data...
        n.add('French', 3, 'A')
        n.add('Latin', 3, 'A')
        n.add('English', 3, 'B')
        n.recode_to_binary()
        assert n.data['3']['Latin'] == '10'
        assert n.data['3']['French'] == '10'
        assert n.data['3']['English'] == '01'
        
    def test_to_binary_missingdata(self):
        """Test Nexus -> Binary: Three Character, missing data"""
        n = copy.deepcopy(self.nex)
        # add some more data...
        n.add('French', 3, 'A')
        n.add('Latin', 3, 'A')
        # no English state for char 3...
        n.recode_to_binary()
        assert re.search("English\s+\?", n.make_nexus())
    
    @nose.tools.raises(AssertionError)
    def test_is_binary_dirtycheck(self):
        """Test Nexus -> Binary: is_binary dirty check"""
        n = copy.deepcopy(self.nex)
        n.recode_to_binary()
        n.add('French', 4, 'A') # should raise AssertionError
        
        