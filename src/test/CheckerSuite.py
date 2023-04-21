import unittest
from TestUtils import TestChecker
from Visitor import Visitor
from StaticError import *
from AST import *
from abc import ABC


class CheckerSuite(unittest.TestCase):
    def test_basicUndeclared_Identifier(self):
        input = """
        i, j:integer = 5, 6;
        foo: function integer (a:integer, b: float) {
            for(i = 1, i < 10, i + 1) {
                for(j = 1, j < 1000, j + 2) {
                     break;
                }
            }
        }
        main: function void () {
            return 0;
        }
        """
        expect = ""
        self.assertTrue(TestChecker.test(input, expect, 401))
