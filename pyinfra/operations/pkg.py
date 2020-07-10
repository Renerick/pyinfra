'''
Manage BSD packages and repositories. Note that BSD package names are case-sensitive.
'''

from __future__ import unicode_literals

from pyinfra.api import operation

from .util.packaging import ensure_packages


@operation
def packages(packages=None, present=True, pkg_path=None, state=None, host=None):
    '''
    Install/remove/update pkg packages. This will use ``pkg ...`` where available
    (FreeBSD) and the ``pkg_*`` variants elsewhere.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + pkg_path: the PKG_PATH environment variable to set

    pkg_path:
        By default this is autogenerated as follows (tested/working for OpenBSD):
        ``http://ftp.<OS>.org/pub/<OS>/<VERSION>/packages/<ARCH>/``. Note that OpenBSD's
        official mirrors only hold the latest two versions packages.

        NetBSD/FreeBSD helpfully use their own directory structures, so the default won't
        work.

    Example:

    .. code:: python

        pkg.packages(
            name='Install Vim and Vim Addon Manager',
            packages=['vim-addon-manager', 'vim'],
        )

    '''

    if present is True:
        if not pkg_path and not host.fact.file('/etc/installurl'):
            host_os = host.fact.os or ''
            pkg_path = 'http://ftp.{http}.org/pub/{os}/{version}/packages/{arch}/'.format(
                http=host_os.lower(),
                os=host_os,
                version=host.fact.os_version,
                arch=host.fact.arch,
            )

    # FreeBSD used "pkg ..." and OpenBSD uses "pkg_[add|delete]"
    is_pkg = host.fact.which('pkg')
    install_command = 'pkg install -y' if is_pkg else 'pkg_add'
    uninstall_command = 'pkg delete -y' if is_pkg else 'pkg_delete'

    if pkg_path:
        install_command = 'PKG_PATH={0} {1}'.format(pkg_path, install_command)

    yield ensure_packages(
        packages, host.fact.pkg_packages, present,
        install_command=install_command,
        uninstall_command=uninstall_command,
    )
