from setuptools import setup, find_packages

setup(
        name='avchd-toolkit',
        version='0.1.1',
        author='Marcin Nowak',
        author_email='marcin.j.nowak@gmail.com',
        zip_safe=True,
        url='https://github.com/marcinn/cando',
        description='Simple tools to help with prosumer cameras workflow (like working with Canon C100` files)',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 2 :: Only',
            'Topic :: Multimedia :: Sound/Audio :: Conversion',
            'Topic :: Multimedia :: Video :: Conversion',
            'Topic :: Utilities',
            ],
        entry_points = {
            'console_scripts': [
                'avchd-renamer = avchdrenamer.cmdline:main',
                'avchd-transcode = avchdtrans.cmdline:main',
                ],
            },
        packages=find_packages('.', exclude=('tests','tests.*')),
        package_data={
            'avchdtrans': ['codecs.ini'],
            },
        install_requires=[
            'futures>=3.0.0,<4.0.0',
            ],
        )
