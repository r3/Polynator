"""
Author: Ryan Roler (ryan.roler@gmail.com)
This is...  THE POLYNATOR!
"""

from functools import total_ordering
from functools import reduce
from operator import add
import string

#----------------------LOW PRIORITY--------------------------
#TODO: In the case of multiple variables, I'd need to store multiple exponents,
#      one for each variable.
#TODO: Plug in both Poly and Term need to accept **kwargs specifying in which
#      variable the input is to be plugged. Partial plugging should work.
#----------------------HIGH PRIORITY-------------------------
#TODO: Parse_poly doesn't handle negative exponents
#TODO: Setup division of terms
#TODO: Setup division of polynomials
#TODO: Allow for a means of operators inputting polynomials and operations
#      using either a full line input, reverse polish notation, or something


@total_ordering
class Term():
    """Term objects represent terms in a polynomial
    An example of a term: 4x^3
    Such a term would be instantiated by passing
    the integer coefficient, a string type Variable
    of one letter, and an integer exponent.
    """

    def __init__(self, coeff, var, expo):
        assert isinstance(coeff, int)
        assert isinstance(expo, int)
        assert isinstance(var, str)

        if coeff == 0:
            self.coeff = 0
            self.var = ''
            self.expo = 0
        else:
            self.coeff = coeff
            self.var = var.lower()
            self.expo = expo

    def __str__(self):
        # Coefficient string construction
        if self.coeff == -1:
            coefficient = '-'
        elif self.coeff and self.coeff != 1:
            coefficient = str(self.coeff)
        elif self.coeff and not self.expo and not self.var:
            coefficient = str(self.coeff)
        else:
            coefficient = ''

        # Variable string construction
        if self.var and (self.expo != 0):
            variable = self.var
        else:
            variable = ''

        # Exponent string construction
        if self.expo and (self.expo != 0) and (self.expo != 1):
            exponent = '^' + str(self.expo)
        else:
            exponent = ''

        # Bring it on home.
        if not coefficient and not variable and not exponent:
            return '0'
        else:
            return coefficient + variable + exponent

    def __lt__(self, other):
        if isinstance(other, Term):
            if self.expo == other.expo:
                if self.var == other.var:
                    return self.coeff < other.coeff
                else:
                    return self.var < other.var
            else:
                return self.expo < other.expo
        elif other == 0:
            return self.coeff < 0
        elif isinstance(other, int):
            return False
        else:
            raise TypeError("These types cannot be compared")

    def __eq__(self, other):
        if isinstance(other, Term):
            return self.__dict__ == other.__dict__
        elif other == 0:
            return self.coeff == 0
        elif isinstance(other, int):
            return False
        else:
            raise TypeError("These types cannot be compared")

    def __add__(self, other):
        if isinstance(other, Term):
            if (other.var == self.var) and (other.expo == self.expo):
                return Term(self.coeff + other.coeff, self.var, self.expo)
            else:
                raise ArithmeticError("Non-matching exponents")
        else:
            raise TypeError("Incompatible types")

    def __sub__(self, other):
        if isinstance(other, Term):
            if (other.var == self.var) and (other.expo == self.expo):
                return Term(self.coeff - other.coeff, self.var, self.expo)
            else:
                raise ArithmeticError("Non-matching exponents")
        else:
            raise TypeError("Incompatible types")

    def __mul__(self, other):
        if isinstance(other, Term):
            if not other.var:
                variable = self.var
                exponent = self.expo
            else:
                variable = self.var
                exponent = self.expo + other.expo
            coefficient = self.coeff * other.coeff
            return Term(coefficient, variable, exponent)
        elif isinstance(other, int):
            return Term(self.coeff * other, self.var, self.expo)
        elif self.var == other:
            return Term(self.coeff, self.var, self.expo + 1)
        else:
            raise TypeError("Incompatible types")

    def __div__(self, other):
        if isinstance(other, Term):
            if self.var == other.var:
                coefficient = self.coeff / other.coeff

    def plug(self, value):
        """Determine value of term given x for f(x)"""
        return self.coeff * (value ** self.expo)


class Poly():
    """Poly objects represent polynomials.
    These are ordered collections of Term objects.
    Any number of Term objects can be passed as
    arguments when instantiating. Non-Term objects
    passed as arguments will be ignored.
    """

    def __init__(self, *args):
        """Store terms in a top-level dict keyed by var, in a lower-level
        dict keyed by the term's exponents: {VAR : {EXPONENT : [TERM OBJECTS]}}
        """

        self.terms = dict()
        for term in args:
            if isinstance(term, Term):
                self.terms.setdefault(term.var, {}).setdefault(
                                      term.expo, []).append(term)
        self._simplify()

    def __str__(self):
        rep = []
        for term in self:
            if not term.coeff and not term.var:
                pass
            elif term < 0:
                rep.append('-')
                rep.append(str(term)[1:])  # Get rid of unnecessary signs
            else:
                rep.append('+')
                rep.append(str(term))
        if rep[0] == '+':
            rep.pop(0)
        return ' '.join(rep)

    def __add__(self, other):
        if isinstance(other, Poly):
            res = []
            for term in self:
                res.append(term)
            for term in other:
                res.append(term)
            return Poly(*res)
        elif isinstance(other, int):
            return Poly(*(list(self) + [other]))
        else:
            raise ArithmeticError("Incompatible Types")

    def __sub__(self, other):
        if isinstance(other, Poly):
            for term in other:
                term.coeff *= -1
            return self + other
        elif isinstance(other, int):
            return Poly(*(list(self) - [other]))

    def __mul__(self, other):
        res = []
        if isinstance(other, Poly):
            for multiplicand in self:
                for multiplier in other:
                    res.append(multiplicand * multiplier)
        elif isinstance(other, (int, Term, str)):
            for term in self:
                res.append(term * other)
        return Poly(*res)

    def __iter__(self):
        rep = []
        for var in self.terms.values():
            for term in var.values():
                rep.append(term)
        return iter(sorted(rep, reverse=True))

    def _simplify(self):
        for var in self.terms:
            for expo in self.terms[var]:
                self.terms[var][expo] = reduce(add, self.terms[var][expo])

    def plug(self, value):
        """Evaluate polynomial for x in f(x)"""
        return reduce(add, (x.plug(value) for x in self._linearize()))


def parse_term(inpt):
    """Parses input to create a Term
    Allows for both 4x^3 or 4x3, which will build equivilant
    Term objects.
    """

    def fix(num):
        if num == '-':
            return -1
        elif num:
            try:
                return int(num)
            except ValueError:
                raise SyntaxError("Improper input formatting ({})".format(num))
        else:
            return 1

    inpt = ''.join([x for x in inpt if x != '^'])
    coeff = ''
    var = ''
    expo = ''

    for item in inpt:
        if item.isdigit() and var:
            expo += item
        elif item.isdigit():
            coeff += item
        elif item.isalpha():
            var += item
        elif item in ('-', '+'):
            if var and item not in expo:
                expo = item + expo
            elif item not in coeff:
                coeff = item + coeff
            else:
                pass
        else:
            raise SyntaxError("Improper input formatting ({}).".format(item))

    coeff = fix(coeff)
    expo = fix(expo)

    return Term(coeff, var, expo)


def parse_poly(inpt):
    """Parses input to create a Poly"""
    chunk = []
    terms = []
    for item in inpt:
        if item in string.whitespace:
            pass
        elif item in ['+', '-'] and chunk:
            terms.append(parse_term(''.join(chunk)))
            chunk = [item]
        else:
            chunk.append(item)
    terms.append(parse_term(''.join(chunk)))
    return Poly(*terms)

if __name__ == '__main__':
    pass
