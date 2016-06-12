from setuptools import setup, find_packages

setup(
        name='avchd-toolkit',
        version='0.4.2',
        author='Marcin Nowak',
        author_email='marcin.j.nowak@gmail.com',
        zip_safe=True,
        url='https://github.com/marcinn/avchd-transcode',
        description='Simple tools to help with prosumer cameras workflow (like working with Canon C100` files)',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: English',
            'Operating System :: MacOS',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 2 :: Only',
            'Topic :: Multimedia :: Sound/Audio :: Conversion',
            'Topic :: Multimedia :: Video :: Conversion',
            'Topic :: Utilities',
            ],
        entry_points = {
            'console_scripts': [
                #'avchd-fix-name = avchdtoolkit.commands.rename:main',
                'avchd-transcode = avchdtoolkit.commands.transcode:main',
                'avchd-extract-timecodes = avchdtoolkit.commands.extract_timecodes:main',
                'avchd-archive = avchdtoolkit.commands.archive:main',
                ],
            },
        packages=find_packages('.', exclude=('tests','tests.*')),
        package_data={
            'avchdtoolkit': ['codecs.ini'],
            },
        install_requires=[
            'futures>=3.0.0,<4.0.0',
            ],
        )
