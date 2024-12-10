.. index:: jump
.. _jump:

Jump
----

**jump** *lineno*

Set the next line that will be executed.

There are a number of limitations on what line can be set.

You can't jump:

* into the body of a for loop
* into an ``except`` block from outside
* outside or inside of a code block you are stopped


.. seealso::

   :ref:`skip <skip>`,
   :ref:`next <next>`, :ref:`step <step>` :ref:`continue <continue>`, and :ref:`finish <finish>` provide other ways to progress.
