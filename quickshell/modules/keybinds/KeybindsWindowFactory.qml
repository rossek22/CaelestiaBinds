pragma Singleton
pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Caelestia.Config
import qs.components
import qs.services

Singleton {
    id: root

    property var win: null

    function open(): void {
        if (win) {
            try {
                win.visible = true;
            } catch (e) {}
            return;
        }
        win = winComp.createObject(dummy);
    }

    function close(): void {
        if (win) {
            win.destroy();
            win = null;
        }
        Qt.quit();
    }

    QtObject {
        id: dummy
    }

    Component {
        id: winComp

        FloatingWindow {
            id: window

            color: Colours.tPalette.m3surface
            surfaceFormat.opaque: false
            title: KeybindsI18n.t("win.title")

            // Tokens ждут имя screen, как в Nexus шелла
            contentItem.Config.screen: window.screen?.name ?? ""
            contentItem.Tokens.screen: window.screen?.name ?? ""

            // Стандартный размер при открытии
            implicitWidth: 1345
            implicitHeight: 845

            minimumSize.width: contentItem.Tokens?.sizes?.nexus?.minWidth ?? 720
            minimumSize.height: contentItem.Tokens?.sizes?.nexus?.minHeight ?? 480

            onVisibleChanged: {
                if (!visible) {
                    root.win = null;
                    destroy();
                    Qt.quit();
                }
            }

            KeybindsNexus {
                id: content
                anchors.fill: parent
                onCloseRequested: root.close()
            }

            Behavior on color {
                CAnim {}
            }
        }
    }
}
