#!/usr/bin/env python2.6
"""
David Hogg's distance measures in cosmology

This module implements the functions from D. Hogg's very useful
cosmography reference (astro-ph/9905116v4).

REQUIREMENTS

SciPy and NumPy

HISTORY

April 5, 2012 (ver 0.4)
  -- Minor reorganiations of constants.
  -- Cleaning up codes.

December 22, 2011 (ver 0.3)
  -- Minor corrections in doc strings.
  -- Minor corrections in codes.

August 3, 2007 (ver 0.2)
  -- Make the whole thing into a class for better organization.

March 23, 2006 (ver 0.1)
  -- Implements most essential functions.  The results are checked
     against the figures in Hogg.
"""

__version__ = '0.4 (April 5, 2012)'
__credits__ = '''The code is written by Taro Sato (ubutsu@gmail.com)'''


from numpy import arcsin, inf, log10, pi, sin, sinh, sqrt
from scipy import integrate
from scipy.constants import c


# frequently used constants
c = c / 1e3   # speed of light in km/s


def E(z, om, ol):
    return sqrt(om * (1. + z)**3 + (1. - om - ol) * (1. + z)**2 + ol)


class Cosmos(object):
    """
    Cosmology for which distance measures will be computed

    INPUT

      Omega_matter, Omega_lambda, h_100
        -- defaults to (0.3, 0.7, 0.7)
    """

    def __init__(self, omega_matter=0.3, omega_lambda=0.7, h_100=0.7):
        self.om = omega_matter
        self.ol = omega_lambda
        self.h = h_100

    @property
    def H0(self):
        """Hubble constant in km/s/Mpc"""
        return 100. * self.h

    @property
    def D_H(self):
        """
        Computes the Hubble distance in Mpc

        REFERENCE

          Eq. (4) of astro-ph/9905116
        """
        return c / self.H0

    def D_C(self, z):
        """
        Computes line-of-sight comoving distance in Mpc

        REFERENCE

          Eq. (15) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        def integrand(z, om, ol):
            return 1. / sqrt(om * (1. + z)**3
                             + (1. - om - ol) * (1. + z)**2 + ol)
        om, ol, h = self.om, self.ol, self.h
        res = integrate.quad(lambda x: integrand(x, om, ol), 0., z)
        return self.D_H * res[0]

    def D_M(self, z):
        """
        Computes transverse comoving distance in Mpc per radian

        REFERENCE

          Eq. (16) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        om, ol, h = self.om, self.ol, self.h
        _D_C = self.D_C(z)
        _D_H = self.D_H
        ok = 1. - om - ol
        if ok > 0.:
            _D_M = (_D_H / sqrt(ok)) * sinh(sqrt(ok) * _D_C / _D_H)
        elif ok == 0.:
            _D_M = _D_C
        else:
            _D_M = (_D_H / sqrt(abs(ok))) * sin(sqrt(abs(ok)) * _D_C / _D_H)
        return _D_M

    def D_A(self, z):
        """
        Computes angular diameter distance in Mpc per radian

        REFERENCE

          Eq. (18) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        return self.D_M(z) / (1. + z)

    def D_L(self, z):
        """
        Computes luminosity distance in Mpc

        REFERENCE

          Eq. (21) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        return (1. + z) * self.D_M(z)

    def DM(self, z):
        """
        Computes distance modulus

        REFERENCE

          Eq. (25) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        return 5. * log10(self.D_L(z) * 1e6 / 10.)

    def dV_C(self, z):
        """
        Computes the comoving volume element

        This function actually computes the comoving volume element per
        unit solid angle dOmega per unit redshift dz, i.e.,

          dV_C / dOmega / dz

        REFERENCE

          Eq. (28) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        om, ol, h = self.om, self.ol, self.h
        ok = 1. - om - ol
        _D_H = self.D_H
        _D_A = self.D_A(z)
        return _D_H * (1. + z)**2 * _D_A**2 / E(z, om, ol)


    def V_C(self, z):
        """
        Computes the total comoving volume out to the specified redshift

        REFERENCE

          Eq. (29) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        om, ol, h = self.om, self.ol, self.h
        ok = 1. - om - ol
        _D_M = self.D_M(z)
        if ok == 0.: _V_C = 4. * pi * _D_M**3 / 3.
        else:
            _D_H = self.D_H
            mh = _D_M / _D_H
            if ok > 0.:
                _V_C = ((2. * pi * _D_H**3 / ok)
                        * (mh * sqrt(1. + ok * mh**2)
                           - arcsinh(mh * sqrt(abs(ok)))
                           / sqrt(abs(ok))))
            else:
                _V_C = ((2. * pi * _D_H**3 / ok)
                        * (mh * sqrt(1. + ok * mh**2)
                           - arcsin(mh * sqrt(abs(ok)))
                           / sqrt(abs(ok))))
        return _V_C

    @property
    def t_H(self):
        """
        Computes the Hubble time in Gyr

        REFERENCE

          Eq. (3) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        _t_H = 1. / self.H0
        _t_H *= 1e-3 * 1e6 * 3.0856776e16  # -> s
        _t_H *= (1. / (365.25 * 24 * 3600)) * 1e-9  # s -> Gyr
        return _t_H

    def t_L(self, z):
        """
        Computes lookback time in Gyr

        REFERENCE

          Eq. (30) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        def integrand(z, om, ol):
            return 1. / (1. + z) / sqrt(om * (1. + z)**3
                                        + (1. - om - ol) * (1. + z)**2
                                        + ol)
        om, ol, h = self.om, self.ol, self.h
        res = integrate.quad(lambda x: integrand(x, om, ol), 0., z)
        return self.t_H * res[0]

    def t(self, z):
        """
        Computes the age of universe in Gyr at the specified redshift

        REFERENCE

          Eq. (30) of astro-ph/9905116 but the range of integration is
          (z, +infty)

        INPUT

          z -- redshift
        """
        def integrand(z, om, ol):
            return 1. / (1. + z) / sqrt(om * (1. + z)**3
                                        + (1. - om - ol) * (1. + z)**2
                                        + ol)
        om, ol, h = self.om, self.ol, self.h
        res = integrate.quad(lambda x: integrand(x, om, ol), z, +integrate.Inf)
        return self.t_H * res[0]

    def dP(self, z):
        """
        Computes the probability of intersection objects

        This function actually computes 

          dP / dz / n(z) / sigma(z)

        where n(z) is the comoving number density and sigma(z) is the
        cross section.

        REFERENCE

          Eq. (31) of astro-ph/9905116

        INPUT

          z -- redshift
        """
        om, ol, h = self.om, self.ol, self.h
        return self.D_H * (1. + z)**2 / E(z, om, ol)


if __name__ == '__main__':
    """test code"""
    z = 0.4

    cosmos = Cosmos()

    cd1 = cosmos.DM(0.025)
    cd2 = cosmos.DM(0.4)

    D1 = cd1
    D2 = cd2

    print D1, D2
