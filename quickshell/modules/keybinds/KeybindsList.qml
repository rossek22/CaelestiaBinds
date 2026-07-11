pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.services

// ListView + reuse: большие списки биндов не лагают
ListView {
    id: root

    required property var backend
    signal bindActivated(var bind)

    clip: true
    spacing: Tokens.spacing.extraSmall / 2
    reuseItems: true
    cacheBuffer: 480
    boundsBehavior: Flickable.DragAndOvershootBounds
    boundsMovement: Flickable.FollowBoundsBehavior
    flickDeceleration: 3500
    maximumFlickVelocity: 4500

    topMargin: Tokens.padding.large
    bottomMargin: Tokens.padding.extraLarge

    model: backend.flatModel

    property string modelStamp: ""
    onModelChanged: {
        const stamp = `${backend.filter}|${backend.search}|${backend.flatModel.length}`;
        if (stamp !== modelStamp) {
            modelStamp = stamp;
            Qt.callLater(() => {
                if (root.count > 0)
                    root.positionViewAtBeginning();
            });
        }
    }

    delegate: Item {
        id: del
        required property var modelData
        required property int index

        width: ListView.view.width
        implicitHeight: modelData?.kind === "header" ? headerBlock.implicitHeight : rowBlock.implicitHeight
        height: implicitHeight

        // Заголовок секции
        Item {
            id: headerBlock
            anchors.left: parent.left
            anchors.right: parent.right
            visible: del.modelData?.kind === "header"
            implicitHeight: visible ? headerLabel.implicitHeight + Tokens.spacing.largeIncreased + Tokens.spacing.extraSmall : 0

            StyledText {
                id: headerLabel
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.leftMargin: Tokens.padding.small
                anchors.bottomMargin: Tokens.spacing.extraSmall
                text: (del.modelData?.title ?? "").toUpperCase()
                color: Colours.palette.m3onSurfaceVariant
                font: Tokens.font.label.medium
                elide: Text.ElideRight
            }
        }

        // Строка бинда
        StyledRect {
            id: rowBlock
            anchors.left: parent.left
            anchors.right: parent.right
            visible: del.modelData?.kind === "row"
            implicitHeight: visible ? rowLayout.implicitHeight + Tokens.padding.medium * 2 : 0

            readonly property var b: del.modelData?.bind ?? null
            readonly property bool first: del.modelData?.first ?? false
            readonly property bool last: del.modelData?.last ?? false
            readonly property bool only: del.modelData?.only ?? false

            color: Colours.tPalette.m3surfaceContainer
            topLeftRadius: only || first ? Tokens.rounding.extraLarge : Tokens.rounding.extraSmall
            topRightRadius: topLeftRadius
            bottomLeftRadius: only || last ? Tokens.rounding.extraLarge : Tokens.rounding.extraSmall
            bottomRightRadius: bottomLeftRadius

            StateLayer {
                anchors.fill: parent
                topLeftRadius: parent.topLeftRadius
                topRightRadius: parent.topRightRadius
                bottomLeftRadius: parent.bottomLeftRadius
                bottomRightRadius: parent.bottomRightRadius
                onClicked: {
                    if (rowBlock.b)
                        root.bindActivated(rowBlock.b);
                }
            }

            RowLayout {
                id: rowLayout
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: Tokens.padding.largeIncreased
                anchors.rightMargin: Tokens.padding.largeIncreased
                spacing: Tokens.spacing.medium

                StyledRect {
                    implicitHeight: keyLabel.implicitHeight + Tokens.padding.extraSmall
                    implicitWidth: keyLabel.implicitWidth + Tokens.padding.medium
                    radius: Tokens.rounding.small
                    color: (rowBlock.b?.source === "custom" || rowBlock.b?.source === "override") ? Colours.palette.m3primaryContainer : Colours.palette.m3secondaryContainer

                    StyledText {
                        id: keyLabel
                        anchors.centerIn: parent
                        text: rowBlock.b?.keys ?? ""
                        color: (rowBlock.b?.source === "custom" || rowBlock.b?.source === "override") ? Colours.palette.m3onPrimaryContainer : Colours.palette.m3onSecondaryContainer
                        font: Tokens.font.label.medium
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0
                    opacity: rowBlock.b?.enabled ? 1 : 0.5

                    StyledText {
                        Layout.fillWidth: true
                        text: rowBlock.b?.title ?? ""
                        font: Tokens.font.body.small
                        elide: Text.ElideRight
                    }

                    StyledText {
                        Layout.fillWidth: true
                        text: rowBlock.b?.detail ?? ""
                        color: Colours.palette.m3outline
                        font: Tokens.font.label.small
                        elide: Text.ElideRight
                    }
                }

                StyledRect {
                    visible: rowBlock.b?.hasVarCmd ?? false
                    implicitHeight: realLabel.implicitHeight + Tokens.padding.extraSmall
                    implicitWidth: Math.min(realLabel.implicitWidth + Tokens.padding.small * 2, 140)
                    radius: Tokens.rounding.full
                    color: Colours.layer(Colours.palette.m3primary, 2)

                    StyledText {
                        id: realLabel
                        anchors.centerIn: parent
                        width: parent.width - Tokens.padding.small * 2
                        horizontalAlignment: Text.AlignHCenter
                        text: {
                            const t = rowBlock.b?.technicalResolved || "";
                            return t.startsWith("exec ") ? t.slice(5) : t;
                        }
                        color: Colours.palette.m3primary
                        font: Tokens.font.label.small
                        elide: Text.ElideRight
                    }
                }

                StyledRect {
                    implicitHeight: srcLabel.implicitHeight + Tokens.padding.extraSmall
                    implicitWidth: srcLabel.implicitWidth + Tokens.padding.small * 2
                    radius: Tokens.rounding.full
                    color: Colours.layer(Colours.palette.m3onSurfaceVariant, 2)

                    StyledText {
                        id: srcLabel
                        anchors.centerIn: parent
                        text: (rowBlock.b?.source || "").toUpperCase()
                        color: Colours.palette.m3onSurfaceVariant
                        font: Tokens.font.label.small
                    }
                }

                MaterialIcon {
                    text: "chevron_right"
                    color: Colours.palette.m3onSurfaceVariant
                    fontStyle: Tokens.font.icon.small
                    opacity: 0.45
                }
            }
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        visible: root.backend.filteredCount === 0
        spacing: Tokens.spacing.small

        MaterialIcon {
            Layout.alignment: Qt.AlignHCenter
            text: "search_off"
            color: Colours.palette.m3onSurfaceVariant
            fontStyle: Tokens.font.icon.extraLarge
        }

        StyledText {
            Layout.alignment: Qt.AlignHCenter
            text: KeybindsI18n.t("list.empty")
            color: Colours.palette.m3onSurfaceVariant
            font: Tokens.font.body.large
        }
    }
}
