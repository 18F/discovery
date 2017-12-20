from inspect import getframeinfo, stack
import psutil


def memory_in_mb(mem):
    #documentation on memory fields: http://psutil.readthedocs.io/en/latest/#id1
    unit = 1024 * 1024 # MB
    return {
        'total': mem.total / unit,
        'available': mem.available / unit, #*
        'used': mem.used / unit, #*
        'free': mem.free / unit,
        'active': mem.active / unit,
        'inactive': mem.inactive / unit,
        'buffers': mem.buffers / unit,
        'cached': mem.cached / unit,
        'shared': mem.shared / unit,
    }


def print_memory(message = "Max Memory"):
    caller = getframeinfo(stack()[1][0])
    mem = memory_in_mb(psutil.virtual_memory())   
    
    
    print("{}/{} | {}: {:.2f}MB {:.2f}MB".format(caller.filename, caller.lineno, message, mem['available'], mem['used']))


def csv_memory(message = "Memory"):
    caller = getframeinfo(stack()[1][0])
    mem = memory_in_mb(psutil.virtual_memory())
    
    return('"{}","{}",{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f}'.format(caller.filename, message, mem['total'], mem['available'], mem['used'], mem['free'], mem['active'], mem['inactive'], mem['buffers'], mem['cached'], mem['shared']))
