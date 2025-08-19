from .logger import logger


def all_in_list(list1: list, list2: list):
	logger.debug(f"Checks if all {list1} is in {list2}...")
	for e in list1:
		if e not in list2:
			logger.debug(f"{repr(e)} is not in {list2}")
			return False
	return True


class classproperty(property):
	# noinspection PyMethodOverriding
	def __get__(self, owner_self, owner_cls):
		return self.fget(owner_cls)
