"""
Author: Ryan Roler (ryan.roler@gmail.com)

This is...
        THE POLYNATOR!
"""

from functools import total_ordering


@total_ordering
class Term():
    """Term objects represent terms in a polynomial
    An example of a term: 4x^3
    Such a term would be instantiated by passing
    the integer coefficient, a string type Variable
    of one letter, and an integer exponent.
    """

    def __init__(self, coeff, var, expon):
        self.coeff = coeff
        self.var = var.lower()
        self.expon = expon

    def __str__(self):
        # Head (Coefficient and Variable part}
        if self.coeff == -1:
            head = '-' + self.var
        elif self.coeff:
            head = str(self.coeff) + self.var
        else:
            head = self.var

        # Tail (Exponential part)
        if self.expon:
            tail = '^' + str(self.expon)
        else:
            tail = ''

        return head + tail

    def __lt__(self, other):
        if isinstance(other, Term):
            if self.expon > other.expon:
                return False
            if self.coeff >= other.coeff:
                return False
            return True
        elif other == 0:
            return self.coeff < 0
        else:
            raise TypeError("These types cannot be compared")

    def __eq__(self, other):
        if isinstance(other, Term):
            for key, value in self.__dict__.items():
                if value != other.__dict__[key]:
                    return False
            return True
        elif other == 0:
            return self.coeff == 0
        else:
            raise TypeError("These types cannot be compared")

    def __add__(self, other):
        if (other.var == self.var) and (other.expon == self.expon):
            return Term(self.coeff + other.coeff, self.var, self.expon)
        else:
            raise ArithmeticError("Non-matching exponents")

    def __sub__(self, other):
        if (other.var == self.var) and (other.expon == self.expon):
            return Term(self.coeff - other.coeff, self.var, self.expon)
        else:
            raise ArithmeticError("Non-matching exponents")


class Poly():
    """Poly objects represent polynomials.
    These are ordered collections of Term objects.
    Any number of Term objects can be passed as
    arguments when instantiating. Non-Term objects
    passed as arguments will be ignored.
    """

    def __init__(self, *args):
        self.terms = [x for x in args if isinstance(x, Term)]
        self.terms.sort(reverse=True)

    def __str__(self):
        # Needs to be changed to retain sign of leading term if negative
        rep = []
        for term in self.terms:
            if term < 0:
                rep.append('-')
                rep.append(str(term)[1:])  # Get rid of unnecessary signs
            else:
                rep.append('+')
                rep.append(str(term))
        if rep[0] == '+':
            return ' '.join(rep[1:])
        return ' '.join(rep)


def parse_term(inpt):
    """Parses input based on a set of rules to create a Term
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
    else:
        sign = 1

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

if __name__ == '__main__':
    stack = []

    while True:
        try:
            stack.append(parse_term(input('>> ')))
        except Exception:
            break

    print(Poly(stack))
