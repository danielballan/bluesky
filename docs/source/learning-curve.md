# On The Bluesky Learning Curve

Mastering Python and Bluesky takes time. How can a facility user, especially one
who does not know Python, quickly get going with Bluesky?

- Put users in front of a set of custom plans parameters the way that they need.
- When even a little typing is too much typing, write a GUI.
- When users have custom requirements, put these users to work alongside
  someone experienced with Bluesky. Leave them with well-commented code that
  they may be able to make simple modifications to.

We strongly discourage writing a DSL (Domain-Specific Language). Using a
widely-supported language and syntax has enormous advantages, and diverging
from that would require unsustainable resources. Those resources would be
better spent building GUIs or dedicating software support to specific
experiments.

It may be useful to a write limited commandline interfaces (CLI) that launch or
schedule Bluesky plans. The CLI should not become a full-fledged scripting
language: it would be composable using shell langauges (e.g. bash scripting).
If users in the Bluesky community experiment with this, perhaps a
general-purpose limited tool could be moved upstream.
