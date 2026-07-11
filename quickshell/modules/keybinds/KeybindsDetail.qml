pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.components
import qs.components.containers
import qs.components.controls
import qs.services

// Detail всегда в дереве: только биндинги на backend.selected
Flickable {
    id: root

    required property var backend
    signal back
    signal editRequested(var bind)

    readonly property var b: backend.selected

    contentWidth: width
    contentHeight: col.implicitHeight + Tokens.padding.extraLarge
    clip: true
    boundsBehavior: Flickable.DragAndOvershootBounds
    flickDeceleration: 3500

    onOpacityChanged: {
        if (opacity > 0.5)
            contentY = 0;
    }

    ColumnLayout {
        id: col
        width: root.width
        spacing: Tokens.spacing.large

        StyledRect {
            Layout.fillWidth: true
            implicitHeight: hero.implicitHeight + Tokens.padding.extraLarge * 2
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer

            ColumnLayout {
                id: hero
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.largeIncreased
                spacing: Tokens.spacing.small

                StyledRect {
                    implicitHeight: k.implicitHeight + Tokens.padding.extraSmall
                    implicitWidth: k.implicitWidth + Tokens.padding.medium
                    radius: Tokens.rounding.small
                    color: Colours.palette.m3primaryContainer

                    StyledText {
                        id: k
                        anchors.centerIn: parent
                        text: root.b?.keys ?? ""
                        color: Colours.palette.m3onPrimaryContainer
                        font: Tokens.font.label.large
                    }
                }

                StyledText {
                    Layout.fillWidth: true
                    text: root.b?.title ?? ""
                    font: Tokens.font.title.medium
                    wrapMode: Text.Wrap
                }

                StyledText {
                    Layout.fillWidth: true
                    Layout.topMargin: Tokens.spacing.small
                    text: KeybindsI18n.t("detail.what")
                    color: Colours.palette.m3onSurfaceVariant
                    font: Tokens.font.label.medium
                }

                StyledText {
                    Layout.fillWidth: true
                    text: root.b?.detail ?? ""
                    color: Colours.palette.m3onSurfaceVariant
                    font: Tokens.font.body.small
                    wrapMode: Text.Wrap
                }

                StyledText {
                    Layout.fillWidth: true
                    Layout.topMargin: Tokens.spacing.small
                    text: KeybindsI18n.t("detail.technical")
                    color: Colours.palette.m3onSurfaceVariant
                    font: Tokens.font.label.medium
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.small

                    StyledRect {
                        Layout.fillWidth: true
                        implicitHeight: techLabel.implicitHeight + Tokens.padding.medium * 2
                        radius: Tokens.rounding.large
                        color: Colours.tPalette.m3surfaceContainerHigh

                        StyledText {
                            id: techLabel
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Tokens.padding.medium
                            text: {
                                if (!root.b)
                                    return "-";
                                if (root.backend.showResolved && root.b.hasVarCmd)
                                    return root.b.technicalResolved;
                                return root.b.technical || "-";
                            }
                            color: Colours.palette.m3primary
                            font: Tokens.font.label.medium
                            wrapMode: Text.WrapAnywhere
                        }
                    }

                    IconTextButton {
                        visible: root.b?.hasVarCmd ?? false
                        text: root.backend.showResolved ? "vars" : "real"
                        icon: root.backend.showResolved ? "data_object" : "terminal"
                        type: TextButton.Tonal
                        onClicked: root.backend.showResolved = !root.backend.showResolved
                    }
                }

                StyledText {
                    Layout.fillWidth: true
                    text: KeybindsI18n.tf("detail.meta", root.b?.category ?? "", root.b?.source ?? "")
                    color: Colours.palette.m3outline
                    font: Tokens.font.label.small
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: Tokens.spacing.small

            IconTextButton {
                Layout.fillWidth: true
                text: KeybindsI18n.t("detail.copy")
                icon: "content_copy"
                type: TextButton.Tonal
                onClicked: {
                    if (!root.b)
                        return;
                    clipProc.command = ["wl-copy", `${root.b.keys}  →  ${root.b.title}`];
                    clipProc.running = true;
                }
            }

            IconTextButton {
                Layout.fillWidth: true
                visible: root.b?.source === "custom" || root.b?.source === "override" || root.b?.source === "system"
                text: root.b?.source === "system" ? KeybindsI18n.t("detail.override") : KeybindsI18n.t("detail.edit")
                icon: "edit"
                type: TextButton.Filled
                onClicked: if (root.b)
                    root.editRequested(root.b)
            }

            IconTextButton {
                Layout.fillWidth: true
                visible: (root.b?.source === "system" || root.b?.source === "custom") && (root.b?.enabled ?? false)
                text: KeybindsI18n.t("detail.disable")
                icon: "block"
                type: TextButton.Tonal
                onClicked: if (root.b)
                    root.backend.disableBind(root.b.id)
            }

            IconTextButton {
                Layout.fillWidth: true
                visible: (root.b?.source === "system" || root.b?.source === "custom") && !(root.b?.enabled ?? true)
                text: KeybindsI18n.t("detail.enable")
                icon: "check_circle"
                type: TextButton.Filled
                onClicked: if (root.b)
                    root.backend.enableBind(root.b.id)
            }

            IconTextButton {
                Layout.fillWidth: true
                text: KeybindsI18n.t("detail.delete")
                icon: "delete"
                type: TextButton.Tonal
                onClicked: if (root.b)
                    root.backend.deleteBind(root.b.id)
            }
        }
    }

    Process {
        id: clipProc
    }
}
