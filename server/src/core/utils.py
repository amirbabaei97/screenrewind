import Quartz
from Cocoa import NSWorkspace, NSRunLoop, NSDate
import logging

def get_active_window_info():
    """
    Returns the bounds of the active window on macOS.
    Returns a dictionary with keys: x, y, width, height, app_name.
    Returns None if no active window is found.
    """
    try:
        # Pump event loop to get latest NSWorkspace updates
        # This is crucial for long-running scripts to detect app switches
        NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))

        # 1. Get Active App
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        if not active_app:
            logging.warning("No active app found via NSWorkspace.")
            return None
        
        pid = active_app.processIdentifier()
        app_name = active_app.localizedName()
        
        # 2. Get All Windows for this App
        options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
        window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
        
        found_windows = []
        for window in window_list:
            if window.get('kCGWindowOwnerPID') == pid:
                bounds = window.get('kCGWindowBounds')
                layer = window.get('kCGWindowLayer', 0)
                title = window.get('kCGWindowName', '')
                
                w_info = {
                    'id': window.get('kCGWindowNumber'),
                    'title': title,
                    'layer': layer,
                    'x': int(bounds['X']),
                    'y': int(bounds['Y']),
                    'width': int(bounds['Width']),
                    'height': int(bounds['Height']),
                    'area': int(bounds['Width']) * int(bounds['Height']),
                    'app_name': app_name
                }
                found_windows.append(w_info)

        # 3. Apply Selection Logic
        # Filter for layer 0 and reasonable size
        valid_windows = []
        for w in found_windows:
            if w['layer'] == 0 and w['width'] > 100 and w['height'] > 100:
                valid_windows.append(w)
        
        if valid_windows:
            # Return the first valid window (z-order)
            selected = valid_windows[0]
            logging.info(f"Selected window: {selected['app_name']} (ID: {selected['id']}, {selected['width']}x{selected['height']})")
            return selected
        
        logging.warning(f"No valid window found for {app_name}. Found {len(found_windows)} total windows.")
        return None

    except Exception as e:
        logging.error(f"Error getting active window info: {e}")
        return None
