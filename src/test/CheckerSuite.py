import unittest
from TestUtils import TestChecker
from Visitor import Visitor
from StaticError import *
from AST import *
from abc import ABC


class CheckerSuite(unittest.TestCase):
    def test_basicUndeclared_Identifier(self):
        input = """
        i, j: integer;
        foo: function integer (i:integer, c: auto) {
            arr: auto = {1,2,3};
        }
        main: function void () inherit foo {
            super(5,6);
        }
        """
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 401))
