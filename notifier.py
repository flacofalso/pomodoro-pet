import subprocess
import platform


def notify(title: str, message: str):
    """Send a native system notification. Works on macOS and Windows."""
    system = platform.system()
    try:
        if system == "Darwin":
            script = (
                f'display notification "{message}" '
                f'with title "{title}" '
                f'sound name "Glass"'
            )
            subprocess.Popen(
                ["osascript", "-e", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Windows":
            # Uses PowerShell toast notification (Windows 10+)
            ps = (
                f"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
                f"ContentType = WindowsRuntime] | Out-Null; "
                f"$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent("
                f"[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
                f"$template.SelectSingleNode('//text[@id=1]').InnerText = '{title}'; "
                f"$template.SelectSingleNode('//text[@id=2]').InnerText = '{message}'; "
                f"$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
                f"[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Pomodoro Pet').Show($toast);"
            )
            subprocess.Popen(
                ["powershell", "-Command", ps],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception as e:
        print(f"[Notifier] Could not send notification: {e}")
