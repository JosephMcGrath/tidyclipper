@ECHO OFF
call activate

ECHO.
ECHO : : : : : : : : : : : : : : : : : : : : : : : : : : : :
ECHO.

python -m black .

ECHO.
ECHO : : : : : : : : : : : : : : : : : : : : : : : : : : : :
ECHO.

python -m pylint src/tidyclipper

ECHO.
ECHO : : : : : : : : : : : : : : : : : : : : : : : : : : : :
ECHO.

python -m mypy src/tidyclipper

ECHO.
ECHO : : : : : : : : : : : : : : : : : : : : : : : : : : : :
ECHO.

@PAUSE
