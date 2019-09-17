#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(repository='my_repository', url='sqlite:///db/datapoints.db', debug='False')
