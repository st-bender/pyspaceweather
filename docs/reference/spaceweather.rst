spaceweather
============

File parsing (and updating) is handled by the submodules,
but all functions are available through importing ``spaceweather``,
for example:

.. code-block:: python

    import spaceweather as sw

    sw.sw_daily()  # the daily space weather indices from celestrak

It should not be necessary to import the submodule(s) individually
as those may still be subject to change.

spaceweather.celestrak
----------------------

.. currentmodule:: spaceweather

.. automodule:: spaceweather.celestrak
   :members:
   :undoc-members:
   :show-inheritance:

spaceweather.omni
-----------------

.. automodule:: spaceweather.omni
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: spaceweather
   :members:
   :undoc-members:
   :show-inheritance:
