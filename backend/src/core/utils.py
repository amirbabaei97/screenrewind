import Quartz
from Cocoa import NSWorkspace
import logging

def get_active_window_info():
    """
    Returns the bounds of the active window on macOS.
    Returns a dictionary with keys: x, y, width, height.
    Returns None if no active window is found.
    """
    try:
        # Get the frontmost application
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        if not active_app:
            return None
        
        pid = active_app.processIdentifier()
        app_name = active_app.localizedName()
        
        # Get all windows on screen
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        
        # Find the windows belonging to the active app
        app_windows = []
        for window in window_list:
            if window.get('kCGWindowOwnerPID') == pid:
                app_windows.append(window)
        
        if not app_windows:
            return None
            
        # Sort by layer (lower layer number is usually on top) and then by ID
        # Usually the first one is the main window, but sometimes there are invisible ones or tooltips.
        # We look for the first one with a reasonable size and layer 0.
        
        valid_windows = []
        for window in app_windows:
            # kCGWindowLayer 0 is the normal window layer
            if window.get('kCGWindowLayer', 0) == 0:
                bounds = window.get('kCGWindowBounds')
                if bounds:
                    w = int(bounds['Width'])
                    h = int(bounds['Height'])
                    # Filter out small windows (e.g. tooltips, menu bars)
                    if w > 100 and h > 100:
                        valid_windows.append({
                            'x': int(bounds['X']),
                            'y': int(bounds['Y']),
                            'width': w,
                            'height': h,
                            'area': w * h,
                            'app_name': app_name
                        })
        
        if valid_windows:
            # Return the first valid window (since they are sorted by z-order)
            # We do NOT sort by area, as that might pick a background window on another monitor.
            return valid_windows[0]
        
        # Fallback: just take the first one if no layer 0 found (unlikely for main window)
        if app_windows:
             bounds = app_windows[0].get('kCGWindowBounds')
             if bounds:
                return {
                    'x': int(bounds['X']),
                    'y': int(bounds['Y']),
                    'width': int(bounds['Width']),
                    'height': int(bounds['Height']),
                    'app_name': app_name
                }

        return None

    excelogging.errorception as e:
        print(f"Error getting active window info: {e}")
        return None
