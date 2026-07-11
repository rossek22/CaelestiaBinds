pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import M3Shapes
import Quickshell
import Caelestia.Config
import qs.components
import qs.components.containers
import qs.components.controls
import qs.services

// Вкладка About: про проект, стек, зачем создан
Flickable {
    id: root

    contentWidth: width
    contentHeight: col.implicitHeight + Tokens.padding.extraLarge
    clip: true
    boundsBehavior: Flickable.DragAndOvershootBounds
    flickDeceleration: 3500

    ColumnLayout {
        id: col
        width: root.width
        spacing: Tokens.spacing.large

        // Hero
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: hero.implicitHeight + Tokens.padding.extraLarge * 2

            ColumnLayout {
                id: hero
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.small

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.medium

                    MaterialShape {
                        implicitSize: 56
                        shape: MaterialShape.Cookie4Sided
                        color: Colours.palette.m3primaryContainer

                        MaterialIcon {
                            anchors.centerIn: parent
                            text: "keyboard"
                            color: Colours.palette.m3onPrimaryContainer
                            fontStyle: Tokens.font.icon.large
                            fill: 1
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0

                        StyledText {
                            text: KeybindsI18n.t("project.title")
                            font: Tokens.font.title.medium
                        }

                        StyledText {
                            Layout.fillWidth: true
                            text: KeybindsI18n.t("project.tagline")
                            color: Colours.palette.m3onSurfaceVariant
                            font: Tokens.font.body.small
                            wrapMode: Text.Wrap
                        }
                    }
                }

                RowLayout {
                    spacing: Tokens.spacing.small
                    StyledRect {
                        implicitHeight: ver.implicitHeight + Tokens.padding.extraSmall
                        implicitWidth: ver.implicitWidth + Tokens.padding.medium
                        radius: Tokens.rounding.full
                        color: Colours.palette.m3secondaryContainer
                        StyledText {
                            id: ver
                            anchors.centerIn: parent
                            text: "v0.1"
                            color: Colours.palette.m3onSecondaryContainer
                            font: Tokens.font.label.medium
                        }
                    }
                    StyledText {
                        text: KeybindsI18n.t("project.license")
                        color: Colours.palette.m3outline
                        font: Tokens.font.label.small
                    }
                }
            }
        }

        // Why
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: whyCol.implicitHeight + Tokens.padding.extraLarge * 2

            ColumnLayout {
                id: whyCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.small

                RowLayout {
                    spacing: Tokens.spacing.small
                    MaterialIcon {
                        text: "lightbulb"
                        color: Colours.palette.m3primary
                        fontStyle: Tokens.font.icon.medium
                        fill: 1
                    }
                    StyledText {
                        text: KeybindsI18n.t("project.why.title")
                        font: Tokens.font.title.small
                    }
                }

                StyledText {
                    Layout.fillWidth: true
                    text: KeybindsI18n.t("project.why.body")
                    color: Colours.palette.m3onSurfaceVariant
                    font: Tokens.font.body.medium
                    wrapMode: Text.Wrap
                }
            }
        }

        // Stack
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: stackCol.implicitHeight + Tokens.padding.extraLarge * 2

            ColumnLayout {
                id: stackCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.medium

                RowLayout {
                    spacing: Tokens.spacing.small
                    MaterialIcon {
                        text: "layers"
                        color: Colours.palette.m3secondary
                        fontStyle: Tokens.font.icon.medium
                        fill: 1
                    }
                    StyledText {
                        text: KeybindsI18n.t("project.stack.title")
                        font: Tokens.font.title.small
                    }
                }

                Repeater {
                    model: [
                        {
                            icon: "palette",
                            key: "project.stack.ui"
                        },
                        {
                            icon: "terminal",
                            key: "project.stack.data"
                        },
                        {
                            icon: "window",
                            key: "project.stack.wm"
                        },
                        {
                            icon: "folder_open",
                            key: "project.stack.cfg"
                        }
                    ]

                    StyledRect {
                        required property var modelData
                        Layout.fillWidth: true
                        radius: Tokens.rounding.large
                        color: Colours.tPalette.m3surfaceContainerHigh
                        implicitHeight: row.implicitHeight + Tokens.padding.medium * 2

                        RowLayout {
                            id: row
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Tokens.padding.medium
                            spacing: Tokens.spacing.medium

                            MaterialIcon {
                                text: modelData.icon
                                color: Colours.palette.m3primary
                                fontStyle: Tokens.font.icon.small
                            }

                            StyledText {
                                Layout.fillWidth: true
                                text: KeybindsI18n.t(modelData.key)
                                color: Colours.palette.m3onSurface
                                font: Tokens.font.body.small
                                wrapMode: Text.Wrap
                            }
                        }
                    }
                }
            }
        }

        // Features
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: featCol.implicitHeight + Tokens.padding.extraLarge * 2

            ColumnLayout {
                id: featCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.small

                RowLayout {
                    spacing: Tokens.spacing.small
                    MaterialIcon {
                        text: "checklist"
                        color: Colours.palette.m3tertiary
                        fontStyle: Tokens.font.icon.medium
                        fill: 1
                    }
                    StyledText {
                        text: KeybindsI18n.t("project.features.title")
                        font: Tokens.font.title.small
                    }
                }

                StyledText {
                    Layout.fillWidth: true
                    text: KeybindsI18n.t("project.features.body")
                    color: Colours.palette.m3onSurfaceVariant
                    font: Tokens.font.body.medium
                    wrapMode: Text.Wrap
                }
            }
        }

        // Contribute
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: contribCol.implicitHeight + Tokens.padding.extraLarge * 2

            StateLayer {
                anchors.fill: parent
                onClicked: Qt.openUrlExternally("https://github.com/rossek22/CaelestiaBinds")
            }

            ColumnLayout {
                id: contribCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.medium

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.small
                    MaterialIcon {
                        text: "handshake"
                        color: Colours.palette.m3primary
                        fontStyle: Tokens.font.icon.medium
                        fill: 1
                    }
                    StyledText {
                        Layout.fillWidth: true
                        text: KeybindsI18n.t("project.contrib.title")
                        font: Tokens.font.title.small
                    }
                    MaterialIcon {
                        text: "open_in_new"
                        color: Colours.palette.m3onSurfaceVariant
                        fontStyle: Tokens.font.icon.small
                    }
                }

                StyledText {
                    Layout.fillWidth: true
                    text: KeybindsI18n.t("project.contrib.body")
                    color: Colours.palette.m3onSurfaceVariant
                    font: Tokens.font.body.small
                    wrapMode: Text.Wrap
                }

                StyledRect {
                    Layout.fillWidth: true
                    implicitHeight: ghRow.implicitHeight + Tokens.padding.medium
                    radius: Tokens.rounding.large
                    color: Colours.palette.m3primaryContainer

                    RowLayout {
                        id: ghRow
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: Tokens.padding.medium
                        spacing: Tokens.spacing.small

                        MaterialIcon {
                            text: "code"
                            color: Colours.palette.m3onPrimaryContainer
                            fontStyle: Tokens.font.icon.small
                        }

                        StyledText {
                            Layout.fillWidth: true
                            text: KeybindsI18n.t("project.repo")
                            color: Colours.palette.m3onPrimaryContainer
                            font: Tokens.font.label.large
                        }

                        StyledText {
                            text: "github.com/rossek22/CaelestiaBinds"
                            color: Colours.palette.m3onPrimaryContainer
                            font: Tokens.font.label.small
                            opacity: 0.85
                            elide: Text.ElideMiddle
                            Layout.maximumWidth: 180
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: Tokens.padding.large
        }
    }
}
