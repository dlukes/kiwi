Link individual flights, input as CSV, into itineraries. See
``find_combinations.py -h`` for further description and usage.

``check.py`` can be used to double check that the itineraries returned by
``find_combinations.py`` are indeed valid.

On ``master``, ``find_combinations.py`` tries to be smart by indexing already
seen flights so that it doesn't have to do an exhaustive search for potential
candidates each time a new flight is considered as a possible extension to
existing itineraries. ``git checkout naive`` is a simpler reference
implementation which *does* search exhaustively; compare outputs of both to
verify that nothing went horribly wrong.

Developed on **Python 3.5.2**.
