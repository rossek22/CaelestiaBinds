pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Effects
import M3Shapes
import Quickshell
import Caelestia.Config
import qs.components
import qs.components.containers
import qs.components.controls
import qs.components.effects
import qs.components.images
import qs.components.widgets
import qs.services

// Вкладка Author: ник, ава, сетап, ссылки. Аватар как CoverArt (без визуалайзера)
Flickable {
    id: root

    contentWidth: width
    contentHeight: col.implicitHeight + Tokens.padding.extraLarge
    clip: true
    boundsBehavior: Flickable.DragAndOvershootBounds
    flickDeceleration: 3500
    // Без VerticalFadeFlickable: слой маски на переключении вкладок дорогой

    readonly property string avatarPath: {
        const r = Quickshell.env("CAELESTIA_BINDS_ROOT");
        if (r && r.length)
            return `file://${r}/assets/rossek2.jpg`;
        return `file://${Quickshell.env("HOME")}/CaelestiaBinds/assets/rossek2.jpg`;
    }

    // Слои GPU всегда включены: страница держится в дереве, переключение слоёв даёт фриз
    readonly property bool layersOn: true

    ColumnLayout {
        id: col
        width: root.width
        spacing: Tokens.spacing.large

        // Карточка автора: клик → GitHub
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: authorRow.implicitHeight + Tokens.padding.extraLarge * 2

            StateLayer {
                anchors.fill: parent
                onClicked: Qt.openUrlExternally("https://github.com/rossek22")
            }

            RowLayout {
                id: authorRow
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.extraLarge

                // Блок из CoverArt.qml (медиа-плеер): cookie + FadeImage + Mask
                Item {
                    id: cover
                    Layout.preferredWidth: 96
                    Layout.preferredHeight: 96
                    implicitWidth: 96
                    implicitHeight: 96

                    property color fallbackColour: Colours.layer(Colours.palette.m3surfaceContainerHighest, 2)

                    // Лёгкое свечение, как у CoverArt
                    layer.enabled: root.layersOn
                    layer.effect: MultiEffect {
                        shadowEnabled: true
                        blurMax: 1
                        shadowColor: Colours.palette.m3outline
                        shadowOpacity: 0.3
                    }

                    Behavior on fallbackColour {
                        CAnim {}
                    }

                    Item {
                        id: shapeWrapper
                        anchors.fill: parent
                        layer.enabled: root.layersOn
                        opacity: cover.fallbackColour.a

                        MaterialShape {
                            id: shape
                            implicitSize: cover.width
                            shape: MaterialShape.Cookie9Sided
                            color: Qt.alpha(cover.fallbackColour, 1)

                            Behavior on color {
                                CAnim {}
                            }
                        }
                    }

                    MaterialIcon {
                        anchors.centerIn: parent
                        grade: 200
                        text: image.status === Image.Error ? "broken_image" : "person"
                        color: Colours.palette.m3onSurfaceVariant
                        fontStyle: Tokens.font.icon.size((parent.width * 0.35) || 1).build()
                        opacity: image.status === Image.Null || image.status === Image.Error ? 1 : 0
                    }

                    FadeImage {
                        id: image
                        anchors.fill: parent
                        source: root.avatarPath
                        preventInit: false
                        layer.enabled: root.layersOn
                        layer.effect: Mask {
                            maskSource: shapeWrapper
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.extraSmall

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Tokens.spacing.small

                        StyledText {
                            text: "Rossek2"
                            font: Tokens.font.headline.medium
                        }

                        Item {
                            Layout.fillWidth: true
                        }

                        MaterialIcon {
                            text: "open_in_new"
                            color: Colours.palette.m3onSurfaceVariant
                            fontStyle: Tokens.font.icon.small
                            opacity: 0.7
                        }
                    }

                    StyledText {
                        text: "github.com/rossek22"
                        color: Colours.palette.m3primary
                        font: Tokens.font.body.medium
                    }

                    StyledText {
                        Layout.fillWidth: true
                        text: KeybindsI18n.t("author.bio")
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.body.small
                        wrapMode: Text.Wrap
                    }
                }
            }
        }

        // Сетап: GPU / CPU / RAM / OS
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: setupInner.implicitHeight + Tokens.padding.extraLarge * 2

            ColumnLayout {
                id: setupInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.medium

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.medium

                    MaterialShape {
                        implicitSize: 48
                        shape: MaterialShape.SoftBurst
                        color: Colours.palette.m3tertiaryContainer

                        MaterialIcon {
                            anchors.centerIn: parent
                            text: "memory"
                            color: Colours.palette.m3onTertiaryContainer
                            fontStyle: Tokens.font.icon.medium
                            fill: 1
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0

                        StyledText {
                            text: KeybindsI18n.t("author.setup")
                            font: Tokens.font.title.small
                        }

                        StyledText {
                            text: KeybindsI18n.t("author.setup.sub")
                            color: Colours.palette.m3onSurfaceVariant
                            font: Tokens.font.label.small
                        }
                    }
                }

                // Сетка из 4 плиток
                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    rowSpacing: Tokens.spacing.small
                    columnSpacing: Tokens.spacing.small

                    // GPU
                    StyledRect {
                        Layout.fillWidth: true
                        radius: Tokens.rounding.large
                        color: Colours.tPalette.m3surfaceContainerHigh
                        implicitHeight: gpuCol.implicitHeight + Tokens.padding.large * 2

                        ColumnLayout {
                            id: gpuCol
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Tokens.padding.large
                            spacing: Tokens.spacing.extraSmall

                            RowLayout {
                                spacing: Tokens.spacing.small
                                MaterialIcon {
                                    text: "developer_board"
                                    color: Colours.palette.m3primary
                                    fontStyle: Tokens.font.icon.small
                                    fill: 1
                                }
                                StyledText {
                                    text: KeybindsI18n.t("author.gpu")
                                    color: Colours.palette.m3outline
                                    font: Tokens.font.label.small
                                }
                            }
                            StyledText {
                                Layout.fillWidth: true
                                text: "AMD Radeon RX 580"
                                font: Tokens.font.body.medium
                                wrapMode: Text.Wrap
                            }
                        }
                    }

                    // CPU
                    StyledRect {
                        Layout.fillWidth: true
                        radius: Tokens.rounding.large
                        color: Colours.tPalette.m3surfaceContainerHigh
                        implicitHeight: cpuCol.implicitHeight + Tokens.padding.large * 2

                        ColumnLayout {
                            id: cpuCol
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Tokens.padding.large
                            spacing: Tokens.spacing.extraSmall

                            RowLayout {
                                spacing: Tokens.spacing.small
                                MaterialIcon {
                                    text: "speed"
                                    color: Colours.palette.m3secondary
                                    fontStyle: Tokens.font.icon.small
                                    fill: 1
                                }
                                StyledText {
                                    text: KeybindsI18n.t("author.cpu")
                                    color: Colours.palette.m3outline
                                    font: Tokens.font.label.small
                                }
                            }
                            StyledText {
                                Layout.fillWidth: true
                                text: "Intel Xeon E3-1270 V2"
                                font: Tokens.font.body.medium
                                wrapMode: Text.Wrap
                            }
                        }
                    }

                    // RAM
                    StyledRect {
                        Layout.fillWidth: true
                        radius: Tokens.rounding.large
                        color: Colours.tPalette.m3surfaceContainerHigh
                        implicitHeight: ramCol.implicitHeight + Tokens.padding.large * 2

                        ColumnLayout {
                            id: ramCol
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Tokens.padding.large
                            spacing: Tokens.spacing.extraSmall

                            RowLayout {
                                spacing: Tokens.spacing.small
                                MaterialIcon {
                                    text: "database"
                                    color: Colours.palette.m3tertiary
                                    fontStyle: Tokens.font.icon.small
                                    fill: 1
                                }
                                StyledText {
                                    text: KeybindsI18n.t("author.ram")
                                    color: Colours.palette.m3outline
                                    font: Tokens.font.label.small
                                }
                            }
                            StyledText {
                                Layout.fillWidth: true
                                text: "16 GB"
                                font: Tokens.font.body.medium
                                wrapMode: Text.Wrap
                            }
                        }
                    }

                    // OS
                    StyledRect {
                        Layout.fillWidth: true
                        radius: Tokens.rounding.large
                        color: Colours.tPalette.m3surfaceContainerHigh
                        implicitHeight: osCol.implicitHeight + Tokens.padding.large * 2

                        ColumnLayout {
                            id: osCol
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Tokens.padding.large
                            spacing: Tokens.spacing.extraSmall

                            RowLayout {
                                spacing: Tokens.spacing.small
                                MaterialIcon {
                                    text: "terminal"
                                    color: Colours.palette.m3primary
                                    fontStyle: Tokens.font.icon.small
                                    fill: 1
                                }
                                StyledText {
                                    text: KeybindsI18n.t("author.system")
                                    color: Colours.palette.m3outline
                                    font: Tokens.font.label.small
                                }
                            }
                            StyledText {
                                Layout.fillWidth: true
                                text: "CachyOS + Caelestia Shell"
                                font: Tokens.font.body.medium
                                wrapMode: Text.Wrap
                            }
                        }
                    }
                }
            }
        }

        // Сайт
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: siteInner.implicitHeight + Tokens.padding.extraLarge * 2

            StateLayer {
                anchors.fill: parent
                onClicked: Qt.openUrlExternally("https://rossek2.ru")
            }

            ColumnLayout {
                id: siteInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.medium

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.medium

                    MaterialShape {
                        implicitSize: 52
                        shape: MaterialShape.ClamShell
                        color: Colours.palette.m3secondaryContainer

                        MaterialIcon {
                            anchors.centerIn: parent
                            text: "language"
                            color: Colours.palette.m3onSecondaryContainer
                            fontStyle: Tokens.font.icon.large
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0

                        StyledText {
                            text: KeybindsI18n.t("author.website")
                            font: Tokens.font.title.small
                        }

                        StyledText {
                            text: "rossek2.ru"
                            color: Colours.palette.m3primary
                            font: Tokens.font.body.large
                        }
                    }

                    MaterialIcon {
                        text: "open_in_new"
                        color: Colours.palette.m3onSurfaceVariant
                        fontStyle: Tokens.font.icon.medium
                    }
                }

                StyledText {
                    Layout.fillWidth: true
                    text: KeybindsI18n.t("author.website.hint")
                    color: Colours.palette.m3onSurfaceVariant
                    font: Tokens.font.body.small
                    wrapMode: Text.Wrap
                }

                StyledRect {
                    Layout.fillWidth: true
                    implicitHeight: urlRow.implicitHeight + Tokens.padding.medium
                    radius: Tokens.rounding.large
                    color: Colours.tPalette.m3surfaceContainerHigh

                    RowLayout {
                        id: urlRow
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: Tokens.padding.medium
                        anchors.rightMargin: Tokens.padding.medium
                        spacing: Tokens.spacing.small

                        MaterialIcon {
                            text: "link"
                            color: Colours.palette.m3primary
                            fontStyle: Tokens.font.icon.small
                        }

                        StyledText {
                            Layout.fillWidth: true
                            text: "https://rossek2.ru"
                            color: Colours.palette.m3primary
                            font: Tokens.font.label.large
                            elide: Text.ElideRight
                        }
                    }
                }
            }
        }

        // Telegram
        StyledRect {
            Layout.fillWidth: true
            radius: Tokens.rounding.extraLarge
            color: Colours.tPalette.m3surfaceContainer
            implicitHeight: tgInner.implicitHeight + Tokens.padding.extraLarge * 2

            StateLayer {
                anchors.fill: parent
                onClicked: Qt.openUrlExternally("https://t.me/rossekdev2")
            }

            ColumnLayout {
                id: tgInner
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: Tokens.padding.extraLarge
                spacing: Tokens.spacing.medium

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.medium

                    StyledRect {
                        implicitWidth: 52
                        implicitHeight: 52
                        radius: Tokens.rounding.full
                        color: Colours.palette.m3primaryContainer

                        MaterialIcon {
                            anchors.centerIn: parent
                            text: "campaign"
                            color: Colours.palette.m3onPrimaryContainer
                            fontStyle: Tokens.font.icon.large
                            fill: 1
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0

                        StyledText {
                            text: KeybindsI18n.t("author.tg")
                            font: Tokens.font.title.small
                        }

                        StyledText {
                            text: "@rossekdev2"
                            color: Colours.palette.m3primary
                            font: Tokens.font.body.large
                        }
                    }

                    StyledRect {
                        implicitHeight: joinLbl.implicitHeight + Tokens.padding.small * 2
                        implicitWidth: joinLbl.implicitWidth + Tokens.padding.large * 2
                        radius: Tokens.rounding.full
                        color: Colours.palette.m3primary

                        StyledText {
                            id: joinLbl
                            anchors.centerIn: parent
                            text: KeybindsI18n.t("author.open")
                            color: Colours.palette.m3onPrimary
                            font: Tokens.font.label.large
                        }
                    }
                }

                StyledRect {
                    Layout.fillWidth: true
                    radius: Tokens.rounding.large
                    color: Colours.tPalette.m3surfaceContainerHigh
                    implicitHeight: feedCol.implicitHeight + Tokens.padding.large * 2

                    ColumnLayout {
                        id: feedCol
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: Tokens.padding.large
                        spacing: Tokens.spacing.small

                        RowLayout {
                            spacing: Tokens.spacing.small
                            MaterialIcon {
                                text: "alternate_email"
                                color: Colours.palette.m3onSurfaceVariant
                                fontStyle: Tokens.font.icon.small
                            }
                            StyledText {
                                text: "rossekdev2"
                                font: Tokens.font.label.large
                            }
                            Item {
                                Layout.fillWidth: true
                            }
                            StyledText {
                                text: KeybindsI18n.t("author.channel")
                                color: Colours.palette.m3outline
                                font: Tokens.font.label.small
                            }
                        }

                        StyledText {
                            Layout.fillWidth: true
                            text: KeybindsI18n.t("author.tg.hint")
                            color: Colours.palette.m3onSurfaceVariant
                            font: Tokens.font.body.small
                            wrapMode: Text.Wrap
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
