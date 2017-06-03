"""Install Tenhou log utils"""
import setuptools


def _setup():
    setuptools.setup(
        name='tenhou_log_utils',
        version='v0.0.1',
        packages=setuptools.find_packages(),
        install_requires=[
            'requests',
        ],
        entry_points={
            'console_scripts': [
                'tlu = tenhou_log_utils.command.main:main'
            ]
        },
    )


if __name__ == '__main__':
    _setup()
