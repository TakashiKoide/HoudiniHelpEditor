# -*- coding: utf-8 -*-
import sys
import codecs
sys.dont_write_bytecode = True
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
