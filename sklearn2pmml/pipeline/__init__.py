from pandas import DataFrame, Series
from sklearn.base import ClassifierMixin
from sklearn.pipeline import Pipeline

import numpy

class _Verification(object):

	def __init__(self, active_values, target_values, precision, zeroThreshold):
		if precision < 0:
			raise ValueError("Precision cannot be negative")
		if zeroThreshold < 0:
			raise ValueError("Zero threshold cannot be negative")
		self.active_values = active_values
		self.target_values = target_values
		self.precision = precision
		self.zeroThreshold = zeroThreshold

def _filter_column_names(X):
	return (numpy.asarray(X)).astype(str);

def _get_column_names(X):
	if isinstance(X, DataFrame):
		return _filter_column_names(X.columns.values)
	elif isinstance(X, Series):
		return _filter_column_names(X.name)
	else:
		return None

def _get_values(X):
	if isinstance(X, DataFrame):
		return X.values
	elif isinstance(X, Series):
		return X.values
	else:
		return X

class PMMLPipeline(Pipeline):

	def __init__(self, steps):
		super(PMMLPipeline, self).__init__(steps = steps)

	def __repr__(self):
		class_name = self.__class__.__name__
		return "%s(steps=[%s])" % (class_name, (",\n" + (1 + len(class_name) // 2) * " ").join(repr(step) for step in self.steps))

	def _fit(self, X, y = None, **fit_params):
		# Collect feature name(s)
		active_fields = _get_column_names(X)
		if active_fields is not None:
			self.active_fields = active_fields
		# Collect label name(s)
		target_fields = _get_column_names(y)
		if target_fields is not None:
			self.target_fields = target_fields
		return super(PMMLPipeline, self)._fit(X = X, y = y, **fit_params)

	def verify(self, X, precision = 1e-13, zeroThreshold = 1e-13):
		active_fields = _get_column_names(X)
		if self.active_fields is None or active_fields is None:
			raise ValueError("Cannot perform model validation with anonymous data")
		if self.active_fields.tolist() != active_fields.tolist():
			raise ValueError("The columns between training data {} and verification data {} do not match".format(self.active_fields, active_fields))
		active_values = _get_values(X)
		y = self.predict(X)
		target_values = _get_values(y)
		self.verification = _Verification(active_values, target_values, precision, zeroThreshold)
		estimator = self._final_estimator
		if isinstance(estimator, ClassifierMixin) and hasattr(estimator, "predict_proba"):
			try:
				y_proba = self.predict_proba(X)
				self.verification.probability_values = _get_values(y_proba)
			except AttributeError:
				pass
