# This specially-named module is loaded first on every new app engine instance. We use it as a bootstrapping hook
# to inform the runtime about our special "libs" subfolder where 3rd-party modules are stored.
import pkgutil
import google

# Several dirs named 'google/' need to be added to the path
google.__path__ += pkgutil.extend_path(google.__path__, 'google')
