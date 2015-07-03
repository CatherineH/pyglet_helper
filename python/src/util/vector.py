# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from math import sqrt, acos

class vector:
	def __init__(self, a = 0.0, b = 0.0, c = 0.0, v = None):
		if not v is None:
			if len(v)==3:
				self.x = v[0]
				self.y = v[1]
				self.z = v[2]
			else:
				raise ValueExcept("Vector must be of length 3!")
		else:
			if type(a) is tuple:
				self.x = a[0]
				self.y = a[1]
				self.z = a[2]
			elif hasattr(a, 'x') and hasattr(a, 'y') and hasattr(a, 'z'):
				self.x = a.x
				self.y = a.y
				self.z = a.z
			else:
				self.x = a
				self.y = b
				self.z = c

	def __add__(self, other):
		return vector( self.x+other.x, self.y+other.y, self.z+other.z)

	def __sub__(self, v):
		return vector( self.x-v.x, self.y-v.y, self.z-v.z)

	def __mul__(self,v):
		if type(v) ==type(self):
			return vector( self.x*v.x, self.y*v.y, self.z*v.z)
		else:
			return vector( self.x*v, self.y*v, self.z*v)
	def __rmul__(self,v):
		if type(v) == type(self):
			return vector(v.x*self.x, v.y*self.y, v.z*self.z)
		else:
			return vector(v*self.x, v*self.y, v*self.z)

	def __div__(self,s):
		return vector( self.x/s, self.y/s, self.z/s)

    # This operator describes a strict weak ordering as defined by the STL.
	def stl_cmp(self, v):
		if (self.x != v.x):
			return self.x < v.x
		elif (self.y != v.y):
			return self.y < v.y
		else:
			return self.z < v.z

	def __eq__(self, v):
		return (v.x == self.x and v.y == self.y and v.z == self.z)

	def __ne__(self,v):
		return not (v == self)

	def nonzero(self):
		return self.x or self.y or self.z

	def __invert__(self):
		return vector( -self.x, -self.y, -self.z)

	# return the magnitude of this vector
	def mag(self):
		return sqrt( self.x*self.x + self.y*self.y + self.z*self.z)

	# This is a magnitude algorithm that is intended to be stable at values
	# greater than 1e154 (or so).  It is much slower since it uses sin, cos,
	# and atan to get the result.
	def stable_mag(self):
		ret = 0.0

		x1 = fabs(x)
		x2 = fabs(y)
		x3 = fabs(z)
		# sort the temporaries into descending order.
		if (x1 < x2):
			swap( x1, x2)
		if (x2 < x3):
			swap(x2, x3)
			if (x1 < x2):
				swap( x1, x2)


		if (x1 == 0.0):
			return 0.0
		if (x2 == 0.0):
			return x1
		# at this point, ret is equal to the length of an R2 vector.
		ret = x1 / cos( atan( x1/ x2))
		if (x3 == 0.0):
			return ret
		ret = ret / cos( atan( ret/x3))
		return ret

	# return the square of the this vector's magnitude
	def mag2(self):
		return (self.x*self.x + self.y*self.y + self.z*self.z)

	# return the unit vector of this vector
	def norm(self):
		magnitude = self.mag()
		if (magnitude):
			# This step ensures that vector(0,0,0).norm() returns vector(0,0,0)
			# instead of NaN
			magnitude = 1.0 / magnitude
		return vector( self.x*magnitude, self.y*magnitude, self.z*magnitude)

	def set_mag(self, m):
	 	self = self.norm()*m

	def set_mag2(self, m2):
		self = self.norm()*sqrt(m2)
	# Pythonic function to provide a "representation" of this object.
	# object.__repr__() should return a string that, were it executed as python
	# code, should regenerate the object.
	def __repr__(self):
		return "vector(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"

	# return the dot product of this vector and another
	def dot(self, v):
		return ( v.x * self.x + v.y * self.y + v.z * self.z)

	# Return the cross product of this vector and another.
	def	cross(self, v):
		ret = vector( self.y*v.z - self.z*v.y \
		, self.z*v.x - self.x*v.z \
		, self.x*v.y - self.y*v.x)
		return ret
	# Return the scalar triple product
	def dot_b_cross_c(self, b, c):
		return ( self.x*(b.y*c.z - b.z*c.y) \
	       - self.y*(b.x*c.z - b.z*c.x) \
	       + self.z*(b.x*c.y - b.y*c.x) )

	# Return the vector triple product
	def cross_b_cross_c( self, b, c):
		return (self.dot( c) * b - self.dot( b) * c)

	# Scalar projection of this to v
	def comp(self, v):
		return (self.dot( v) / v.mag())

	# Vector projection of this to v
	def proj( self, v):
		return (self.dot( v)/v.mag2() * v)

	# Returns the angular difference between two vectors, in radians, between 0 and pi.
	def diff_angle(self, v):
		vn1 = self.norm()
		vn2 = v.norm()
		d = vn1.dot(vn2)
		if (d > 0.999):
			d = vector(vn2.x-vn1.x, vn2.y-vn1.y, vn2.z-vn1.z).mag()
			return 2.0*asin(d/2.0)
		elif (d < -0.999):
			d = vector(vn2.x+vn1.x, vn2.y+vn1.y, vn2.z+vn1.z).mag()
			return pi - 2.0*asin(d/2.0)

		return acos(d)

	# Scale this vector to another, by elementwise multiplication
	def scale(self, v):
		return vector( self.x*v.x, self.y*v.y, self.z*v.z)

    # Inversely scale this vector to another, by elementwise division
	def scale_inv(self, v):
		return vector( x/v.x, y/v.y, z/v.z)

	def rotate(self, angle, axis = None):
		if not axis is None:
			R = rotation( angle, axis.norm())
		else:
			axis = vector(0,0,1)
			R = rotation( angle, axis.norm())
		return R * self

	@property
	def x(self):
		return self.x
	@x.setter
	def x(self,s):
		self.x = s

	@property
	def y(self):
		return self.y
	@y.setter
	def y(self,s):
		self.y = s

	@property
	def z(self):
		return self.z
	@z.setter
	def z(self,s):
		self.z = s

	# zero the state of the vector. Potentially useful for reusing a temporary.
	def clear(self):
		self.x=0.0
		self.y=0.0
		self.z=0.0

	def __getitem__(self, i):
		if i ==0 or i==-3:
			return self.x
		if i==1 or i == -2:
			return self.y
		if i==2 or i == -1:
			return self.z
		if i>2 or i<-3:
			raise IndexError("index not available")

	def __setitem__(self, i, value):
		if i ==0 or i==-3:
			self.x = value
		if i==1 or i == -2:
			self.y = value
		if i==2 or i == -1:
			self.z = value
		if i>2 or i<-3:
			raise IndexError("index not available")

	def fabs(self):
	 return vector( fabs(self.x), fabs(self.y), fabs(self.z))

	def gl_render(self):
		glVertex3dv( self.x)

	def gl_normal(self):
		glNormal3dv(self.x)

	def sum(self):
	 return self.x + self.y + self.z


# Free functions for mag, mag2, dot, unit, cross, and tripleproducts.
# All of these functions merely call their class-member variants to save code.
def mag(v):
	return v.mag()

def mag2(v):
	return v.mag2()

def norm(v):
	return v.norm()

def dot(v1,  v2):
	return v1.dot(v2)

def cross( v1, v2):
	return v1.cross( v2)

def a_dot_b_cross_c( a,  b,  c):
	return a.dot_b_cross_c( b, c)

def a_cross_b_cross_c( a, b, c):
	return a.cross_b_cross_c( b, c)

# Scalar projection of v1 -> v2
def comp( v1, v2):
	return v1.comp( v2)

# Vector projection of v1 to v2
def proj( v1, v2):
	return v1.proj( v2)

# Returns the angular difference between two vectors, in radians, from 0 - pi.
def diff_angle( v1,  v2):
 return v1.diff_angle( v2)

def rotate( v, angle, axis = vector( 0,0,1)):
	return v.rotate( angle, axis)
