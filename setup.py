from cx_Freeze import setup, Executable

setup(
    name='paint',
    version='0.1',
    description='Your app description',
    executables=[Executable('paint.py')]
)
