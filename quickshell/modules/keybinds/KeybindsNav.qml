pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.components.containers
import qs.components.controls
import qs.services

// Как NavPane / NavLocations / SearchBar в Nexus шелла
ColumnLayout {
    id: root

    required property var pages
    required property int currentIndex
    property string searchText
    // Первая инфо-вкладка (about/author): разделитель перед ней
    property int infoIndex: {
        for (let i = 0; i < pages.length; i++) {
            const k = pages[i].key;
            if (k === "about" || k === "author")
                return i;
        }
        return -1;
    }

    signal pageSelected(int idx)

    spacing: Tokens.spacing.large

    // Клон SearchBar
    StyledRect {
        id: searchShell
        Layout.fillWidth: true
        implicitHeight: searchLayout.implicitHeight + Tokens.padding.medium * 2
        radius: Tokens.rounding.full
        color: Colours.tPalette.m3surfaceContainerLowest
        border.color: Colours.palette.m3outlineVariant

        Behavior on border.color {
            CAnim {}
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.IBeamCursor
            onClicked: searchField.forceActiveFocus()
        }

        RowLayout {
            id: searchLayout
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.margins: Tokens.padding.large
            spacing: Tokens.spacing.small

            MaterialIcon {
                text: "search"
                color: Colours.palette.m3onSurfaceVariant
                fontStyle: Tokens.font.icon.medium
            }

            StyledTextField {
                id: searchField
                Layout.fillWidth: true
                Layout.fillHeight: true
                placeholderText: KeybindsI18n.t("nav.search")
                placeholderTextColor: Colours.palette.m3onSurfaceVariant
                color: Colours.palette.m3onSurfaceVariant
                font: Tokens.font.body.large
                text: root.searchText
                onTextChanged: root.searchText = text
            }

            IconButton {
                icon: "close"
                font: Tokens.font.icon.medium
                type: IconButton.Text
                padding: Tokens.padding.extraSmall
                isRound: true
                opacity: searchField.text.length > 0 ? 1 : 0
                onClicked: searchField.clear()
                Behavior on opacity {
                    Anim {
                        type: Anim.DefaultEffects
                    }
                }
            }
        }
    }

    // Обычный Flickable без слоя VerticalFadeFlickable
    Flickable {
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        contentHeight: navCol.implicitHeight + Tokens.padding.large * 2
        boundsBehavior: Flickable.StopAtBounds
        flickableDirection: Flickable.VerticalFlick

        ColumnLayout {
            id: navCol
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: Tokens.padding.large
            spacing: Tokens.spacing.extraSmall

            Repeater {
                id: list
                model: root.pages

                ColumnLayout {
                    id: wrap
                    required property var modelData
                    required property int index
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.extraSmall

                    // Разделитель перед блоком INFO
                    Item {
                        visible: wrap.index === root.infoIndex && root.infoIndex > 0
                        Layout.fillWidth: true
                        Layout.preferredHeight: Tokens.spacing.large + Tokens.padding.small
                        Layout.topMargin: Tokens.spacing.small

                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: Tokens.padding.small
                            anchors.rightMargin: Tokens.padding.small
                            height: 1
                            color: Colours.palette.m3outlineVariant
                            opacity: 0.55
                        }
                    }

                    StyledText {
                        visible: wrap.index === root.infoIndex && root.infoIndex > 0
                        Layout.leftMargin: Tokens.padding.small
                        Layout.bottomMargin: Tokens.spacing.extraSmall / 2
                        text: KeybindsI18n.t("nav.info")
                        color: Colours.palette.m3outline
                        font: Tokens.font.label.small
                    }

                    StyledRect {
                        id: item
                        Layout.fillWidth: true
                        implicitHeight: {
                            const h = layout.implicitHeight + layout.anchors.margins * 2;
                            return h % 2 === 0 ? h : h + 1;
                        }

                        readonly property bool isCurrent: wrap.index === root.currentIndex

                        color: isCurrent ? Colours.palette.m3secondaryContainer : Colours.layer(Colours.palette.m3surfaceContainerHigh, 2)
                        topLeftRadius: stateLayer.pressed ? Tokens.rounding.medium : isCurrent ? Tokens.rounding.extraLargeIncreased : Tokens.rounding.extraLarge
                        topRightRadius: topLeftRadius
                        bottomLeftRadius: topLeftRadius
                        bottomRightRadius: topLeftRadius

                        Behavior on topLeftRadius {
                            Anim {
                                type: Anim.DefaultEffects
                            }
                        }
                        Behavior on color {
                            CAnim {}
                        }

                        StateLayer {
                            id: stateLayer
                            anchors.fill: parent
                            topLeftRadius: parent.topLeftRadius
                            topRightRadius: parent.topRightRadius
                            bottomLeftRadius: parent.bottomLeftRadius
                            bottomRightRadius: parent.bottomRightRadius
                            onClicked: root.pageSelected(wrap.index)
                        }

                        RowLayout {
                            id: layout
                            anchors.fill: parent
                            anchors.margins: Tokens.padding.large
                            spacing: Tokens.spacing.medium

                            StyledRect {
                                Layout.fillHeight: true
                                Layout.topMargin: -1
                                Layout.bottomMargin: -1
                                implicitWidth: height
                                radius: Tokens.rounding.full
                                color: item.isCurrent ? Colours.palette.m3primary : Colours.palette.m3secondaryContainer
                                Behavior on color {
                                    CAnim {}
                                }

                                MaterialIcon {
                                    anchors.centerIn: parent
                                    anchors.verticalCenterOffset: 1
                                    text: wrap.modelData.icon
                                    color: item.isCurrent ? Colours.palette.m3onPrimary : Colours.palette.m3onSecondaryContainer
                                    fontStyle: Tokens.font.icon.builders.medium.weight(Font.Medium).build()
                                    grade: 25
                                    fill: 1
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 0

                                StyledText {
                                    Layout.fillWidth: true
                                    text: wrap.modelData.label
                                    font: Tokens.font.body.medium
                                    elide: Text.ElideRight
                                }

                                StyledText {
                                    Layout.fillWidth: true
                                    text: wrap.modelData.description
                                    color: Colours.palette.m3onSurfaceVariant
                                    font: Tokens.font.label.small
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Круглая кнопка языка слева снизу
    RowLayout {
        Layout.fillWidth: true
        Layout.topMargin: Tokens.spacing.small

        StyledRect {
            id: langBtn
            implicitWidth: 40
            implicitHeight: 40
            radius: Tokens.rounding.full
            color: Colours.layer(Colours.palette.m3surfaceContainerHigh, 2)
            border.color: Colours.palette.m3outlineVariant
            border.width: 1

            StateLayer {
                anchors.fill: parent
                radius: parent.radius
                onClicked: KeybindsI18n.toggle()
            }

            StyledText {
                anchors.centerIn: parent
                text: KeybindsI18n.isRu ? "RU" : "EN"
                font: Tokens.font.label.medium
                color: Colours.palette.m3onSurface
            }
        }

        Item {
            Layout.fillWidth: true
        }
    }
}
