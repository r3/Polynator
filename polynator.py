"""
Author: Ryan Roler (ryan.roler@gmail.com)

This is...
        THE POLYNATOR!
this
"""

from functools import total_ordering
from functools import reduce
from operator import add
import string

#----------------------LOW PRIORITY--------------------------
#TODO: Plug in both Poly and Term need to accept **kwargs specifying in which
#      variable the input is to be plugged. Partial plugging should work.
#----------------------HIGH PRIORITY-------------------------
#TODO: Test/Fix Poly._simplify to allow for terms with either coefficients or
#      exponents or variables of '' and 0. This may already work. Test it.
#TODO: Setup addition and subtraction of polynomials
#TODO: Setup multiplication and division of terms
#TODO: Setup multiplication and division of polynomials
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

        return coefficient + variable + exponent

    def __lt__(self, other):
        if isinstance(other, Term):
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
        if (other.var == self.var) and (other.expo == self.expo):
            return Term(self.coeff + other.coeff, self.var, self.expo)
        else:
            raise ArithmeticError("Non-matching exponents")

    def __sub__(self, other):
        if (other.var == self.var) and (other.expo == self.expo):
            return Term(self.coeff - other.coeff, self.var, self.expo)
        else:
            raise ArithmeticError("Non-matching exponents")

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
        for term in self._linearize():
            if term < 0:
                rep.append('-')
                rep.append(str(term)[1:])  # Get rid of unnecessary signs
            else:
                rep.append('+')
                rep.append(str(term))
        if rep[0] == '+':
            rep.pop(0)
        return ' '.join(rep)

    def _simplify(self):
        for var in self.terms:
            for expo in self.terms[var]:
                self.terms[var][expo] = reduce(add, self.terms[var][expo])

    def _linearize(self):
        rep = []
        for var in self.terms.values():
            for term in var.values():
                rep.append(term)
        return sorted(rep, reverse=True)

    def plug(self, value):
        """Evaluate polynomial for x in f(x)"""
        return reduce(add, (x.plug(value) for x in self._linearize()))


def parse_term(inpt):
    """Parses input to create a Term
    Allows for both 4x^3 or 4x3, which will build equivilant
    Term objects.
    """

    def fix(num):
        # Sometimes, input for a part is missing, we fix that here
        if not num:
            return 1
        else:
            return int(num)

    # Grab any sign if it exists and truncate
    if inpt.startswith('-'):
        sign = -1
        inpt = inpt[1:]
    elif inpt.startswith('+'):
        sign = 1
        inpt = inpt[1:]
    else:
        sign = 1

    # Sometimes, the input will just be a coefficient or a variable
    if len(inpt) == 1:
        if inpt.isalpha():
            expon = 1
            var = inpt
            coeff = 1
        elif inpt.isdigit():
            expon = 0
            var = ''
            coeff = int(inpt)
        return Term(sign * coeff, var, expon)

    # Caret character used to denote existing exponent (4x^6 form)
    try:
        found = inpt.index('^')
        expon = fix(inpt[found + 1:])
        var = inpt[found - 1]
        coeff = fix(inpt[:found - 1])

    # Exponent part not noted by caret character (4x6 form)
    except ValueError:
        # Find first string character and assume it's the variable
        for index, value in enumerate(inpt):
            if value.isalpha():
                found = index
                var = inpt[found]
                break
        # Anything before the variable should be the coefficient
        try:
            coeff = fix(inpt[:found])
        except ValueError:
            raise SyntaxError("Input not valid")

        # Anything after variable should be an exponent
        if len(inpt) > found:
            try:
                expon = fix(inpt[found + 1:])
            except ValueError:
                raise SyntaxError("Input not valid")
        else:
            expon = 1

    return Term(sign * coeff, var, expon)


def parse_poly(inpt):
    """Parses input to create a Poly"""
    chunk = []
    terms = []
    for item in inpt:
        if item in string.whitespace:
            pass
        elif item in ['+', '-']:
            terms.append(parse_term(''.join(chunk)))
            chunk = [item]
        else:
            chunk.append(item)
    terms.append(parse_term(''.join(chunk)))
    return Poly(*terms)

if __name__ == '__main__':
    pass
