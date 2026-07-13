pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs.services

Scope {
    id: root

    // open window immediately — this qs config is just the UI
    Component.onCompleted: KeybindsWindowFactory.open()

    
    Connections {
        target: Colours
    }
}
