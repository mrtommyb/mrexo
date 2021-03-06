from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()



setup(name='mrexo',
      version='0.1',
      description='Non parametric mass radius relationship for exoplanets',
      long_description=readme(),
      url='https://github.com/shbhuk/mrexo',
      author='Shubham Kanodia',
      author_email='shbhuk@gmail.com',
      install_requires=['astropy>2','matplotlib','numpy','scipy'],
      packages=['mrexo'],
      license='GPLv3',
      classifiers=['Topic :: Scientific/Engineering :: Astronomy'],
      keywords='Mass-Radius relationship Non parametric Exoplanets',
      include_package_data=True
      )
