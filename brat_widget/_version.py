version_info = (0, 2, 3)#, 'dev')
__version__ = '.'.join(map(str, version_info))
__frontend_version__ = '^%s.%s.%s'%(version_info[0], version_info[1], version_info[2])