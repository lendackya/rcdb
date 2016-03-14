import sys
import os

#Setup default environment. This environment
#if not 'CCDB_HOME' in os.environ:
#    print "CCDB_HOME environment variable is not found but should be set to compile the CCDB"
#    print "One can run 'source environment.bash' from your bash shell to automatically set environment variables"
#    exit(1)

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
BOLD = "\033[1m"

def supports_color():
    """
    Returns True if the running system's terminal supports color,
    and False otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True

if supports_color():
    print (HEADER+BOLD+"RCDB build scripts options:"+ENDC)
    print ("(default values are shown)")
    print (OKBLUE+"with-tests"+ENDC +"="+ OKGREEN + "true" +  ENDC + "   Build unit tests. Will be as ./bin/test_rcdb_cpp")
    print ("")


#Create 'default' environment. Other environments will be a copy of this one
default_env = Environment(
    #>> CCDB related default staff <<
    CPPPATH = ['#include', '#src', '/usr/include'], #, '#include/SQLite'],
    ENV = os.environ,
    CXXFLAGS = '-std=c++11',
)


#Export 'default' environment for everything that wishes to use it
Export('default_env')

#Create 'working' environment
#default_env.Repository('src')

#Attach SConsctipts
SConscript('src/SQLiteCpp/SConscript', 'default_env', variant_dir='tmp/SQLiteCpp', duplicate=0)
SConscript('tests/SConscript', 'default_env', variant_dir='tmp/Tests', duplicate=0)
#SConscript('src/Tests/SConscript', 'default_env', variant_dir='tmp/Tests', duplicate=0)

#if ARGUMENTS.get("with-tests","false")=="true":
#    print("Building with tests. To run example print example_ccdb_<example name> in console")
#    SConscript('examples/SConscript', 'default_env', variant_dir='tmp/Examples', duplicate=0)
#else:
#    print("Building without examples. To build with examples add 'with-examples=true' flag")


