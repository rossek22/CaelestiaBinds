pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import qs.services

Scope {
    id: root

    // Сразу открываем окно: этот qs-конфиг только ради UI
    Component.onCompleted: KeybindsWindowFactory.open()

    
    Connections {
        target: Colours
    }
}
