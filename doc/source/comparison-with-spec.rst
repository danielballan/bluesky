Migrating from SPEC
===================

Why did we write new data acquisition software?
-----------------------------------------------

`SPEC <https://www.certif.com/content/spec/>`_ is a popular software package
for instrument control and data acquisition. Many users in the synchrotron
community, from which bluesky originated, know SPEC and ask what differentiates
and motivates bluesky. Answering this question in an informed and unbiased way
is difficult, and we welcome any corrections.

There are many good features of SPEC that have been incorporated into
bluesky, including:

* Simple commands for common experiments, which can be used as building blocks
  for more complex procedures
* Easy hardware configuration
* Interruption handling (Ctrl+C)
* Integration with EPICS (and potentially other instrument control systems)
* "Pseudomotors" presenting virtual axes
* Integration with reciprocal space transformation code

Bluesky has also addressed certain limitations of SPEC. In fairness to SPEC, we
have the benefit of learning from its decades of use, and we are standing on
the shoulders of the modern open-source community.

* Bluesky is free and open-source in all aspects. Macros from the SPEC user
  community are open-source, but the core SPEC C source code is closed and not
  free.
* Bluesky provides more control over the console output and plotting.
* SPEC was designed before large area detectors existed. Ingesting area
  detector data is possible, but *ad hoc*. In bluesky, area detectors and other
  higher-dimensional inputs are integrated naturally.
* SPEC writes to a custom text-based format (a "SPEC file"). Bluesky can
  write---in real time or *post facto*---to any format.
* SPEC has a simulation mode. Bluesky allows users to incorporate much richer
  simulation capabilities (about which more below) but, as of version 0.9.0,
  provides less than SPEC out of the box.

Using Python, a general-purpose programming language, gives several immediate
advantages:

* Python checks syntax automatically.
* Python provides tools for interactive debugging.
* There are many more resources for learning Python.
* The language is more flexible.
* It's easy to integrate with the scientific Python ecosystem.

Bluesky tries to go further than SPEC in some regards:

* Complex custom procedures are easier to express.
* Automated "suspension" (pausing and resuming) is consistent and easier to
  manage.
* The prevailing model in SPEC is to collect data as a step scan. Other types
  of scans---such as fly scans or asynchronous monitoring---can be
  done, but they are *ad hoc*. Bluesky supports several modalities of data
  acquisition with equal ease.
* Bluesky can acquire multiple asynchronous, uncoordinated streams of data and
  represent them in a simple :doc:`event-based data model <documents>`.
* It is easy to build tools that inspect/simulate a procedure before it is run
  to check for safety, estimate time to completion, or visualize its behavior.
* Bluesky is a library that works well interactively but can also be used
  programmatically in scripts or other libraries.
* Users can add arbitrary metadata with rich semantics, including large arrays
  (such as masks) or nested mappings.
* Bluesky is a holistic solution for data acquisition and management. Users can
  push live streaming data directly into their data processing and analysis
  pipelines and/or export it into a file.

On the other hand, one major advantage of SPEC over bluesky is its maturity.
SPEC is battle-hardened from decades of use at many facilities, and it has a
large user community. Bluesky is a young project.

Why do I have to type RE?
-------------------------

SPEC users immediately notice that simple bluesky commands are more verbose
than their counterparts in SPEC. Most especially, they wonder why it is
necessary to type ``RE(...)`` all the time.

*Argumentum ad populum:* During the development process, we found that most
users who voiced this complaint at first soon appreciated that the bluesky's
overall convenience and power outweigh the superficial inconvenience of typing
"RE".

Our key arguments are:

* By using up/down arrow keys to repeat previous commands and using tab
  completion, users don't actually do that much more typing.
* A general-purpose language requires a more explicit syntax, but in exchange
  you get flexibility and interoperability with the scientific Python
  ecosystem.
* The RunEngine ensures that Devices are left in a safe state in the event of
  an interruption or error; it listens for user-initiated pauses (Ctrl+C); it
  can suspend and resume, unattended, in response to external conditions.
* The RunEngine is a central place to store configuration that you don't want
  to have to specify every time, including a list of supplemental readings to
  be taken or tasks to be executed during every plan, persistent metadata, and
  a list of destinations for the live stream of data and metadata.

If you are still feeling skeptical that this design choice is technically
justified, we offer the following Socratic dialogue, tongue in cheek.

Socrates: These commands are more verbose than I'm used to, Plato. My fingers
are older than yours --- I don't know how you type so quickly!

Plato: Did you know that IPython lets you use the up/down arrow key to scroll
through previous commands? Once you type a command out once, you can always go
back to it, make some changes if needed, and execute it again. Tab completion
can save time too.

Socrates: Why do we need all these parentheses and commas? In SPEC we just used
spaces.

Plato: SPEC is a single-purpose command line interface, whereas Python is a
general-purpose language. Python requires a more explicit syntax, but in
exchange you get flexibility and interoperability with a huge ecosystem of
scientific code in Python, C, and Fortran. You might not think you want that at
first, but consider how convenient it might be to use a mathematical expression
in line, such as this basic example:

.. code-block:: python

    from numpy import sin, pi, linspace

    # Scan 50 points between 0 and 10, distributed sinusoidally.
    RE(list_scan(dets, motor, 10 * sin(linspace(0, pi, num=50)))

Without parentheses and commas, that would be impossible to express. Even if
your data collection needs are simple, you will find that knowing some Python
is even more useful for data *analysis*. Isn't it better to use one standard,
widely-used language than to save on some parentheses and commas?

Socrates: Overall it seems more complex than I would expect.

Plato: Some of the difference is also due to the richer abstractions required
to capture the complexity of modern hardware.

Socrates: OK, I can see I'm not going to convince you to change the syntax. But
what is this ``RE``?

Plato: ``RE``, the RunEngine, executes the experiment while plans like
``count(dets)`` tell it what to do. By separating these two concepts --- the
executor and the instructions --- we can handle many concerns consistently and
correctly in the executor so that scientists don't have to worry about them
when they write custom plans. In particular, handling errors and interruptions
safely and correctly is tricky, and it's best to do it once, correctly, in one
place.

* The RunEngine keeps track of every Device that the plan asks it to touch, and
  it ensure that the Device is put into a safe state at the end --- even if
  there is an error and the plan exits unexpectedly.
* The RunEngine listens for the user to hit Ctrl+C and, again, ensures that
  every Device is put into a safe state. It makes it possible to cleanly resume
  that plan without losing data.
* The RunEngine can monitor external conditions (Has a shutter been closed? Has
  the beam dumped?) in the background and automatically suspend plan execution
  and then resume it after conditions return to normal. This is especially
  useful if something goes temporarily wrong in the middle of the night. You'll
  return in the morning to discover that the RunEngine suspended your work,
  rewound to a safe point to resume from, and then continued.
* The RunEngine is a central place to store configuration, including a list of
  supplemental readings to be taken or tasks to be executed during every plan,
  persistent metadata, and a list of destinations for the live stream of data
  and metadata.
* The RunEngine handles all I/O, ensuring that data and metadata are captured
  and organized in a flexible but standardized way.

Socrates: But why do we need to type ``RE(count(dets))``? Isn't typing
``count(dets)`` enough? Can't bluesky know that I want it to run ``RE(...)``?

Plato: You would think so! But in fact, we tried that model with users for
awhile and found that it created more problems that it solved.

Socrates: Hmm. You're my best student, Plato. Surely you are smart enough to
figure out a way that I won't have to type RE.

Plato:

Socrates: My users shouldn't have to know about RE.

Plato:
