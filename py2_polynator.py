"""
Author: Ryan Roler (ryan.roler@gmail.com)
This is...  THE POLYNATOR!
"""

from functools import total_ordering
from functools import reduce
from operator import add
from copy import copy
import string

#----------------------LOW PRIORITY--------------------------
#TODO: Plug in both Poly and Term need to accept **kwargs specifying in which
#      variable the input is to be plugged. Still works for 'x' vars.
#----------------------HIGH PRIORITY-------------------------
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

    def __init__(self, coeff=0.0, var='', expo=0):
        if len(var) > 1:
            var = var[-1]
            print "Allows for single variables only, using '{}'".format(var)
        self.coeff = float(coeff)
        self.var = var.lower()
        self.expo = expo

        if coeff in (0, 0.0):
            self.var = ''
            self.expo = 0
        elif expo == 0:
            self.var = ''
        elif var == '':
            self.expo = 1

    def __str__(self):
        def coeff_format():
            if self.coeff.is_integer():
                return str(int(self.coeff))
            else:
                return "{:.3}".format(self.coeff)

        # Coefficient string construction
        if (coeff_format() == '-1') and self.var:
            coefficient = '-'
        elif self.coeff and (coeff_format() != '1'):
            coefficient = coeff_format()
        elif self.coeff and not self.var and (self.expo == 1):
            coefficient = coeff_format()
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
            if self.var == other.var:
                if self.expo == other.expo:
                    return self.coeff < other.coeff
                else:
                    return self.expo < other.expo
            else:
                return self.var < other.var
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
                raise ValueError("Non-matching exponents")
        else:
            raise TypeError("Incompatible types")

    def __sub__(self, other):
        if isinstance(other, Term):
            if (other.var == self.var) and (other.expo == self.expo):
                return Term(self.coeff - other.coeff, self.var, self.expo)
            else:
                raise ValueError("Non-matching exponents")
        else:
            raise TypeError("Incompatible types")

    def __mul__(self, other):
        if isinstance(other, Term):
            if not other.var:
                variable = self.var
                exponent = self.expo
            elif other.var == self.var:
                variable = self.var
                exponent = self.expo + other.expo
            else:
                variable = other.var
                exponent = other.expo
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
            coefficient = self.coeff / other.coeff
            variable = self.var
            if self.var == other.var:
                exponent = self.expo - other.expo
            else:
                exponent = self.expo
        elif isinstance(other, (int, float)):
            coefficient = self.coeff / other
            variable = self.var
            exponent = self.expo
        else:
            raise TypeError("Incompatible types")
        return Term(coefficient, variable, exponent)

    def plug(self, value):
        """Determine value of term given x for f(x)"""
        return self.coeff * (value ** self.expo)


@total_ordering
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
        self.__simplify()

    def __str__(self):
        rep = []
        for term in self:
            if not term.coeff and not term.var:
                pass
            elif term < 0 and rep:  # Get rid of unnecessary signs unless first
                rep.append('-')
                rep.append(str(term)[1:])
            elif term < 0:
                rep.append(str(term))
            else:
                rep.append('+')
                rep.append(str(term))
        if rep and rep[0] == '+':
            rep.pop(0)
        if not rep:
            return '0'
        return ' '.join(rep)

    def __lt__(self, other):
        if isinstance(other, Poly):
            return list(self)[0] < list(other)[0]
        elif isinstance(other, Term):
            return list(self)[0] < other
        elif other == 0:
            return list(self)[0] < 0
        else:
            raise TypeError("These types cannot be compared")

    def __eq__(self, other):
        if isinstance(other, Poly):
            list(self) == list(other)
        else:
            raise TypeError("These types cannot be compared")

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
            raise ValueError("Incompatible Types")

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

    def __divmod__(self, other):
        def factor(dividend, divisor):  # Self == dividend, other == divisor
            return dividend[0] / divisor[0]
        if isinstance(other, Poly):
            remain = copy(self)
            res = []
            while other.degree <= remain.degree:
                res.append(factor(remain, other))
                remain = (other * res[-1] * -1) + remain
            return Poly(*res), remain

    def __div__(self, other):
        res, remain = self.__divmod__(other)
        return res

    def __mod__(self, other):
        res, remain = self.__divmod__(other)
        return remain

    def __iter__(self):
        rep = []
        for var in self.terms.values():
            for term in var.values():
                rep.append(term)
        return iter(sorted(rep, reverse=True))

    def __getitem__(self, index):
        return list(self)[index]

    def __simplify(self):
        for var in self.terms:
            for expo in self.terms[var]:
                self.terms[var][expo] = reduce(add, self.terms[var][expo])

    @property
    def degree(self):
        deg = list(self)[0]
        if deg.var:
            return deg.expo
        else:
            return 0

    def plug(self, value):
        """Evaluate polynomial for x in f(x)"""
        return reduce(add, (x.plug(value) for x in self._linearize()))


def parse_term(inpt):
    """Parses input to create a Term
    Allows for both 4x^3 or 4x3, which will build equivilant
    Term objects.
    """

    def fix(num, cls=int):
        if num == '-':
            return -1
        elif num:
            try:
                return cls(num)
            except ValueError:
                raise SyntaxError("Improper input formatting ({})".format(num))
        else:
            return 1

    inpt = inpt.replace('^', '')
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
        elif item == '.' and var:
            expo += item
        elif item == '.':
            coeff += item
        else:
            raise SyntaxError("Improper input formatting ({}).".format(item))

    coeff = fix(coeff, float)
    expo = fix(expo, int)

    return Term(coeff, var, expo)


def parse_poly(inpt):
    """Parses input to create a Poly
    operators and terms should be separated by spaces:
    5x^3 - 3x^2 + x + 9
    """

    terms = []
    sign = 1
    for item in inpt.split():
        if item in string.whitespace or item == '+':
            pass
        elif item == '-':
            sign = -1
        else:
            terms.append(parse_term(''.join(item)) * sign)
            sign = 1
    return Poly(*terms)

if __name__ == '__main__':
    stack = []
    select = {
                ''  : 'stack.append(copy(stack[0]))',
                'help' : 'hlp()',
                'h' : 'hlp()'
             }

    def hlp():
        print """\n\t\t\t\t\tThe Polynator
              Allows for calculator of single variable polynomials using a
              variety of operations (+, -, *, /, %) in reverse polish notation.
              As polynomials are entered, they are placed on a stack, and
              mathematical operations make use of the newest two.

              For example (3x^2 + 2x - 10) / (2x + 5) would be entered:

              3x^2 + 2x - 10 [enter]
              2x + 5 [enter]
              / [enter]

              Additional operations include the following:
              ~     : Delete the top item on the stack
              s     : Swap the previous two items on the stack
              h     : Disply this help
              clear : Clear the stack
                    : Entering blank lines will duplicate the top stack item
              q     : Quit\n"""

    def dispatch(inpt, stack):
        try:
            if inpt in select:
                eval(select[inpt])
            elif inpt in ('-', '+', '*', '/', '%'):
                stack.append(eval('stack.pop(-2) {} stack.pop()'.format(inpt)))
                print stack[-1]
            elif inpt == '?':
                print ",\t".join((str(x) for x in stack))
            elif inpt == 'clear':
                for item in stack:
                    stack.remove(item)
            elif inpt == '~':
                del stack[-1]
            elif inpt == 's':
                stack[-2], stack[-1] = stack[-1], stack[-2]
            else:
                try:
                    stack.append(parse_poly(inpt))
                except SyntaxError:
                    print "'{}' not valid input\n".format(inpt)
                    hlp()
        except IndexError:
            print "Not enough items on the stack."

        return inpt


    hlp()
    while dispatch(raw_input('>> ').lower(), stack) not in ['q', 'Q']:
        pass
